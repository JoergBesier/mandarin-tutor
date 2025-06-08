"""
app/llm.py  •  LangChain-based helpers for Mandarin-Tutor backend
---------------------------------------------------------------

Environment variables expected (e.g. in .env):

OPENAI_API_KEY       = sk-...
OPENAI_CHAT_MODEL    = gpt-4o-mini
OPENAI_TEMP          = 0.2
LANGCHAIN_TRACING_V2 = true                 # if you enable LangSmith
LANGCHAIN_API_KEY    = ls-...
"""

from __future__ import annotations
import json, os
from functools import lru_cache
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.tracers import LangChainTracer   # enable if using LS

# ── config ───────────────────────────────────────────────────────────────
_MODEL     = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
_TEMP      = float(os.getenv("OPENAI_TEMP", 0.2))

# ── lazy OpenAI client ───────────────────────────────────────────────────
@lru_cache
def _get_llm() -> ChatOpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = ChatOpenAI(model=_MODEL, temperature=_TEMP, api_key=key)

    # Optional LangSmith tracing
    # if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
    #     tracer = LangChainTracer(project_name="mandarin-tutor")
    #     client.bind(tracer=tracer)

    return client


# ── prompts ──────────────────────────────────────────────────────────────
_PINYIN_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a professional Chinese linguist. "
     "Return ONLY valid JSON: {{ \"pinyin\": \"<string>\" }}. "
     "Formatting rules: "
     "1) Use tone MARKS, not numbers; "
     "2) Modern dictionary word boundaries; "
     "3) ONE space between words; "
     "4) Keep Chinese punctuation as separate tokens with a space AFTER the mark; "
     "5) No extra keys or commentary."
    ),
    ("user", "{inp}")
])

_EN_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Return ONLY valid JSON: {{ \"en\": \"<string>\" }}. "
     "Provide a concise, natural English translation."
    ),
    ("user", "{inp}")
])

_WORDLIST_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Return ONLY valid JSON: "
     "{{ \"words\": [ {{\"h\":\"<hanzi>\",\"p\":\"<pinyin>\",\"en\":\"<eng>\"}}, … ] }}. "
     "Split the user's sentence into dictionary words; "
     "treat Chinese punctuation as separate tokens with \"type\":\"punct\"."
    ),
    ("user", "{inp}")
])


# ── helpers ──────────────────────────────────────────────────────────────
def _invoke(prompt: ChatPromptTemplate, text: str) -> Any:
    llm = _get_llm()
    chain = prompt | llm | (lambda m: m.content)
    return json.loads(chain.invoke({"inp": text}))


def pinyin(text: str) -> str:
    """Return tone-marked pinyin with spaces."""
    return _invoke(_PINYIN_PROMPT, text).get("pinyin", "")


def english(text: str) -> str:
    """Return concise English translation."""
    return _invoke(_EN_PROMPT, text).get("en", "")


def word_list(text: str) -> List[Dict]:
    """
    Return list of word dicts:
      [{"h": "电脑", "p": "diànnǎo", "en": "computer"}, …]
    """
    return _invoke(_WORDLIST_PROMPT, text).get("words", [])


def full_package(text: str) -> Dict:
    """Convenience: all fields in one call."""
    return {
        "hanzi": text,
        "pinyin": pinyin(text),
        "english": english(text),
        "wordList": word_list(text),
    }


__all__ = ["pinyin", "english", "word_list", "full_package"]