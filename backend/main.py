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
        'noplaylist': True,
        'extract_flat': 'in_playlist',
        'default_search': 'ytsearch',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash']
            }
        }
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
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Use full URL for better extraction reliability
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Extracting stream for: {video_url}")
            info = ydl.extract_info(video_url, download=False)
            
            # Try to get the direct URL from formats if not in root
            if 'url' not in info and 'formats' in info:
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        return f['url']
            
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
