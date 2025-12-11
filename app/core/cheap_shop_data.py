# app/core/cheap_shop_data.py

from typing import Optional

import pandas as pd

from app.core.config import CHEAP_SHOP_CSV_PATH

_cheap_df: pd.DataFrame | None = None


def load_cheap_shop_data() -> pd.DataFrame:
    """
    착한 가격 가게 CSV 로딩 (lazy + 캐시).
    공공데이터 포털 형식이라 cp949 인코딩 사용.
    """
    global _cheap_df
    if _cheap_df is None:
        df = pd.read_csv(
            CHEAP_SHOP_CSV_PATH,
            encoding="cp949",
            low_memory=False,
        )
        _cheap_df = df
    return _cheap_df


def filter_shops(
    sido: Optional[str] = None,
    sigungu: Optional[str] = None,
    category: Optional[str] = None,  # 업종
    max_price: Optional[int] = None,
) -> pd.DataFrame:
    """
    시도/시군/업종/최대가격 조건으로 가게 필터링.
    컬럼 예시:
    - 시도, 시군, 업종, 업소명, 연락처, 주소,
      메뉴1, 가격1, 메뉴2, 가격2, 메뉴3, 가격3, 메뉴4, 가격4
    """
    df = load_cheap_shop_data()
    cond = pd.Series([True] * len(df), index=df.index)

    if sido:
        cond &= df["시도"] == sido
    if sigungu:
        cond &= df["시군"] == sigungu
    if category:
        cond &= df["업종"].astype(str).str.contains(category, na=False)

    if max_price is not None:
        price_cols = [c for c in df.columns if c.startswith("가격")]
        if price_cols:
            price_df = df[price_cols].apply(pd.to_numeric, errors="coerce")
            cond &= (price_df <= max_price).any(axis=1)

    return df[cond].copy()


def sample_for_prompt(df: pd.DataFrame, max_rows: int = 15) -> list[dict]:
    """
    프롬프트에 넣을 가게 샘플 (랜덤).
    """
    if df.empty:
        return []
    n = min(max_rows, len(df))
    sample = df.sample(n=n, random_state=None)
    # 너무 많은 컬럼은 줄이고 핵심만 남기고 싶으면 여기서 제한해도 됨.
    return sample.to_dict(orient="records")

