import yt_dlp
import asyncio
import os
from typing import List, Optional

class YouTubeService:
    """
    YouTubeService handles interaction with YouTube via yt-dlp.
    Optimized for local extraction with minimal caching for speed.
    """
    def __init__(self):
        self._stream_cache = {} # Simple in-memory cache
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'ios'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'concurrent_fragment_downloads': 10,
            'extract_flat': 'in_playlist',
            'no_playlist': True,
            'ffmpeg_location': os.getenv("FFMPEG_PATH"),
        }

    def _get_cookie_file(self) -> Optional[str]:
        """Search for the writable cookies.txt."""
        paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies.txt"),
            "cookies.txt",
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    async def search_youtube(self, query: str, max_results: int = 15) -> List[dict]:
        opts = self.ydl_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
            'default_search': 'ytsearch',
        })

        if cookie_file := self._get_cookie_file():
            opts['cookiefile'] = cookie_file

        def _extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

        try:
            print(f"Searching YouTube for: {query}", flush=True)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _extract)
            tracks = []
            if 'entries' in result:
                for entry in result['entries']:
                    tracks.append({
                        "title": entry.get("title", ""),
                        "artist": entry.get("uploader", "Unknown Artist"),
                        "video_id": entry.get("id"),
                        "duration": int(entry.get("duration", 0)),
                        "thumbnail": entry.get("thumbnails", [{"url": ""}])[0].get("url") if entry.get("thumbnails") else ""
                    })
            print(f"Found {len(tracks)} tracks via yt-dlp", flush=True)
            return tracks
        except Exception as e:
            print(f"yt-dlp search failed: {e}", flush=True)
            return []

    async def get_stream_url(self, video_id: str) -> Optional[dict]:
        if video_id in self._stream_cache:
            return self._stream_cache[video_id]

        opts = self.ydl_opts.copy()
        opts.update({
            'format': 'bestaudio/best', 
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'force_ipv4': True,
            'extract_flat': True,
            'skip_download': True,
            'http_chunk_size': 1024 * 1024,
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'android', 'ios', 'tv'],
                    'skip': ['hls', 'dash']
                }
            }
        })

        if cookie_file := self._get_cookie_file():
            opts['cookiefile'] = cookie_file

        def _extract():
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            print(f"Extracting stream URL for {video_id}...", flush=True)
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract)
            
            direct_url = info.get('url')
            if not direct_url and 'formats' in info:
                formats = info['formats']
                audio_only = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_only:
                    audio_only.sort(key=lambda x: x.get('abr') or x.get('tbr') or 0, reverse=True)
                    direct_url = audio_only[0]['url']
                else:
                    any_with_url = [f for f in formats if f.get('url')]
                    if any_with_url:
                        any_with_url.sort(key=lambda x: x.get('tbr') or 0, reverse=True)
                        direct_url = any_with_url[0]['url']

            if direct_url:
                print(f"yt-dlp extraction successful for {video_id}", flush=True)
                
                # Try to get the actual format's mime-type
                mime_type = "audio/mpeg"
                for f in info.get('formats', []):
                    if f.get('url') == direct_url:
                        mime_type = f.get('mime_type', mime_type)
                        break

                data = {
                    "stream_url": direct_url,
                    "format": info.get('ext', 'unknown'),
                    "mime_type": mime_type,
                    "duration": int(info.get('duration', 0)),
                    "title": info.get('title', 'Unknown Title'),
                    "thumbnail": info.get('thumbnail', ''),
                    "video_id": video_id
                }
                self._stream_cache[video_id] = data
                return data
        except Exception as e:
            print(f"yt-dlp extraction failed for {video_id}: {e}", flush=True)
        
        return None

youtube_service = YouTubeService()
