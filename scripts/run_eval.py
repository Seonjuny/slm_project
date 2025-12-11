# scripts/run_eval.py

"""
간단한 RAG 평가 러너 예시.

- 숙박 / 착한 가격 가게 각각에 대해
  "질문 -> 검색된 rows -> 모델 답변"을 만든 뒤
  app.core.rag_eval.evaluate_rag_case 로
  groundedness / relevance / hallucination 을 점수화.

실제 프로젝트에서는
- 별도 JSON/CSV 평가셋을 만들고
- 그걸 loop 돌면서 aggregate metric 뽑는 구조로 확장하면 됨.
"""

from pprint import pprint

from app.core.lodging_data import filter_by_condition, sample_for_prompt
from app.core.cheap_shop_data import filter_shops, sample_for_prompt as cheap_sample
from app.core.model_client import generate_llm
from app.core.rag_eval import evaluate_rag_case


def eval_lodging_case():
    question = "영업/정상 업소가 휴업/폐업 업소보다 얼마나 더 많은지 알려줘."
    df = filter_by_condition(active_only=False)
    rows = sample_for_prompt(df, max_rows=30)

    prompt = (
        "당신은 한국의 숙박업 공공데이터를 해석해주는 데이터 분석 어시스턴트입니다.\n"
        "아래 샘플 데이터를 참고하여 질문에 답하세요.\n\n"
        f"[샘플 데이터]\n{rows}\n\n"
        f"[질문]\n{question}\n\n"
        "[ASSISTANT]"
    )

    answer = generate_llm(prompt)
    print("\n[LODING ANSWER]")
    print(answer)

    scores = evaluate_rag_case(
        question=question,
        retrieved_rows=rows,
        answer=answer,
    )
    print("\n[LODING EVAL SCORES]")
    pprint(scores)


def eval_cheap_case():
    question = "서울 종로구에서 5천원 이하로 식사할 수 있는 가게가 대략 어느 정도 있는지 알려줘."
    df = filter_shops(sido="서울특별시", sigungu="종로구", max_price=5000)
    rows = cheap_sample(df, max_rows=30)

    prompt = (
        "당신은 한국의 착한 가격 가게 데이터를 기반으로 합리적인 가격대의 가게를 알려주는 어시스턴트입니다.\n"
        "아래 샘플 데이터를 참고하여 질문에 답하세요.\n\n"
        f"[샘플 데이터]\n{rows}\n\n"
        f"[질문]\n{question}\n\n"
        "[ASSISTANT]"
    )

    answer = generate_llm(prompt)
    print("\n[CHEAP SHOP ANSWER]")
    print(answer)

    scores = evaluate_rag_case(
        question=question,
        retrieved_rows=rows,
        answer=answer,
    )
    print("\n[CHEAP SHOP EVAL SCORES]")
    pprint(scores)


if __name__ == "__main__":
    print("==== RAG EVAL: LODGING ====")
    eval_lodging_case()
    print("\n\n==== RAG EVAL: CHEAP SHOP ====")
    eval_cheap_case()
