from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import httpx
from dotenv import load_dotenv

# Absolute imports for modular structure
from models.schemas import SearchResponse, StreamInfo
from services.youtube_service import youtube_service

# Load environment variables
load_dotenv()

# Setup Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AudioArc Bridge Server")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
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
    On startup, ensure a writable cookies.txt exists by reading from env vars or secret files.
    """
    print("🚀 AudioArc Bridge Server starting...", flush=True)
    
    cookie_content = None
    
    # 1. Try Environment Variable first
    env_cookies = os.getenv("YT_COOKIES")
    if env_cookies:
        print("📡 Found YT_COOKIES environment variable", flush=True)
        cookie_content = env_cookies
    
    # 2. Try Secret File locations if env var not found
    if not cookie_content:
        secret_paths = ["/etc/secrets/YT_COOKIES", "/etc/secrets/cookies.txt"]
        for p in secret_paths:
            if os.path.exists(p):
                print(f"✅ Found secret file at {p}", flush=True)
                try:
                    with open(p, "r") as f:
                        cookie_content = f.read()
                    break
                except Exception as e:
                    print(f"❌ Error reading secret file {p}: {e}")

    # 3. Write to a guaranteed writable location
    if cookie_content:
        # Use current file's directory for predictability
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        try:
            # Clean up content
            cookie_content = cookie_content.strip().strip('"').strip("'")
            with open(output_path, "w") as f:
                f.write(cookie_content)
            print(f"✅ Writable cookies.txt created at {output_path}", flush=True)
        except Exception as e:
            print(f"❌ Failed to write local cookies.txt: {e}", flush=True)
    else:
        print("⚠️ No YouTube cookies found (search may be restricted)", flush=True)

    print("\n🔐 [ADVANCED] YouTube OAuth2 enabled.", flush=True)
    print("If extraction fails, check logs for a code (google.com/device) to link your account.", flush=True)

@app.get("/")
async def root():
    return {"message": "AudioArc Bridge Server is online"}

@app.get("/api/search", response_model=SearchResponse, response_model_by_alias=True)
@limiter.limit("30/minute")
async def search(request: Request, q: str = Query(..., min_length=1)):
    results = await youtube_service.search_youtube(q)
    return {"results": results}

@app.get("/api/stream/{video_id}", response_model=StreamInfo)
@limiter.limit("20/minute")
async def stream(request: Request, video_id: str):
    """
    Returns stream metadata, pointing the stream_url to our local bridge/proxy.
    """
    info = await youtube_service.get_stream_url(video_id)
    if not info:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # Point the frontend to our bridge instead of direct YouTube CDN
    # This fulfills the "bridge" requirement and bypasses client IP blocks
    base_url = str(request.base_url).rstrip('/')
    info["stream_url"] = f"{base_url}/api/audio_proxy/{video_id}"
    
    return info

@app.get("/api/audio_proxy/{video_id}")
@limiter.limit("20/minute")
async def audio_proxy(request: Request, video_id: str):
    """
    Acting as a bridge: fetches audio from YouTube CDN and streams it to the client.
    This bypasses IP blocking and provides a direct stream URL for the frontend.
    """
    info = await youtube_service.get_stream_url(video_id)
    if not info or not info.get("stream_url"):
         raise HTTPException(status_code=404, detail="Audio stream URL not found")
    
    stream_url = info["stream_url"]
    
    async def generate_chunks():
        async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
            try:
                async with client.stream("GET", stream_url) as response:
                    # Forward the stream chunks to the client
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 64):
                        yield chunk
            except Exception as e:
                print(f"Streaming error for {video_id}: {e}")

    # Use audio/mpeg as a safe default, or better: detect from info
    return StreamingResponse(
        generate_chunks(),
        media_type="audio/mpeg", 
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{video_id}.mp3"',
            "Cache-Control": "public, max-age=3600"
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
