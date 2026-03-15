import yt_dlp
import asyncio
import os
from typing import List, Optional
from cache.cache_manager import cache_manager

class YouTubeService:
    def __init__(self):
        self.common_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',  # IPv4 only
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash']
                }
            }
        }

    def _get_cookie_path(self):
        cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies.txt")
        return cookie_path if os.path.exists(cookie_path) else None

    async def search_tracks(self, query: str, max_results: int = 15) -> List[dict]:
        # Check cache
        cached = cache_manager.get_search(query)
        if cached:
            return cached

        opts = self.common_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
            'default_search': 'ytsearch',
        })
        
        cookie_path = self._get_cookie_path()
        if cookie_path:
            opts['cookiefile'] = cookie_path

        def _extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

        try:
            result = await asyncio.to_thread(_extract)
            songs = []
            if 'entries' in result:
                for entry in result['entries']:
                    songs.append({
                        "videoId": entry.get("id"),
                        "title": entry.get("title", ""),
                        "artist": entry.get("uploader", "Unknown Artist"),
                        "thumbnail": entry.get("thumbnails", [{"url": ""}])[0].get("url") if entry.get("thumbnails") else "",
                        "duration": entry.get("duration", 0),
                    })
            
            cache_manager.set_search(query, songs)
            return songs
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    async def get_stream_info(self, video_id: str) -> Optional[dict]:
        # Check cache
        cached = cache_manager.get_stream(video_id)
        if cached:
            return cached

        opts = self.common_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
        })
        
        cookie_path = self._get_cookie_path()
        if cookie_path:
            opts['cookiefile'] = cookie_path

        def _extract():
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            info = await asyncio.to_thread(_extract)
            
            stream_url = info.get('url')
            if not stream_url and 'formats' in info:
                # Fallback to finding best audio format direct URL
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                    stream_url = audio_formats[0]['url']

            if not stream_url:
                return None

            data = {
                "videoId": video_id,
                "title": info.get("title", ""),
                "artist": info.get("uploader", "Unknown Artist"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "stream_url": stream_url
            }
            
            cache_manager.set_stream(video_id, data)
            return data
        except Exception as e:
            print(f"Extraction error: {str(e)}")
            return None

# Global service instance
youtube_service = YouTubeService()
