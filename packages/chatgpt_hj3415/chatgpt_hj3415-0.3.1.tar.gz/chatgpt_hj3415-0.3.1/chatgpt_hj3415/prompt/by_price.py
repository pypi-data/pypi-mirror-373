import pandas as pd
import yfinance as yf
import time
import io

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__)

def _fetch_recent_ndays_df(ticker: str, n_days: int) -> pd.DataFrame:
    """
    최근 n_days '거래일' 기준의 일봉 데이터를 반환합니다.
    - yfinance의 period는 달력일 기준이라 거래일 부족 가능 → 버퍼(×1.6) 적용 후 tail(n_days).
    """
    max_retries = 3
    delay_sec = 2

    # 거래일 부족 대비 버퍼: 예) 20거래일 ≈ 달력 32일 정도 → 넉넉히 1.6배
    period_days = max(int(n_days * 1.6), n_days)
    period_str = f"{period_days}d"

    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                tickers=ticker,
                period=period_str,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=True,
            )

            if df is not None and not df.empty:
                # 컬럼 정리 및 필요한 컬럼만 선택
                cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
                exist_cols = [c for c in cols if c in df.columns]
                df = df[exist_cols].copy()

                # 인덱스(DateTimeIndex)를 'Date' 컬럼으로
                df = df.reset_index()
                if "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"]):
                    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

                # 최근 n_days 거래일만
                df = df.tail(n_days).reset_index(drop=True)

                if not df.empty:
                    return df
                else:
                     mylogger.warning(
                        "[%d/%d] '%s' 최근 %d거래일 데이터가 비어 있음(기간: %s). %ds 후 재시도...",
                        attempt, max_retries, ticker, n_days, period_str, delay_sec
                    )
            else:
                mylogger.warning(
                    "[%d/%d] '%s' 다운로드 결과가 비어 있음(기간: %s). %ds 후 재시도...",
                    attempt, max_retries, ticker, period_str, delay_sec
                )

        except Exception as e:
            mylogger.exception(
                "[%d/%d] '%s' 다운로드 중 오류: %s. %ds 후 재시도...",
                attempt, max_retries, ticker, repr(e), delay_sec
            )

        time.sleep(delay_sec)

    mylogger.error("'%s' 주가 데이터를 최대 %d회 시도했지만 실패했습니다.", ticker, max_retries)
    return pd.DataFrame()


def _build_chatgpt_prompt_from_df(
    ticker: str,
    df: pd.DataFrame,
    n_days: int
) -> str:
    """
    DataFrame을 CSV 문자열로 직렬화하고, ChatGPT가 해석하기 쉬운 지시문을 포함한 프롬프트로 구성합니다.
    """
    if df.empty:
        return f"[데이터 없음] 티커 '{ticker}'의 최근 {n_days} 거래일 데이터를 가져오지 못했습니다."

    # CSV 직렬화 (너무 큰 수치가 들어오면 SI 단위가 더 낫지만, 그대로 두는 편이 후처리에 유리)
    buf = io.StringIO()
    # 컬럼 순서 정렬(있을 때만)
    preferred = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    cols = [c for c in preferred if c in df.columns]
    df[cols].to_csv(buf, index=False)
    csv_block = buf.getvalue().strip()

    # 분석 지시문(한국어)
    hint_ko = (
        "요청 항목"
        "1) 최근 추세(상승/하락/횡보)와 근거 "
        "2) 변동성 지표: 일중 고저폭 평균, 표준편차, ATR(14) 중 최소 2개 "
        "3) 거래량 변화: 최근 5일 평균 vs 직전 5일 평균, 증가율(%)"
        "4) 5일/20일 SMA 교차, 기울기(상승/하락),乖離율 "
        "5) 의미 있는 지지/저항(최근 스윙 고저/돌파·이탈 레벨 3~5개) "
        "6) 갭 발생 여부 및 이상치(가격·거래량) 탐지"
        ""
        "**미래 예측(필수)**"
        "- 향후 5~10거래일 시나리오 3가지(강세/중립/약세), 각 **확률(%)**과 **가격 범위**(또는 지수 포인트), **촉발 요인**을 제시"
        "- **베이스 시나리오 1개**를 선정하고 근거 지표를 나열"
        "- **무효화 조건**(예: 종가가 XX 아래/위로 2일 연속 마감 시)과 **재평가 트리거**를 명시"
        "- 리스크 요인 3개, 관찰 포인트 3개"
    )
    hint_eng = (
"""
Request Items
1) Recent trend (uptrend / downtrend / sideways) and supporting evidence
2) Volatility indicators: at least two among average daily high-low range, standard deviation, and ATR(14)
3) Volume change: compare the average volume of the last 5 trading days vs. the previous 5 days, including the percentage increase/decrease
4) 5-day / 20-day SMA crossover, slope direction (uptrend/downtrend), and deviation rate
5) Significant support and resistance levels (3 to 5 levels based on recent swing highs/lows or breakout/breakdown points)
6) Detection of price gaps and anomalies (in price and volume)

Future Prediction (Required)
- Provide three scenarios for the next 5 to 10 trading days (bullish / neutral / bearish), including probabilities (%), expected price ranges (or index points), and potential drivers.
- Select one base scenario and list the key technical indicators supporting it.
- Specify invalidation conditions (e.g., "if the closing price stays below/above XX for 2 consecutive days") and re-evaluation triggers.
- List 3 key risk factors and 3 observation points for the short term.
"""
    )

    prompt = (
        f"아래는 티커 '{ticker}'의 최근 {n_days} 거래일 일봉 데이터임.\n"
        f"분석 지시:\n- {hint_ko}\n\n"
        f"데이터 설명:\n- Date: YYYY-MM-DD\n- 가격: Open/High/Low/Close, 보정가: Adj Close, 거래량: Volume(주)\n\n"
        f"CSV 데이터 시작\n{csv_block}\nCSV 데이터 끝"
    )
    return prompt

# 권장 데이터 일수 120일
def get_prompt(ticker: str, n_days: int = 120) -> list[dict]:
    """
    외부에서 호출하는 메인 함수:
    - 최근 n_days 거래일의 일봉 데이터를 yfinance로 가져와
    - ChatGPT 분석에 바로 사용할 수 있는 '한국어 프롬프트 문자열'을 반환.
    """
    df = _fetch_recent_ndays_df(ticker=ticker, n_days=n_days)
    content = _build_chatgpt_prompt_from_df(ticker=ticker, df=df, n_days=n_days)
    return [
        {"role": "system",
         "content": "너의 역할은 CSV 일봉 데이터를 바탕으로 정량 지표를 계산하고, 과거/현재 요약뿐 아니라"
                    " 향후 5~10거래일에 대한 확률적 예측을 제공하는 한국어 사용 기술적 애널리스트다. "
                    "모든 예측은 교육적·정보 제공 목적의 확률적 시나리오로 제시해라(투자 조언 아님)."
                    "숫자 근거(지표 값, 기준일, 구간)를 반드시 명시하고, 불확실성/무효화 조건도 함께 적어라."},
        {"role": "user",
         "content": content},
    ]