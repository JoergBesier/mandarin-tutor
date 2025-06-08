# tests/test_llm_integration.py
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parent.parent / ".env"
loaded = load_dotenv(env_file, override=True)
print("LOADED_DOTENV?", loaded, "PATH", env_file)        # debug

import os, pytest
from app import llm

pytestmark = pytest.mark.integration  # custom marker

API_KEY = os.getenv("OPENAI_API_KEY")
print ("API_KEY", API_KEY)  # debug
# Uncomment the line below to use a specific API key for testing

def skip_if_no_key():
    if not API_KEY:
        pytest.skip("OPENAI_API_KEY not set – skipping integration test")


def test_pinyin_live():
    skip_if_no_key()
    out = llm.pinyin("好")
    # very loose assertion: contains hǎo or hao (tone-marks may vary)
    assert "hǎo" in out or "hao" in out.lower()


def test_english_live():
    skip_if_no_key()
    out = llm.english("好")
    assert "good" in out.lower() or "ok" in out.lower()# only integration tests
