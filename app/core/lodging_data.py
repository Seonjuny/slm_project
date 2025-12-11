# app/core/lodging_data.py

from typing import Dict, Any

import pandas as pd

from app.core.config import LODGING_CSV_PATH

_lodging_df: pd.DataFrame | None = None


def load_lodging_data() -> pd.DataFrame:
    """
    관광숙박업 공공데이터 CSV를 lazy 로딩 + 캐시.
    """
    global _lodging_df
    if _lodging_df is None:
        df = pd.read_csv(
            LODGING_CSV_PATH,
            encoding="cp949",
            low_memory=False,  # <= 이거 추가
        )
        _lodging_df = df
    return _lodging_df

def get_basic_stats() -> Dict[str, Any]:
    """
    실제 컬럼 기준 기초 통계:
    - 전체/영업/휴업/폐업 수
    - 평균 객실수, 평균 총층수
    - 관광숙박업상세명 / 지역구분명 / 주변환경명 분포
    """
    df = load_lodging_data()

    total_count = len(df)

    status_counts = (
        df["영업상태명"]
        .fillna("미기재")
        .value_counts()
        .to_dict()
    )

    # '영업', '영업/정상' 둘 다 영업으로 간주
    active_count = 0
    for k, v in status_counts.items():
        if "영업" in str(k) and "폐업" not in str(k) and "휴업" not in str(k):
            active_count += int(v)

    # 객실수 / 총층수 평균
    avg_rooms = None
    if "객실수" in df.columns:
        avg_rooms = df["객실수"].apply(pd.to_numeric, errors="coerce").mean()

    avg_floors = None
    if "총층수" in df.columns:
        avg_floors = df["총층수"].apply(pd.to_numeric, errors="coerce").mean()

    detail_counts = {}
    if "관광숙박업상세명" in df.columns:
        detail_counts = (
            df["관광숙박업상세명"]
            .fillna("미기재")
            .value_counts()
            .to_dict()
        )

    region_counts = {}
    if "지역구분명" in df.columns:
        region_counts = (
            df["지역구분명"]
            .fillna("미기재")
            .value_counts()
            .to_dict()
        )

    env_counts = {}
    if "주변환경명" in df.columns:
        env_counts = (
            df["주변환경명"]
            .fillna("미기재")
            .value_counts()
            .to_dict()
        )

    return {
        "total_count": int(total_count),
        "status_counts": status_counts,
        "active_count_estimated": int(active_count),
        "avg_rooms": float(avg_rooms) if avg_rooms is not None else None,
        "avg_total_floors": float(avg_floors) if avg_floors is not None else None,
        "detail_type_counts": detail_counts,
        "region_type_counts": region_counts,
        "environment_type_counts": env_counts,
    }


def filter_by_condition(
    active_only: bool = True,
    owner_type: str | None = None,   # 현재 데이터엔 없음 → 무시
    multi_only: bool | None = None,  # 현재 데이터엔 없음 → 무시
) -> pd.DataFrame:
    """
    조건에 맞는 숙박 업소만 필터링.

    현재 실제 컬럼 기준으로:
    - active_only: 영업 상태(영업/정상 등)만 남기기
    나머지 owner_type, multi_only는 현 데이터에 컬럼이 없으므로 무시.
    """
    df = load_lodging_data()

    cond = pd.Series(True, index=df.index)

    if active_only and "영업상태명" in df.columns:
        cond &= df["영업상태명"].astype(str).str.contains("영업", na=False) \
                & ~df["영업상태명"].astype(str).str.contains("폐업", na=False)

    # owner_type, multi_only는 현재 데이터에 해당 컬럼이 없으므로 일단 noop

    return df[cond].copy()


def sample_for_prompt(df: pd.DataFrame, max_rows: int = 20) -> list[dict]:
    """
    프롬프트에 넣을 샘플 레코드를 랜덤으로 추출.
    """
    if df.empty:
        return []
    n = min(max_rows, len(df))
    sample = df.sample(n=n, random_state=None)
    return sample.to_dict(orient="records")
