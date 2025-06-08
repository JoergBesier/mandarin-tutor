# tests/test_llm.py
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
import app.llm as llm
import json

def fake_llm(json_str):
    return RunnableLambda(lambda *_a, **_k: AIMessage(content=json_str))

def test_pinyin(monkeypatch):
    monkeypatch.setattr(llm, "_get_llm", lambda: fake_llm('{"pinyin":"hǎo"}'))
    assert llm.pinyin("好") == "hǎo"

def test_english(monkeypatch):
    monkeypatch.setattr(llm, "_get_llm", lambda: fake_llm('{"en":"good"}'))
    assert llm.english("好") == "good"

def test_word_list(monkeypatch):
    fake_json = {"words":[{"h":"好","p":"hǎo","en":"good"}]}
    monkeypatch.setattr(llm, "_get_llm",
                        lambda: fake_llm(json.dumps(fake_json)))
    assert llm.word_list("好")[0]["p"] == "hǎo"