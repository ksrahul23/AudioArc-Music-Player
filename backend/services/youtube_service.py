import yt_dlp
import asyncio
import os
import httpx
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
        self.piped_instances = [
            "https://pipedapi.kavin.rocks",
            "https://pipedapi.leptons.xyz",
            "https://pipedapi.adminforge.de",
            "https://piped-api.lunar.icu",
            "https://api.piped.projectsegfau.lt",
            "https://pipedapi.rammer.pw"
        ]

    def _get_cookie_path(self):
        # Look in the backend/ folder (up one from services/)
        cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies.txt")
        if os.path.exists(cookie_path):
            return cookie_path
        # Fallback to current working directory
        if os.path.exists("cookies.txt"):
            return os.path.abspath("cookies.txt")
        return None

    async def search_tracks(self, query: str, max_results: int = 15) -> List[dict]:
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
            print(f"🔍 [yt-dlp Search] Using cookies: {cookie_path}", flush=True)

        try:
            print(f"Attempting yt-dlp search for: {query}", flush=True)
            def _extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            
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
            if songs:
                cache_manager.set_search(query, songs)
                return songs
        except Exception as e:
            print(f"❌ yt-dlp search failed: {str(e)}. Falling back to Piped...", flush=True)

        return await self._piped_search_fallback(query)

    async def get_stream_info(self, video_id: str) -> Optional[dict]:
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
            print(f"🔍 [yt-dlp Extract] Using cookies: {cookie_path}", flush=True)

        try:
            print(f"Attempting yt-dlp extraction for: {video_id}", flush=True)
            url = f"https://www.youtube.com/watch?v={video_id}"
            def _extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)

            info = await asyncio.to_thread(_extract)
            
            stream_url = info.get('url')
            if not stream_url and 'formats' in info:
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                    stream_url = audio_formats[0]['url']

            if stream_url:
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
            print(f"❌ yt-dlp extraction failed: {str(e)}. Falling back to Piped...", flush=True)

        return await self._piped_stream_fallback(video_id)

    async def _piped_search_fallback(self, query: str) -> List[dict]:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            for instance in self.piped_instances:
                try:
                    print(f"Trying Piped search fallback: {instance}", flush=True)
                    response = await client.get(f"{instance}/search", params={"q": query, "filter": "music_songs"})
                    if response.status_code == 200:
                        data = response.json()
                        songs = []
                        for item in data.get("items", []):
                            if item.get("type") == "stream":
                                video_id = item.get("url", "").split("=")[-1]
                                songs.append({
                                    "videoId": video_id,
                                    "title": item.get("title", ""),
                                    "artist": item.get("uploaderName", "Unknown Artist"),
                                    "thumbnail": item.get("thumbnail", ""),
                                    "duration": item.get("duration", 0),
                                })
                        if songs:
                            return songs
                except Exception as e:
                    print(f"Piped search failed on {instance}: {str(e)}", flush=True)
                    continue
        return []

    async def _piped_stream_fallback(self, video_id: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            for instance in self.piped_instances:
                try:
                    print(f"Trying Piped stream fallback: {instance}", flush=True)
                    response = await client.get(f"{instance}/streams/{video_id}")
                    if response.status_code == 200:
                        data = response.json()
                        audio_streams = data.get("audioStreams", [])
                        if audio_streams:
                            audio_streams.sort(key=lambda x: x.get("bitrate", 0), reverse=True)
                            stream_url = audio_streams[0]["url"]
                            return {
                                "videoId": video_id,
                                "title": data.get("title", "Unknown Title"),
                                "artist": data.get("uploader", "Unknown Artist"),
                                "thumbnail": data.get("thumbnailUrl", ""),
                                "duration": data.get("duration", 0),
                                "stream_url": stream_url
                            }
                except Exception as e:
                    print(f"Piped extraction failed on {instance}: {str(e)}", flush=True)
                    continue
        return None

# Global service instance
youtube_service = YouTubeService()
