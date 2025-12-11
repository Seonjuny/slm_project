# app/core/config.py
import os
from pathlib import Path

# /app/app/core -> parents[2] = /app
BASE_DIR = Path(__file__).resolve().parents[2]

# ----- 데이터 경로 -----
DATA_DIR = BASE_DIR / "data"
LODGING_CSV_PATH = DATA_DIR / "lodging.csv"

# 착한 가격 가게 데이터 (시도, 시군, 업종, 메뉴/가격 ...)
CHEAP_SHOP_CSV_PATH = DATA_DIR / "cheap_shop.csv"  # 이 이름으로 CSV 저장하면 됨

# ----- LLM 서버 설정 (Qwen2.5 14B Q4_K 포함, 어떤 LLM이든 공통) -----
# 예: Ollama 기준  http://localhost:11434
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434")

# Modelfile: 
#   FROM qwen2.5:14b
#   PARAMETER quantization q4_K_M
# 이런 식으로 띄워놓고, 모델 ID는 ollama cli 기준으로 맞추면 됨.
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "qwen2.5:14b-q4_K_M")
