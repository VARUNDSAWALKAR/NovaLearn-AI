"""UNLOX NovaLearn: LangChain/Gemini backend and safe local configuration.

No credentials are stored in this source file. All saved keys remain inside a
local .env (gitignored). Imports for model dependencies are intentionally lazy.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
AVAILABLE_MODELS = (
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
)
MAX_QUESTION_CHARS = 4000
MAX_HISTORY_MESSAGES = 10
TOPICS = {
    "Study Assistant": "Explain academic topics clearly, step by step, and include an example when helpful.",
    "Python Doubt Solver": "Help with Python concepts, debugging, and readable code examples. Explain the reasoning.",
    "Interview Preparation": "Coach the user through technical interviews with concise explanations, examples, and useful follow-up practice.",
}
PLACEHOLDER_KEYS = {
    "paste_your_gemini_api_key_here",
    "your_new_gemini_api_key",
    "your_actual_gemini_api_key",
    "your_api_key",
    "your_gemini_api_key",
    "replace_with_your_gemini_api_key",
}


class ChatbotConfigurationError(RuntimeError):
    """Required configuration is unavailable or invalid."""


class ChatbotResponseError(RuntimeError):
    """The remote model call failed or returned nothing usable."""


@dataclass(frozen=True)
class ChatbotSettings:
    api_key: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.3


def validate_question(question: str) -> str:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question before submitting.")
    cleaned = question.strip()
    if len(cleaned) > MAX_QUESTION_CHARS:
        raise ValueError(f"Please limit your question to {MAX_QUESTION_CHARS} characters.")
    return cleaned


def _clean_key(value: str | None) -> str:
    key = (value or "").strip().strip('"').strip("'").strip()
    if not key or key.lower() in PLACEHOLDER_KEYS:
        return ""
    if any(char in key for char in ("\n", "\r", "\x00", " ", "\t")):
        return ""
    return key


def load_settings() -> ChatbotSettings:
    """Load the local .env next to this script, regardless of working directory.

    A saved local key takes precedence over stale shell environment variables.
    Both GOOGLE_API_KEY and GEMINI_API_KEY are supported.
    """
    from dotenv import dotenv_values

    saved = dotenv_values(ENV_PATH) if ENV_PATH.is_file() else {}
    candidates = (
        saved.get("GOOGLE_API_KEY"),
        saved.get("GEMINI_API_KEY"),
        os.environ.get("GOOGLE_API_KEY"),
        os.environ.get("GEMINI_API_KEY"),
    )
    key = next((cleaned for candidate in candidates if (cleaned := _clean_key(candidate))), "")
    if not key:
        raise ChatbotConfigurationError(
            "No Gemini API key found. Add it in the sidebar's secure key setup, "
            "or set GOOGLE_API_KEY in the .env next to app.py."
        )
    model = str(saved.get("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL).strip()
    return ChatbotSettings(api_key=key, model=model or DEFAULT_MODEL)


def save_local_settings(api_key: str, model: str = DEFAULT_MODEL) -> Path:
    """Save secrets only on this device in .env, never to source or ZIP."""
    from dotenv import set_key

    cleaned = _clean_key(api_key)
    if not cleaned:
        raise ChatbotConfigurationError("Paste a Gemini API key; placeholders and spaces are not valid.")
    if model not in AVAILABLE_MODELS:
        raise ChatbotConfigurationError("Choose one of the supported model options.")
    ENV_PATH.touch(exist_ok=True)
    if os.name != "nt":
        ENV_PATH.chmod(0o600)
    set_key(str(ENV_PATH), "GOOGLE_API_KEY", cleaned, quote_mode="always")
    set_key(str(ENV_PATH), "GEMINI_MODEL", model, quote_mode="always")
    return ENV_PATH


def save_local_model(model: str) -> Path:
    """Update the model without requiring the user to re-enter their key."""
    from dotenv import set_key

    if model not in AVAILABLE_MODELS:
        raise ChatbotConfigurationError("Choose a supported model.")
    if not ENV_PATH.is_file():
        raise ChatbotConfigurationError("Save a key locally before changing the model.")
    set_key(str(ENV_PATH), "GEMINI_MODEL", model, quote_mode="always")
    return ENV_PATH


def build_chain(settings: ChatbotSettings, topic: str = "Study Assistant") -> Any:
    if topic not in TOPICS:
        raise ValueError("Unsupported topic selected.")
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_google_genai import ChatGoogleGenerativeAI

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an accurate, patient AI assistant. Your role: {topic}. "
            "{topic_instructions} If unsure, say so rather than inventing facts. "
            "Answer the latest user question using older conversation only as context.",
        ),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{question}"),
    ])
    model = ChatGoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.api_key,
        temperature=settings.temperature,
        max_retries=1,
        timeout=45,
    )
    return prompt | model | StrOutputParser()


def make_history(messages: list[dict[str, str]]) -> list[Any]:
    if not messages:
        return []
    from langchain_core.messages import AIMessage, HumanMessage

    converted: list[Any] = []
    for message in messages[-MAX_HISTORY_MESSAGES:]:
        content = message.get("content", "")
        if not isinstance(content, str) or not content:
            continue
        if message.get("role") == "user":
            converted.append(HumanMessage(content=content))
        elif message.get("role") == "assistant":
            converted.append(AIMessage(content=content))
    return converted


def _safe_remote_error(exc: Exception) -> str:
    """Classify remote errors without ever returning raw (possibly secret) logs."""
    message = str(exc).lower()
    if "access_token_type_unsupported" in message:
        return (
            "Gemini rejected this API credential type (401 ACCESS_TOKEN_TYPE_UNSUPPORTED). "
            "Some AQ.-prefix keys have this issue. Check the key in Google AI Studio "
            "and try a newly created Gemini Developer API key."
        )
    if any(code in message for code in ("401", "403", "permission denied", "unauthenticated", "api_key_invalid")):
        return "Gemini rejected the key or access is blocked (401/403). Check the key, project access and API restrictions."
    if any(code in message for code in ("429", "quota", "rate limit", "resource_exhausted")):
        return "Gemini quota or rate limit reached (429). Check usage and billing in Google AI Studio."
    if any(code in message for code in ("404", "model not found", "model_or_resource", "unsupported model", "no longer available")):
        return "This Gemini model is unavailable (404). Choose another model in the sidebar and retry."
    if any(code in message for code in ("503", "service unavailable", "unavailable", "overloaded")):
        return "Gemini is temporarily unavailable (503). Retry, or select another model."
    if any(code in message for code in ("timeout", "timed out", "connection", "dns")):
        return "Network or request timeout. Check your internet connection and retry."
    return "Gemini could not complete the request. Check your model settings and try again."


def answer_question(chain: Any, question: str, topic: str, messages: list[dict[str, str]] | None = None) -> str:
    cleaned = validate_question(question)
    if topic not in TOPICS:
        raise ValueError("Unsupported topic selected.")
    try:
        result = chain.invoke({
            "topic": topic,
            "topic_instructions": TOPICS[topic],
            "question": cleaned,
            "history": make_history(messages or []),
        })
    except Exception as exc:
        raise ChatbotResponseError(_safe_remote_error(exc)) from exc
    if not isinstance(result, str) or not result.strip():
        raise ChatbotResponseError("Gemini returned an empty response. Retry your question.")
    return result.strip()


def test_connection(settings: ChatbotSettings) -> bool:
    """Make a real, inexpensive Gemini request. Never mark 'connected' without one."""
    chain = build_chain(settings, topic="Study Assistant")
    answer_question(chain, "Reply with one short greeting.", "Study Assistant")
    return True
