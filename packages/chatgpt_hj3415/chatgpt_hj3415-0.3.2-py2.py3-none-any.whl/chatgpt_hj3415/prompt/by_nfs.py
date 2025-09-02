import re
from typing import Literal

import pandas as pd
from db2_hj3415.nfs import c103, c104, c106

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, level='INFO')

def extract_code(ticker: str) -> str:
    """
    티커에서 종목코드를 추출합니다.
    형식이 잘못된 경우 ValueError를 발생시킵니다.
    예: 005930.KS → 005930
    """
    match = re.fullmatch(r'(\d{6})\.[A-Z]+', ticker)
    if not match:
        raise ValueError(f"잘못된 티커 형식입니다: {ticker}")
    return match.group(1)

def c1034_to_csv(df: pd.DataFrame, cleaning: bool = True, label_cols: list[str] = ['항목']) -> str:
    if not cleaning:
        # ✅ 행번호 제거
        return df.to_csv(index=False)

    dfc = df.copy()

    # 공백/문자 'NaN' 등을 결측으로 통일
    dfc.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
    dfc.replace({'NaN': pd.NA, 'nan': pd.NA, 'None': pd.NA}, inplace=True)

    # 라벨열/값열 분리
    label_cols = [c for c in label_cols if c in dfc.columns]
    value_cols = [c for c in dfc.columns if c not in label_cols]

    # 값열을 숫자로 캐스팅(결측 판정 정확도↑)
    if value_cols:
        dfc[value_cols] = dfc[value_cols].apply(pd.to_numeric, errors='coerce')

    # 값열이 전부 NaN인 행 제거
    if value_cols:
        dfc = dfc.dropna(how='all', subset=value_cols)

    # 값열 중 전체 NaN인 열 제거
    if value_cols:
        keep_values = [c for c in value_cols if not dfc[c].isna().all()]
    else:
        keep_values = []

    cols_out = [*label_cols, *keep_values] if label_cols else keep_values
    dfc = dfc.loc[:, cols_out]

    # ✅ 행번호(인덱스) 없이 CSV 출력
    return dfc.to_csv(index=False)

def c106_to_csv(df: pd.DataFrame, cleaning: bool = True) -> str:
    dfc = df.copy()

    # 1) '항목' 컬럼 제거(있으면)
    dfc.drop(columns=['항목'], errors='ignore', inplace=True)

    if not cleaning:
        # 인덱스 제거 + '항목2'는 남김
        # (원하는 경우 '항목2'를 맨 앞으로 재배치)
        if '항목2' in dfc.columns:
            cols = ['항목2'] + [c for c in dfc.columns if c != '항목2']
            dfc = dfc.loc[:, cols]
        return dfc.to_csv(index=False)

    # -----------------------------
    # cleaning=True일 때의 정리 로직
    # -----------------------------
    # 공백/문자 'NaN' 등을 결측으로 통일
    dfc.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
    dfc.replace({'NaN': pd.NA, 'nan': pd.NA, 'None': pd.NA}, inplace=True)

    # 라벨/값 컬럼 분리: '항목2'는 라벨로 간주하고 유지
    label_cols = [c for c in ['항목2'] if c in dfc.columns]
    value_cols = [c for c in dfc.columns if c not in label_cols]

    # 값 컬럼 숫자 변환(문자 숫자→실수, 변환 불가→NaN)
    if value_cols:
        dfc[value_cols] = dfc[value_cols].apply(pd.to_numeric, errors='coerce')

    # 값 컬럼이 전부 NaN인 "행" 제거(라벨 컬럼은 판단에서 제외)
    if value_cols:
        dfc = dfc.dropna(how='all', subset=value_cols)

    # 값 컬럼 중 전부 NaN인 "열" 제거(라벨 컬럼은 유지)
    keep_value_cols = [c for c in value_cols if not dfc[c].isna().all()]

    # '항목2'를 맨 앞으로 배치하여 출력
    out_cols = (label_cols + keep_value_cols) if label_cols else keep_value_cols
    dfc = dfc.loc[:, out_cols]

    # 인덱스 제거
    return dfc.to_csv(index=False)

