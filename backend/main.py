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
    
    # --- Deep Diagnostics ---
    cookies_content = os.getenv("YT_COOKIES")
    if cookies_content:
        # Cleanup pasted quotes
        cookies_content = cookies_content.strip().strip('"').strip("'")
        
        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        
        try:
            with open(cookie_path, "w") as f:
                f.write(cookies_content)
            
            file_size = os.path.getsize(cookie_path)
            is_netscape = cookies_content.startswith("#")
            
            print(f"✅ Diagnostics: YT_COOKIES found in environment.", flush=True)
            print(f"📄 Diagnostics: Wrote to {cookie_path} ({file_size} bytes).", flush=True)
            print(f"🚩 Diagnostics: Netscape format check: {'PASS' if is_netscape else 'FAIL (Check export!)'}", flush=True)
        except Exception as e:
            print(f"❌ Diagnostics: Failed to write cookie file: {str(e)}", flush=True)
    else:
        print("ℹ️ Diagnostics: YT_COOKIES environment variable is EMPTY or NOT SET.", flush=True)
    # -----------------------

@app.get("/api/search", response_model=SearchResponse)
@limiter.limit("40/minute") # Increased limit for search
async def search(request: Request, q: str = Query(..., min_length=1)):
    """
    Search for tracks on YouTube.
    Caches results for 15 minutes.
    """
    results = await youtube_service.search_tracks(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
@limiter.limit("20/minute") # Increased limit for stream
async def stream(request: Request, video_id: str):
    """
    Get direct stream URL and metadata for a video.
    Caches results for 30 minutes.
    """
    info = await youtube_service.get_stream_info(video_id)
    if not info:
        # If extraction completely fails (including fallbacks)
        raise HTTPException(status_code=404, detail="Stream failed. YouTube is being extra difficult today!")
    return info

@app.get("/health")
async def health():
    return {"status": "healthy"}
