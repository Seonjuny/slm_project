# app/core/model_client.py
import logging
from typing import Optional

import requests

from app.core.config import LLM_BASE_URL, LLM_MODEL_ID

logger = logging.getLogger(__name__)

# Ollama 기준: /api/generate
GENERATE_URL = f"{LLM_BASE_URL}/api/generate"


def generate_llm(
    prompt: str,
    model: Optional[str] = None,
    stream: bool = False,
) -> str:
    """
    LLM 서버에 프롬프트를 보내서 응답을 받는 공통 함수.
    - model: None이면 기본값(LLM_MODEL_ID) 사용
    - stream: True면 스트리밍 모드(지금은 False 기준으로 사용 권장)
    Qwen2.5 14B Q4_K든, 다른 양자화 모델이든 여기선 신경 안 씀.
    """
    payload = {
        "model": model or LLM_MODEL_ID,
        "prompt": prompt,
        "stream": stream,
    }

    try:
        resp = requests.post(GENERATE_URL, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("LLM 서버 요청 실패: %s", e)
        raise RuntimeError(f"LLM 서버 호출 중 오류가 발생했습니다: {e}") from e

    data = resp.json()
    return (data.get("response") or "").strip()




