from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from .dependencies import get_sheet
import json

from app import llm

templates = Environment(loader=FileSystemLoader("app/templates"))
app = FastAPI(title="Mandarin Tutor API")

@app.get("/", response_class=HTMLResponse)
def index():
    return "<h3>Mandarin-Tutor API is running.</h3>"

@app.get("/sentence/{row_id}", response_class=HTMLResponse)
def sentence_page(row_id: int, sheet=Depends(get_sheet)):
    try:
        hanzi, mp3, pinyin, english, words_json = sheet.row_values(row_id)[:5]
    except Exception:
        raise HTTPException(404, f"Row {row_id} not found")

    html = templates.get_template("sentence.html").render(
        hanzi=hanzi,
        pinyin=pinyin,
        english=english,
        audio=mp3,
        words=json.loads(words_json or "[]")
    )
    return html

@app.get("/api/sentence/{row_id}")
def api_sentence(row_id: int, sheet=Depends(get_sheet)):
    vals = sheet.row_values(row_id)[:5]
    if len(vals) < 5:
        raise HTTPException(404, "row too short")
    keys = ["hanzi", "audio", "pinyin", "english", "wordList"]
    return dict(zip(keys, vals))



@app.post("/api/pinyin")
def api_pinyin(body: dict):
    return {"pinyin": llm.pinyin(body["text"])}