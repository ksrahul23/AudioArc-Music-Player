import yt_dlp
import asyncio
import os
from typing import List, Optional
from cache.cache_manager import cache_manager

class YouTubeService:
    """
    YouTubeService handles interaction with YouTube via yt-dlp.
    It uses the Android player client to avoid aggressive IP blocking.
    """
    def __init__(self):
        # Professional yt-dlp configuration as requested
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',  # Force IPv4 to avoid Render IPv6 issues
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash']
                }
            }
        }

    def _get_cookie_file(self) -> Optional[str]:
        # Check for cookies.txt in the backend root for resilience
        cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies.txt")
        return cookie_path if os.path.exists(cookie_path) else None

    async def search_youtube(self, query: str, max_results: int = 15) -> List[dict]:
        """
        Search for tracks and return metadata.
        """
        # Return cached results if available
        cached = cache_manager.get_search(query)
        if cached:
            return cached

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
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _extract)
            tracks = []
            
            if 'entries' in result:
                for entry in result['entries']:
                    tracks.append({
                        "title": entry.get("title", "Unknown Title"),
                        "artist/channel": entry.get("uploader", "Unknown Artist"),
                        "video_id": entry.get("id"),
                        "duration": int(entry.get("duration", 0)),
                        "thumbnail": entry.get("thumbnails", [{"url": ""}])[0].get("url") if entry.get("thumbnails") else ""
                    })
            
            cache_manager.set_search(query, tracks)
            return tracks
        except Exception as e:
            print(f"yt-dlp search exception: {e}")
            return []

    async def get_stream_url(self, video_id: str) -> Optional[dict]:
        """
        Extract the direct stream URL and metadata.
        """
        # Return cached stream info if available
        cached = cache_manager.get_stream(video_id)
        if cached:
            return cached

        opts = self.ydl_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
            'noplaylist': True,
        })

        if cookie_file := self._get_cookie_file():
            opts['cookiefile'] = cookie_file

        def _extract():
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract)
            
            # Extract direct URL from formats if not directly provided
            direct_url = info.get('url')
            if not direct_url and 'formats' in info:
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                    direct_url = audio_formats[0]['url']

            if not direct_url:
                return None

            data = {
                "title": info.get("title", "Unknown Title"),
                "stream_url": direct_url,
                "thumbnail": info.get("thumbnail", ""),
                "duration": int(info.get("duration", 0))
            }
            
            cache_manager.set_stream(video_id, data)
            return data
        except Exception as e:
            print(f"yt-dlp extraction exception for {video_id}: {e}")
            return None

# Singleton service for system-wide access
youtube_service = YouTubeService()
