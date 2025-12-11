# app/routers/lodging.py

from typing import Optional, List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.lodging_data import (
    get_basic_stats,
    filter_by_condition,
    sample_for_prompt,
)
from app.core.model_client import generate_llm

router = APIRouter(prefix="/lodging", tags=["lodging"])


class LodgingChatRequest(BaseModel):
    question: str
    active_only: bool = True
    owner_type: Optional[str] = None
    multi_only: Optional[bool] = None
    model: Optional[str] = None


class LodgingChatResponse(BaseModel):
    row_count: int
    sample_size: int
    samples: List[Dict[str, Any]]
    stats: Dict[str, Any]
    answer: str


@router.post("/chat", response_model=LodgingChatResponse)
def lodging_chat(req: LodgingChatRequest):
    """
    숙박 데이터 기반 RAG 챗봇:
    - 조건으로 필터링한 뒤
    - 일부 샘플 + 전체 통계를 LLM에 전달해서
    - 자연어 분석/설명을 생성
    """
    df = filter_by_condition(
        active_only=req.active_only,
        owner_type=req.owner_type,
        multi_only=req.multi_only,
    )
    row_count = len(df)
    samples = sample_for_prompt(df, max_rows=20)
    stats = get_basic_stats()

    prompt = (
        "당신은 한국의 숙박업 공공데이터를 해석해주는 데이터 분석 어시스턴트입니다.\n"
        "당신은 한국어만 사용하는 AI입니다. \n"
        "모든 출력은 반드시 100% 한국어로만 작성해야 합니다. \n"
        "중국어·일본어·영어·기타 외국어 문구는 절대 포함하지 마십시오. \n"
        "답변 예시는 한국인이 자연스럽게 읽을 수 있는 문장으로 작성하세요. \n"
        "아래의 통계 정보와 샘플 데이터를 참고하여 사용자의 질문에 답변하세요.\n"
        "- 표에 없는 내용은 아는 척하지 말고, '데이터 상으로는 확실히 말하기 어렵다'고 말하세요.\n"
        "- 추정이 필요한 경우 '추정컨대', '샘플 기준으로는'과 같이 불확실성을 명시하세요.\n"
        "- 숫자나 비율을 언급할 때는 너무 세밀하지 않게, 이해하기 쉬운 수준으로 설명하세요.\n\n"
        "[전체 통계 정보]\n"
        f"{stats}\n\n"
        f"[필터 조건에 맞는 전체 행 수] {row_count}건\n\n"
        "[샘플 데이터 (일부)]\n"
        f"{samples}\n\n"
        "[사용자 질문]\n"
        f"{req.question}\n\n"
        "[ASSISTANT]"
    )

    answer = generate_llm(prompt, model=req.model)

    return LodgingChatResponse(
        row_count=row_count,
        sample_size=len(samples),
        samples=samples,
        stats=stats,
        answer=answer.strip(),
    )