async def c103_convert_df_to_csv(code: str, period: str)-> str:
    c103_data : dict[str, pd.DataFrame] = await c103.get_latest(code,'dataframe')
    if period == '분기':
        filtered = {k[:-1]+f"({period})": v for k, v in c103_data.items() if k.endswith('q')}
    elif period == '연간':
        filtered = {k[:-1] + f"({period})": v for k, v in c103_data.items() if k.endswith('y')}
    else:
        raise Exception("period error")
    c103_str = ""
    for page, df in filtered.items():
        c103_str += f"{page}\n{c1034_to_csv(df, True)}\n"
    return c103_str

async def c104_convert_df_to_csv(code: str, period: str)-> dict[str, str]:
    c104_data: dict[str, pd.DataFrame] = await c104.get_latest(code, 'dataframe')
    if period == '분기':
        filtered = {"투자지표(분기)": v for k, v in c104_data.items() if k.endswith('q')}
    elif period == '연간':
        filtered = {"투자지표(연간)": v for k, v in c104_data.items() if k.endswith('y')}
    else:
        raise Exception("period error")
    c104_str = ""
    for page, df in filtered.items():
        c104_str += f"{page}\n{c1034_to_csv(df, True)}\n"
    return c104_str

async def c106_convert_df_to_csv(code: str, period: str)-> dict[str, str]:
    c106_data: dict[str, pd.DataFrame] = await c106.get_latest(code, 'dataframe')
    if period == '분기':
        filtered = {"동종업종비교(분기)": v for k, v in c106_data.items() if k.endswith('q')}
    elif period == '연간':
        filtered = {"동종업종비교(연간)": v for k, v in c106_data.items() if k.endswith('y')}
    else:
        raise Exception("period error")
    c106_str = ""
    for page, df in filtered.items():
        c106_str += f"{page}\n{c106_to_csv(df, True)}\n"
    return c106_str

async def _build_chatgpt_prompt_from_df(ticker: str) -> str:
    code = extract_code(ticker)
    csv_103y = await c103_convert_df_to_csv(code, '연간')
    csv_103q = await c103_convert_df_to_csv(code, '분기')
    csv_104y = await c104_convert_df_to_csv(code, '연간')
    csv_104q = await c104_convert_df_to_csv(code, '분기')
    csv_106y = await c106_convert_df_to_csv(code, '연간')
    csv_106q = await c106_convert_df_to_csv(code, '분기')

    hint_ko = (
        f"다음의 데이터(재무분석, 투자지표, 업종 비교)와 "
        f"관련 정보(산업 동향, 경기 사이클 등)를 바탕으로, "
        f"기업의 현재와 미래 상황을 다음 항목에 따라 구체적으로 분석해 주세요:\n"
        f"1) 재무 상태  2) 수익성  3) 성장성  4) 투자 매력도  5) 산업 내 경쟁력\n"
    )

    hint_eng = (
        f"Based on the following data (financial statements, investment indicators, and industry comparison) "
        f"and other relevant information (such as industry trends and economic cycles), "
        f"please analyze the current and future status of the company in detail by the following aspects:\n"
        f"1) Financial health\n2) Profitability\n3) Growth potential\n4) Investment attractiveness\n5) Competitiveness in the industry\n"
    )

    prompt = (
        f"아래는 티커 '{ticker}'의 연간/분기 재무분석 데이터임.\n"
        f"분석 지시:\n- {hint_ko}\n\n"
        f"데이터 설명:\n단위:억원,%,배,천주 / 분기:순액기준\n\n"
        f"CSV 데이터 시작\n{csv_103y}{csv_104y}{csv_106y}{csv_103q}{csv_104q}{csv_106q}CSV 데이터 끝"
    )

    return prompt


async def get_prompt(ticker:str) -> list[dict]:
    content = await _build_chatgpt_prompt_from_df(ticker)

    return [
        {"role": "system",
         "content": "너의 역할은 CSV 재무분석 데이터를 분석하여, 과거/현재 요약뿐 아니라"
                    " 향후 회사에 대한 투자가치의 확률적 예측을 제공하는 한국어 사용 기술적 애널리스트다."
                    "주식 초보에게 설명하듯 이해하기 쉽게 정리해서 안내해줘."},
        {"role": "user",
         "content": content},
    ]