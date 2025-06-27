# app.py   ── complete working backend (Step A: real transcription, no translation yet)

import os
import uuid
import tempfile
import subprocess
import httpx
import yt_dlp



def translate_hu(text: str) -> str:
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {"key": os.getenv("GOOGLE_API_KEY")}
    payload = {"q": text, "target": "hu", "format": "text"}
    r = httpx.post(url, params=params, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["data"]["translations"][0]["translatedText"]

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

import openai           # ← make sure “openai” and “yt-dlp” are in requirements.txt

# ─────────────────────────────
# FastAPI instance
# ─────────────────────────────
app = FastAPI()

# ─────────────────────────────
# Pydantic models
# ─────────────────────────────
class VideoRequest(BaseModel):
    video_url: str

class SubtitleResponse(BaseModel):
    video_url: str
    subtitles_url: str
    transcript: str
    analysis: Optional[dict]

# ─────────────────────────────
# Helper functions
# ─────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")   # Variable set in Railway

def download_audio(url: str) -> str:
    """
    Download the best audio track with yt-dlp’s Python API.
    Saves as .m4a (no FFmpeg needed) and returns the local path.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".m4a", delete=False)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp.name,              # exact filename
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return tmp.name

def transcribe(path: str) -> str:
    """Transcribe audio file using OpenAI Whisper."""
    with open(path, "rb") as f:
        resp = openai.Audio.transcribe("whisper-1", f)
    return resp["text"]

# ─────────────────────────────
# Routes
# ─────────────────────────────
@app.post("/generate", response_model=SubtitleResponse)
async def generate_subtitles(request: VideoRequest):
    video_url = request.video_url

    # 1) download audio
    audio_path = download_audio(video_url)

    # 2) transcribe to text (source language)
    src_text = transcribe(audio_path)

    # 3) placeholders for next steps (translation + real VTT)
    subtitles_url = f"https://{uuid.uuid4()}.vtt"   # fake for now
    transcript    = src_text                       # real transcript, untranslated
    analysis      = {"summary": "coming soon"}

    return SubtitleResponse(
        video_url=video_url,
        subtitles_url=subtitles_url,
        transcript=transcript,
        analysis=analysis
    )

@app.get("/quicktest")
def quick_test(video_url: str):
    hu_text = translate_hu(transcribe(download_audio(video_url)))
    return {"transcript": hu_text[:400] + " …"}
