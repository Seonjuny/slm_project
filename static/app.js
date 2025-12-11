// static/app.js

const API_BASE = "";

// ==============================
// 탭 / 선택 카드 연동
// ==============================
const botCards = document.querySelectorAll(".bot-card");
const botTabs = document.querySelectorAll(".bot-tab");
const panels = {
  lodging: document.getElementById("panel-lodging"),
  cheap: document.getElementById("panel-cheap"),
};

function activateBot(bot) {
  // 카드 활성화
  botCards.forEach((card) => {
    card.classList.toggle("active", card.dataset.bot === bot);
  });

  // 탭 활성화
  botTabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.bot === bot);
  });

  // 패널 활성화
  Object.entries(panels).forEach(([key, el]) => {
    el.classList.toggle("active", key === bot);
  });
}

// 카드 클릭
botCards.forEach((card) => {
  card.addEventListener("click", () => {
    activateBot(card.dataset.bot);
  });
});

// 탭 클릭
botTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    activateBot(tab.dataset.bot);
  });
});

// ==============================
// Lodging UI 요소
// ==============================
const lodgingChatWindow = document.getElementById("chat-window-lodging");
const lodgingInput = document.getElementById("input-lodging");
const lodgingSendBtn = document.getElementById("send-lodging");
const lodgingModelSelect = document.getElementById("lodging-model-select");

const lodgingActiveOnly = document.getElementById("lodging-active-only");
const lodgingOwnerType = document.getElementById("lodging-owner-type");
const lodgingMultiOnly = document.getElementById("lodging-multi-only");

// ==============================
// Cheap UI 요소
// ==============================
const cheapChatWindow = document.getElementById("chat-window-cheap");
const cheapInput = document.getElementById("input-cheap");
const cheapSendBtn = document.getElementById("send-cheap");
const cheapModelSelect = document.getElementById("cheap-model-select");

const cheapSido = document.getElementById("cheap-sido");
const cheapSigungu = document.getElementById("cheap-sigungu");
const cheapCategory = document.getElementById("cheap-category");
const cheapMaxPrice = document.getElementById("cheap-max-price");

// ==============================
// 로딩 상태 플래그
// ==============================
let lodgingLoading = false;
let cheapLoading = false;

// ==============================
// 공통 메시지 렌더링
// ==============================
function appendMessage(container, role, text, meta) {
  const msg = document.createElement("div");
  msg.className = `chat-message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";

  const roleLabel = document.createElement("div");
  roleLabel.className = "chat-role";
  roleLabel.textContent = role === "user" ? "나" : "AI";

  const textEl = document.createElement("div");
  textEl.className = "chat-text";
  textEl.textContent = text;

  bubble.appendChild(roleLabel);
  bubble.appendChild(textEl);

  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "chat-meta";
    metaEl.textContent = meta;
    bubble.appendChild(metaEl);
  }

  msg.appendChild(bubble);
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;

  return msg; // 필요하면 나중에 이 DOM을 잡아서 수정할 수도 있음
}

// ==============================
// Lodging 전송
// ==============================
async function sendLodging() {
  // 이미 요청 처리 중이면 무시 (중복 전송 방지)
  if (lodgingLoading) return;

  const raw = lodgingInput.value;
  const question = raw.trim();

  // 1) 비어 있으면 전송 X
  if (!question) return;

  // 2) 너무 짧은 입력 / 의미 없는 단어들은 아예 무시
  const bannedShort = ["줘", "라", "다줘", "나줘"];
  if (question.length <= 1 || bannedShort.includes(question)) {
    lodgingInput.value = ""; // 입력창만 비우고 끝
    return;
  }

  // 3) 여기부터는 "정상 질문"만 들어옴
  appendMessage(lodgingChatWindow, "user", question);
  lodgingInput.value = "";

  const activeOnly = lodgingActiveOnly.checked;
  const ownerType = lodgingOwnerType.value.trim() || null;
  const multiVal = lodgingMultiOnly.value;
  let multiOnly = null;
  if (multiVal === "true") multiOnly = true;
  else if (multiVal === "false") multiOnly = false;

  const model = lodgingModelSelect.value || null;

  // 로딩 시작 상태
  lodgingLoading = true;
  lodgingSendBtn.disabled = true;
  lodgingInput.disabled = true;

  // AI placeholder 한 개만 추가
  appendMessage(lodgingChatWindow, "assistant", "생각 중...", "로딩 중");

  try {
    const resp = await fetch(`${API_BASE}/lodging/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        active_only: activeOnly,
        owner_type: ownerType,
        multi_only: multiOnly,
        model,
      }),
    });

    const data = await resp.json();

    // 마지막 “생각 중…” 지우고 실제 답변 그리기
    lodgingChatWindow.removeChild(lodgingChatWindow.lastChild);

    const meta = `검색된 행: ${data.row_count}개 · 샘플: ${data.sample_size}개`;
    appendMessage(lodgingChatWindow, "assistant", data.answer, meta);
  } catch (err) {
    console.error(err);
    lodgingChatWindow.removeChild(lodgingChatWindow.lastChild);
    appendMessage(
      lodgingChatWindow,
      "assistant",
      "요청 중 오류가 발생했습니다.",
      "에러"
    );
  } finally {
    lodgingLoading = false;
    lodgingSendBtn.disabled = false;
    lodgingInput.disabled = false;
  }
}

