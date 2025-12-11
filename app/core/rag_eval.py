# app/core/rag_eval.py
from __future__ import annotations

import json
from typing import Any, Dict, List

from app.core.model_client import generate_llm


def build_context_preview(rows: List[dict], max_rows: int = 10) -> str:
    """
    LLM judge에 넘길 수 있도록 컨텍스트를 문자열로 요약.
    """
    preview = rows[:max_rows]
    return json.dumps(preview, ensure_ascii=False, indent=2)


def evaluate_rag_case(
    question: str,
    retrieved_rows: List[dict],
    answer: str,
    judge_model: str | None = None,
) -> Dict[str, Any]:
    """
    LLM을 judge로 사용해서
    - groundedness (근거 충실도)
    - relevance (질문 관련성)
    - hallucination (환각 여부)
    등을 0~1 스코어로 평가.

    반환 예:
    {
      "groundedness": 0.9,
      "relevance": 0.8,
      "hallucination": 0.1,
      "raw": "<judge 원문>"
    }
    """
    context_str = build_context_preview(retrieved_rows)

    prompt = f"""
당신은 다른 AI 모델의 답변을 평가하는 엄격한 심사위원입니다.

[질문]
{question}

[검색된 근거 데이터(일부 샘플, JSON 형태)]
{context_str}

[모델의 답변]
{answer}

다음 항목에 대해 0과 1 사이의 점수로 평가해 주세요.

1) groundedness: 답변이 위 근거 데이터에 기반해 있는 정도
2) relevance: 답변이 질문에 얼마나 직접적으로 관련이 있는지
3) hallucination: 근거에 없는 내용을 자신있게 말하는 정도 (높을수록 나쁨)

JSON 형식으로만 답변하세요. 예시는 다음과 같습니다:
{{
  "groundedness": 0.9,
  "relevance": 0.8,
  "hallucination": 0.1
}}
"""
    judge_raw = generate_llm(prompt, model=judge_model)
    try:
        scores = json.loads(judge_raw)
    except json.JSONDecodeError:
        scores = {}

    return {
        "groundedness": float(scores.get("groundedness", 0.0)),
        "relevance": float(scores.get("relevance", 0.0)),
        "hallucination": float(scores.get("hallucination", 0.0)),
        "raw": judge_raw,
    }
