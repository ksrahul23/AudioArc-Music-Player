from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

# Import our modular components
from models.schemas import SearchResponse, StreamInfo, ErrorResponse
from services.youtube_service import youtube_service

# Load environment variables (like YT_COOKIES)
load_dotenv()

# Setup Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Professional Music API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Handle initialization and cookie setup for cloud environments.
    """
    print("🚀 Starting Professional Music Backend...", flush=True)
    cookies_content = os.getenv("YT_COOKIES")
    if cookies_content:
        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        # Cleanup quotes if any
        cookies_content = cookies_content.strip().strip('"').strip("'")
        with open(cookie_path, "w") as f:
            f.write(cookies_content)
        print(f"✅ YouTube cookies successfully loaded to {cookie_path}", flush=True)
    else:
        print("ℹ️ Warning: YT_COOKIES not found. IP blocking may occur on Render.", flush=True)

@app.get("/")
async def root():
    return {"message": "Professional Music API is Online", "status": "healthy"}

@app.get("/api/search", response_model=SearchResponse)
@limiter.limit("30/minute")
async def search(request: Request, q: str = Query(..., min_length=1)):
    """
    Search endpoint: Returns track metadata.
    Example output format:
    {
        "results": [
            {
                "title": "Song Title",
                "artist": "Artist Name",
                "video_id": "abc123",
                "duration": 240,
                "thumbnail": "url_to_image"
            }
        ]
    }
    """
    results = await youtube_service.search_tracks(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
@limiter.limit("15/minute")
async def stream(request: Request, video_id: str):
    """
    Stream endpoint: Returns direct audio URL.
    Does NOT proxy audio; returns a direct YouTube URL for the frontend to play.
    """
    info = await youtube_service.get_stream_info(video_id)
    if not info:
        raise HTTPException(
            status_code=404, 
            detail="Failed to extract stream. YouTube may have blocked the server IP."
        )
    return info

@app.get("/health")
async def health():
    return {"status": "ok"}
