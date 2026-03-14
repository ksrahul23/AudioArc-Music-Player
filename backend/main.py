from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import asyncio

app = FastAPI(title="Realtime Music App API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_youtube(query: str, max_results: int = 15):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
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
            return []
        except Exception as e:
            raise Exception(f"Failed to search: {str(e)}")

def get_stream_url(video_id: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Use full URL for better extraction reliability
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Extracting stream for: {video_url}")
            info = ydl.extract_info(video_url, download=False)
            if 'url' not in info:
                 raise Exception("No stream URL found in info")
            return info['url']
        except Exception as e:
            print(f"Extraction failed: {str(e)}")
            raise Exception(f"Failed to get stream: {str(e)}")

@app.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    try:
        results = await asyncio.to_thread(search_youtube, q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream")
async def stream(videoId: str = Query(..., min_length=1)):
    try:
        url = await asyncio.to_thread(get_stream_url, videoId)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
