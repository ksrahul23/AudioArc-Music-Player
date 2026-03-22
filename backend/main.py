from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from contextlib import asynccontextmanager
import os
import httpx
from dotenv import load_dotenv

# Absolute imports for modular structure
from models.schemas import SearchResponse, StreamInfo
from services.youtube_service import youtube_service

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init httpx client
    async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
        app.state.client = client
        print("AudioArc Bridge Server starting...", flush=True)
        yield
    # Shutdown: client is automatically closed by context manager

app = FastAPI(title="AudioArc Bridge Server", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # More permissive for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AudioArc Bridge Server is online"}

@app.get("/api/search", response_model=SearchResponse, response_model_by_alias=True)
async def search(request: Request, q: str = Query(..., min_length=1)):
    results = await youtube_service.search_youtube(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
async def stream(request: Request, video_id: str):
    info = await youtube_service.get_stream_url(video_id)
    if not info or not info.get("stream_url"):
        raise HTTPException(status_code=404, detail="Stream link not found")
    
    # We return the direct URL for best performance and seeking support
    # This bypasses the proxy entirely for the primary load
    return info

@app.get("/api/audio_proxy/{video_id}")
async def audio_proxy(request: Request, video_id: str):
    """Fallback proxy if direct playback fails."""
    info = await youtube_service.get_stream_url(video_id)
    if not info or not info.get("stream_url"):
         raise HTTPException(status_code=404, detail="Audio stream URL not found")
    
    stream_url = info["stream_url"]
    
    # For a local bridge, we can just redirect. 
    # This is much more stable than proxying megabytes of data through Python.
    return RedirectResponse(url=stream_url)

@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