// ==============================
// Cheap 전송
// ==============================
async function sendCheap() {
  // 이미 요청 처리 중이면 무시
  if (cheapLoading) return;

  const raw = cheapInput.value;
  const question = raw.trim();

  // 1) 비어 있으면 전송 X
  if (!question) return;

  // 2) 너무 짧은 입력 / 의미 없는 단어들은 무시
  const bannedShort = ["줘", "라", "다줘", "나줘"];
  if (question.length <= 1 || bannedShort.includes(question)) {
    cheapInput.value = "";
    return;
  }

  appendMessage(cheapChatWindow, "user", question);
  cheapInput.value = "";

  const sido = cheapSido.value.trim() || null;
  const sigungu = cheapSigungu.value.trim() || null;
  const category = cheapCategory.value.trim() || null;
  const maxPriceRaw = cheapMaxPrice.value.trim();
  const max_price = maxPriceRaw ? Number(maxPriceRaw) : null;

  const model = cheapModelSelect.value || null;

  // 로딩 시작
  cheapLoading = true;
  cheapSendBtn.disabled = true;
  cheapInput.disabled = true;

  // AI placeholder 한 개만 추가
  appendMessage(cheapChatWindow, "assistant", "생각 중...", "로딩 중");

  try {
    const resp = await fetch(`${API_BASE}/cheap/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        sido,
        sigungu,
        category,
        max_price,
        model,
      }),
    });

    const data = await resp.json();

    // 마지막 “생각 중…” 삭제 후 실제 응답 추가
    cheapChatWindow.removeChild(cheapChatWindow.lastChild);

    const meta = `필터 후 가게 수: ${data.row_count}개 · 샘플: ${data.sample_size}개`;
    appendMessage(cheapChatWindow, "assistant", data.answer, meta);
  } catch (err) {
    console.error(err);
    cheapChatWindow.removeChild(cheapChatWindow.lastChild);
    appendMessage(
      cheapChatWindow,
      "assistant",
      "요청 중 오류가 발생했습니다.",
      "에러"
    );
  } finally {
    cheapLoading = false;
    cheapSendBtn.disabled = false;
    cheapInput.disabled = false;
  }
}

// ==============================
// 이벤트 바인딩
// ==============================
lodgingSendBtn.addEventListener("click", sendLodging);
cheapSendBtn.addEventListener("click", sendCheap);

lodgingInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault(); // 줄바꿈 막고
    sendLodging();      // 바로 전송
  }
});

cheapInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendCheap();
  }
});
