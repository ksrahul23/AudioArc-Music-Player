from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

# Absolute imports for modular structure
from models.schemas import SearchResponse, StreamInfo
from services.youtube_service import youtube_service

# Load environment variables (e.g., YT_COOKIES for cloud resilience)
load_dotenv()

# Setup Rate Limiting to prevent IP flagging
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pro Music Backend API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    On startup, verify and load YouTube cookies if provided.
    This is the definitive way to bypass cloud-IP blocking.
    """
    print("🚀 Senior Backend Refactor starting...", flush=True)
    cookies = os.getenv("YT_COOKIES")
    if cookies:
        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        # Cleanup potential formatting issues
        cookies = cookies.strip().strip('"').strip("'")
        with open(cookie_path, "w") as f:
            f.write(cookies)
        print(f"✅ YouTube session cookies loaded to {cookie_path}", flush=True)

@app.get("/")
async def root():
    return {"message": "Professional Music Backend is online"}

@app.get("/api/search", response_model=SearchResponse, response_model_by_alias=True)
@limiter.limit("30/minute")
async def search(request: Request, q: str = Query(..., min_length=1)):
    """
    Search YouTube for music tracks.
    Returns: title, artist/channel, video_id, duration, thumbnail.
    """
    results = await youtube_service.search_youtube(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
@limiter.limit("20/minute")
async def stream(request: Request, video_id: str):
    """
    Fetch direct stream URL for a video.
    Does NOT proxy audio; returns a direct YouTube CDN URL.
    """
    info = await youtube_service.get_stream_url(video_id)
    if not info:
        raise HTTPException(
            status_code=404, 
            detail="Stream could not be extracted. IP might be blocked or video is unavailable."
        )
    return info

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
