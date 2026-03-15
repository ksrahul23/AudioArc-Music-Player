import yt_dlp
import asyncio
import os
from typing import List, Optional
from cache.cache_manager import cache_manager

class YouTubeService:
    """
    Core service for interacting with YouTube using yt-dlp.
    Optimized for Android player client to minimize blocks.
    """
    def __init__(self):
        self.common_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',  # Force IPv4
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash']
                }
            }
        }

    def _get_cookies(self) -> Optional[str]:
        # Look for cookies.txt in the backend root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookie_path = os.path.join(base_dir, "cookies.txt")
        return cookie_path if os.path.exists(cookie_path) else None

    async def search_tracks(self, query: str, max_results: int = 15) -> List[dict]:
        """
        Search for music tracks. Returns metadata without stream URLs.
        """
        # Check cache first
        cached = cache_manager.get_search(query)
        if cached:
            return cached

        opts = self.common_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
            'default_search': 'ytsearch',
        })
        
        cookie_path = self._get_cookies()
        if cookie_path:
            opts['cookiefile'] = cookie_path

        def _extract():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _extract)
            songs = []
            if 'entries' in result:
                for entry in result['entries']:
                    songs.append({
                        "title": entry.get("title", ""),
                        "artist": entry.get("uploader", "Unknown Artist"),
                        "videoId": entry.get("id"),
                        "duration": int(entry.get("duration", 0)),
                        "thumbnail": entry.get("thumbnails", [{"url": ""}])[0].get("url") if entry.get("thumbnails") else "",
                    })
            
            cache_manager.set_search(query, songs)
            return songs
        except Exception as e:
            print(f"yt-dlp search error: {str(e)}")
            return []

    async def get_stream_info(self, video_id: str) -> Optional[dict]:
        """
        Extract direct stream URL and metadata for a video.
        """
        # Check cache first
        cached = cache_manager.get_stream(video_id)
        if cached:
            return cached

        opts = self.common_opts.copy()
        opts.update({
            'format': 'bestaudio/best',
        })
        
        cookie_path = self._get_cookies()
        if cookie_path:
            opts['cookiefile'] = cookie_path

        def _extract():
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract)
            
            # Find the best direct audio URL
            stream_url = info.get('url')
            if not stream_url and 'formats' in info:
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    # Sort by average bitrate descending
                    audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                    stream_url = audio_formats[0]['url']

            if not stream_url:
                return None

            data = {
                "title": info.get("title", ""),
                "stream_url": stream_url,
                "thumbnail": info.get("thumbnail", ""),
                "duration": int(info.get("duration", 0)),
                "videoId": video_id,
                "artist": info.get("uploader", "Unknown Artist")
            }
            
            cache_manager.set_stream(video_id, data)
            return data
        except Exception as e:
            print(f"yt-dlp extraction error for {video_id}: {str(e)}")
            return None

# Singleton service instance
youtube_service = YouTubeService()
