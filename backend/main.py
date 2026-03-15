from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import shutil
from dotenv import load_dotenv

from models.schemas import SearchResponse, StreamInfo, ErrorResponse
from services.youtube_service import youtube_service

# Load environment variables
load_dotenv()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pro Music Player API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: Handle Cookies from Environment
@app.on_event("startup")
async def startup_event():
    print("🚀 Pro Music Backend starting...", flush=True)
    cookies_content = os.getenv("YT_COOKIES")
    if cookies_content:
        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        # Cleanup pasted quotes
        cookies_content = cookies_content.strip().strip('"').strip("'")
        with open(cookie_path, "w") as f:
            f.write(cookies_content)
        print(f"✅ Cookies loaded from environment: {cookie_path}", flush=True)

@app.get("/api/search", response_model=SearchResponse)
@limiter.limit("20/minute")
async def search(request: Request, q: str = Query(..., min_length=1)):
    """
    Search for tracks on YouTube.
    Caches results for 15 minutes.
    """
    results = await youtube_service.search_tracks(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
@limiter.limit("10/minute")
async def stream(request: Request, video_id: str):
    """
    Get direct stream URL and metadata for a video.
    Caches results for 30 minutes.
    """
    info = await youtube_service.get_stream_info(video_id)
    if not info:
        raise HTTPException(status_code=404, detail="Stream not found or blocked by YouTube")
    return info

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Example JSON Formats (for documentation)
"""
Search Response:
{
  "results": [
    {
      "videoId": "s4fYA_wkta8",
      "title": "Iss Tarah Aashiqui Ka",
      "artist": "Kumar Sanu",
      "thumbnail": "https://i.ytimg.com/vi/s4fYA_wkta8/hqdefault.jpg",
      "duration": 345
    }
  ]
}

Stream Response:
{
  "videoId": "s4fYA_wkta8",
  "title": "Iss Tarah Aashiqui Ka",
  "artist": "Kumar Sanu",
  "thumbnail": "https://i.ytimg.com/vi/s4fYA_wkta8/hqdefault.jpg",
  "duration": 345,
  "stream_url": "https://rr2---sn-cvh76nlz.googlevideo.com/videoplayback?..."
}
"""
