# app/routers/cheap.py

from typing import Optional, List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.cheap_shop_data import filter_shops, sample_for_prompt
from app.core.model_client import generate_llm

router = APIRouter(prefix="/cheap", tags=["cheap-shop"])


class CheapChatRequest(BaseModel):
    question: str
    sido: Optional[str] = None
    sigungu: Optional[str] = None
    category: Optional[str] = None  # 업종(한식, 양식, 미용업 등)
    max_price: Optional[int] = None
    model: Optional[str] = None


class CheapChatResponse(BaseModel):
    row_count: int
    sample_size: int
    samples: List[Dict[str, Any]]
    answer: str


@router.post("/chat", response_model=CheapChatResponse)
def cheap_chat(req: CheapChatRequest):
    """
    착한 가격 가게 RAG 챗봇:
    - 시도/시군/업종/최대가격 조건으로 가게 필터링
    - 일부 샘플을 기반으로 추천/설명을 생성
    """
    df = filter_shops(
        sido=req.sido,
        sigungu=req.sigungu,
        category=req.category,
        max_price=req.max_price,
    )
    row_count = len(df)
    samples = sample_for_prompt(df, max_rows=15)

    prompt = (
        "당신은 한국의 착한 가격 가게(음식점, 미용실 등)를 추천해주는 어시스턴트입니다.\n"
        "당신은 한국어만 사용하는 AI입니다. \n"
        "모든 출력은 반드시 100% 한국어로만 작성해야 합니다. \n"
        "중국어·일본어·영어·기타 외국어 문구는 절대 포함하지 마십시오. \n"
        "답변 예시는 한국인이 자연스럽게 읽을 수 있는 문장으로 작성하세요. \n"
        "아래 샘플 데이터를 참고하여 사용자의 조건에 맞는 가게를 3~5곳 정도 추천해 주세요.\n"
        "- 샘플에 없는 가게 이름이나 가격을 지어내지 마세요.\n"
        "- 조건(지역, 최대 가격, 업종)을 최대한 만족하는 가게 위주로 소개하세요.\n"
        "- 각 가게에 대해 업소명, 대표 메뉴, 대략적인 가격, 위치를 간단히 설명하세요.\n"
        "- 조건에 맞는 가게가 매우 적거나 없으면, 그 사실을 솔직하게 말해 주세요.\n\n"
        f"[필터 조건]\n"
        f"- 시도: {req.sido or '제한 없음'}\n"
        f"- 시군: {req.sigungu or '제한 없음'}\n"
        f"- 업종: {req.category or '제한 없음'}\n"
        f"- 최대 가격: {req.max_price or '제한 없음'}\n\n"
        "[샘플 가게 데이터 (일부)]\n"
        f"{samples}\n\n"
        "[사용자 질문]\n"
        f"{req.question}\n\n"
        "[ASSISTANT]"
    )

    answer = generate_llm(prompt, model=req.model)

    return CheapChatResponse(
        row_count=row_count,
        sample_size=len(samples),
        samples=samples,
        answer=answer.strip(),
    )
