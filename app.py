from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()                         # <-- this MUST be here first

class VideoRequest(BaseModel):
    video_url: str

class SubtitleResponse(BaseModel):
    video_url: str
    subtitles_url: str
    transcript: str
    analysis: Optional[dict]

@app.post("/generate", response_model=SubtitleResponse)
async def generate_subtitles(request: VideoRequest):
    video_url = request.video_url
    # --- placeholder response ---
    subtitles_url = f"https://{uuid.uuid4()}.vtt"
    transcript = "Ez egy példa a lefordított szövegre magyarul."
    analysis = {
        "summary": "Ez egy rövid összefoglaló.",
        "topics": ["téma1", "téma2"],
        "sentiment": "Semleges"
    }
    return SubtitleResponse(
        video_url=video_url,
        subtitles_url=subtitles_url,
        transcript=transcript,
        analysis=analysis
    )

@app.get("/")
def ping():
    return {"status": "ok"}
