from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import asyncio
import httpx
import os

app = FastAPI(title="Realtime Music App API")

# Helper to ensure cookies are present
def ensure_cookies():
    cookies_content = os.getenv("YT_COOKIES")
    # Try multiple paths for reliability in cloud environments
    paths_to_try = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt"),
        "/tmp/cookies.txt",
        "cookies.txt"
    ]
    
    selected_path = paths_to_try[0]
    
    if not cookies_content:
        print("ℹ️ Diagnostics: YT_COOKIES environment variable is EMPTY or NOT SET.")
        # Check if file already exists from a previous run or git
        for p in paths_to_try:
            if os.path.exists(p):
                return p
        return None

    # Cleanup and verify format
    cookies_content = cookies_content.strip().strip('"').strip("'")
    if not cookies_content.startswith("#"):
        print("⚠️ Diagnostics: YT_COOKIES does not start with # (Netscape format). Please check your export!")

    # Write to the first writable path
    for p in paths_to_try:
        try:
            with open(p, "w") as f:
                f.write(cookies_content)
            print(f"✅ Diagnostics: Successfully wrote cookies to {p} ({len(cookies_content)} bytes)")
            return p
        except Exception as e:
            print(f"❌ Diagnostics: Failed to write to {p}: {str(e)}")
            continue
            
    return None

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper for Piped API Fallback
async def get_piped_stream(video_id: str):
    piped_instances = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.leptons.xyz",
        "https://pipedapi.adminforge.de",
        "https://piped-api.lunar.icu",
        "https://api.piped.projectsegfau.lt",
        "https://pipedapi.moe.xyz",
        "https://pipedapi.rammer.pw"
    ]
    
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        for instance in piped_instances:
            try:
                print(f"Trying Piped fallback: {instance}")
                response = await client.get(f"{instance}/streams/{video_id}")
                if response.status_code == 200:
                    data = response.json()
                    audio_streams = data.get("audioStreams", [])
                    if audio_streams:
                        audio_streams.sort(key=lambda x: x.get("bitrate", 0), reverse=True)
                        return audio_streams[0]["url"]
                    if data.get("hls"):
                        return data["hls"]
            except Exception as e:
                print(f"Piped instance {instance} failed: {str(e)}")
                continue
    return None

async def piped_search_fallback(query: str):
    piped_instances = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.leptons.xyz",
        "https://pipedapi.adminforge.de"
    ]
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        for instance in piped_instances:
            try:
                print(f"Trying Piped search fallback: {instance}")
                response = await client.get(f"{instance}/search", params={"q": query, "filter": "music_songs"})
                if response.status_code == 200:
                    data = response.json()
                    songs = []
                    for item in data.get("items", []):
                        if item.get("type") == "stream":
                            songs.append({
                                "videoId": item.get("url", "").split("=")[-1],
                                "title": item.get("title", ""),
                                "artist": item.get("uploaderName", "Unknown Artist"),
                                "thumbnail": item.get("thumbnail", ""),
                                "duration": item.get("duration", 0),
                            })
                    return songs
            except Exception as e:
                 print(f"Piped search failed on {instance}: {str(e)}")
                 continue
    return []

async def search_youtube_smart(query: str, max_results: int = 15):
    cookie_path = ensure_cookies()
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extract_flat': 'in_playlist',
        'default_search': 'ytsearch',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'web_embedded', 'android'],
                'skip': ['hls', 'dash']
            }
        }
    }
    
    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path
        print(f"🔍 Using cookies for search: {cookie_path}")
    else:
        print("💡 Search proceeding without cookies (Environment variable missing)")

    try:
        print(f"Attempting yt-dlp search for: {query}")
        result = await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch{max_results}:{query}", download=False))
        if 'entries' in result:
            songs = []
            for entry in result['entries']:
                songs.append({
                    "videoId": entry.get("id"),
                    "title": entry.get("title", ""),
                    "artist": entry.get("uploader", "Unknown Artist"),
                    "thumbnail": entry.get("thumbnails", [{"url": ""}])[0].get("url") if entry.get("thumbnails") else "",
                    "duration": entry.get("duration", 0),
                })
            return songs
    except Exception as e:
        print(f"❌ yt-dlp search failed: {str(e)}. Falling back to Piped...")
        return await piped_search_fallback(query)
    
    return []

async def get_stream_url(video_id: str):
    cookie_path = ensure_cookies()
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'web_embedded', 'android'],
                'skip': ['hls', 'dash']
            }
        }
    }

    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path
        print(f"🎵 Using cookies for extraction: {cookie_path}")
    else:
        print("💡 Extraction proceeding without cookies (Environment variable missing)")

    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Attempting yt-dlp extraction for: {video_url}")
        
        info = await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(video_url, download=False))
        
        if 'url' not in info and 'formats' in info:
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                return audio_formats[0]['url']
        
        if 'url' in info:
             return info['url']
             
    except Exception as e:
        error_msg = str(e)
        print(f"❌ yt-dlp extraction failed: {error_msg}")
        
        if "confirm you're not a bot" in error_msg or "Sign in" in error_msg or "403" in error_msg:
            print("Triggering Piped API fallback...")
            piped_url = await get_piped_stream(video_id)
            if piped_url:
                print("✅ Piped fallback successful!")
                return piped_url
            
    piped_url = await get_piped_stream(video_id)
    if piped_url:
        return piped_url
        
    raise Exception("All stream extraction methods failed.")

@app.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    try:
        results = await search_youtube_smart(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream")
async def stream(videoId: str = Query(..., min_length=1)):
    try:
        url = await get_stream_url(videoId)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
