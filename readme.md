# readme

# 📘 SLM 로컬 RAG Demo

공공데이터 기반 숙박/착한가격 음식점을 로컬 LLM(Qwen2.5)으로 검색·추천해주는 RAG 기반 서비스

---

## 1. 📌 프로젝트 소개

**SLM(Local Small Language Model) Demo**는

두 개의 공공데이터셋을 기반으로 하는 로컬 LLM 기반 질의응답 서비스입니다.

### 지원 도메인

- **숙박 데이터 봇**
- **착한가격 음식점 데이터 봇**

LLM은 **Ollama + Qwen2.5 14B(양자화 모델)**을 사용하여

로컬 환경에서도 효율적으로 RAG 기반 답변을 생성할 수 있도록 구성되었습니다.

---

## 2. 📁 전체 구조

```
.
├─ app/
│  ├─ main.py                # FastAPI 엔트리포인트
│  ├─ routers/
│  │  ├─ lodging.py          # 숙박 도메인 API
│  │  └─ cheap.py            # 착한가격 음식점 API
│  └─ core/
│     ├─ lodging_data.py     # 숙박 CSV 로드 및 검색 로직
│     ├─ cheap_shop_data.py  # 음식점 CSV 로드 및 검색 로직
│     ├─ model_client.py     # LLM 서버 요청 유틸
│     ├─ memory.py           # 대화 히스토리 관리(옵션)
│     └─ rag_eval.py         # RAG 평가 Judge 로직
│
├─ static/
│  ├─ index.html             # UI 구조
│  ├─ styles.css             # 스타일
│  └─ app.js                 # 프론트엔드 로직
│
├─ eval_questions.jsonl      # 평가 질문 데이터셋(JSONL)
├─ run_eval.py               # RAG 평가 실행 스크립트
├─ Dockerfile                # FastAPI Docker 이미지 정의
├─ Modelfile                 # Ollama 모델 구성 파일(옵션)
├─ requirements.txt          # Python 패키지 목록
└─ (옵션) Kubernetes manifest(deployment/service)

```

구조는 **API → 데이터 → LLM → 프론트** 로 이어지는 명확한 4단 구성을 따른다.

---

## 3. 📊 주요 기능 요약

### 3.1. 숙박 데이터 봇

- 공공데이터 CSV(cp949) 로드
- 영업 여부, 소유 형태, 다중이용업 필터 지원
- 질문 기반 데이터 검색 및 통계 추출
- LLM이 자연어 요약/추천 생성

---

### 3.2. 착한가격 음식점 데이터 봇

- 지역(시/도, 시/군/구), 업종, 최대 가격 등 필터 지원
- 데이터 기반 추천/설명 생성
- LLM을 사용해 자연어 응답 생성

---

### 3.3. 프론트엔드 특징

- 단일 페이지 UI
- 두 개의 탭(숙박 / 음식점) 구성
- 각 패널에서 독립된 채팅 처리
- 짧은 입력(“줘”, “라” 등)은 자동 무시하여 사용자 버블 생성 방지
- LLM 응답 전에는 `"생각 중..."` 로딩 버블로 일관된 사용자 경험 제공

---

### 3.4. RAG 평가 기능

RAG 품질을 정량적으로 평가하기 위해 다음 요소를 LLM Judge가 평가한다:

- **Groundedness**
    
    → 답변이 검색된 실제 데이터에 근거하는 정도
    
- **Relevance**
    
    → 질문과 답변 사이의 관련성
    
- **Hallucination**
    
    → 없는 정보를 생성하는 정도
    

평가는 `run_eval.py` 를 통해 실행되며

여러 질문을 한 번에 처리할 수 있도록 JSONL 형식을 지원한다.

---

## 4. ⚙️ 설치 & 실행

### 4.1. Python 의존성 설치

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

```

---

### 4.2. LLM 준비(Ollama)

1. Ollama 설치
2. 모델 다운로드

```bash
ollama pull qwen2.5:14b
ollama pull qwen2.5:14b-q4_K_M     # 양자화된 모델(예시)

```

1. 모델 확인

```bash
ollama list

```

1. `.env` 설정

```
LLM_BASE_URL=http://host.docker.internal:11434
LLM_MODEL_ID=qwen2.5:14b-q4_K_M

```

---

### 4.3. FastAPI 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

접속:

👉 http://localhost:8000

---

### 4.4. Docker 실행

```bash
docker build -t slm .
docker run --name slm -p 8000:8000 --env-file .env slm

```

---

## 5. 🔍 데이터 흐름 요약

### 요청 흐름

```
사용자 질문
   ↓
프론트(app.js)
   ↓
FastAPI 라우터(lodging/cheap)
   ↓
데이터 필터링(lodging_data / cheap_data)
   ↓
프롬프트 생성
   ↓
LLM 호출(model_client)
   ↓
자연어 응답 생성
   ↓
프론트로 응답 반환

```

### 프론트 처리 흐름

```
Enter 키 또는 버튼 클릭
   ↓
짧은 입력 필터링 (무의미 입력 제거)
   ↓
"생각 중..." 표시
   ↓
서버 응답 도착
   ↓
로딩 메시지 삭제
   ↓
실제 답변 렌더링

```

---

## 6. 🧪 RAG 평가 프로세스

### 6.1. 평가 목표

- RAG 응답이 데이터에 근거했는가?
- 질문과 관련된 답을 했는가?
- 환각이 얼마나 발생했는가?

---

### 6.2. 평가 데이터 형식(JSONL)

`eval_questions.jsonl` 예:

```json
{"id":"lodging_001","bot":"lodging","question":"서울 숙박업소 몇 개야?","intent":"통계"}
{"id":"cheap_001","bot":"cheap","question":"종로구 1만원 이하 식당 추천해줘","intent":"추천"}

```

---

### 6.3. 평가 실행

```bash
python run_eval.py

```

출력 예:

```
=== LODGING ===
groundedness: 0.82
relevance: 0.90
hallucination: 0.10

=== CHEAP ===
groundedness: 0.75
relevance: 0.88
hallucination: 0.15

```

---

## 7. 🚀 확장 가능성

- 질문 유형별(추천/설명/통계) 평가 세분화 가능
- 여러 LLM 모델 비교 평가
- FastAPI 엔드포인트 확장
- ESG, 교육 등 다른 도메인 데이터 적용 가능
- CI/CD(Jenkins) + Kubernetes 배포 자동화 가능

---

## 8. 📌 결론

이 프로젝트는 다음을 보여주는 **종합적인 로컬 RAG 데모**입니다:

- 공공데이터 필터링 및 전처리
- 로컬 LLM(Qwen) 기반 자연어 응답 생성
- 완성도 있는 웹 기반 QA 인터페이스
- RAG 성능을 직접 평가하는 Judge 시스템
- Docker/K8s 기반 배포 확장성

구조적으로 명확한 계층을 갖추고 있어

추후 기능 추가, 모델 교체, 데이터셋 확장이 매우 용이합니다.