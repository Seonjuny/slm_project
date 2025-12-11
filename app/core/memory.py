# app/core/memory.py

from typing import Dict, List

# session_id -> List[{"role": "user"|"assistant"|"system", "content": "..."}]
_conversations: Dict[str, List[Dict[str, str]]] = {}


def get_history(session_id: str) -> List[Dict[str, str]]:
    return _conversations.get(session_id, [])


def set_history(session_id: str, history: List[Dict[str, str]]) -> None:
    _conversations[session_id] = history


def reset_session(session_id: str) -> None:
    if session_id in _conversations:
        del _conversations[session_id]


def reset_all() -> None:
    _conversations.clear()


def list_sessions() -> list[str]:
    return list(_conversations.keys())
