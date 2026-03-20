import yt_dlp
import asyncio
import os
import httpx
from typing import List, Optional
from cache.cache_manager import cache_manager

class YouTubeService:
    """
    YouTubeService handles interaction with YouTube via yt-dlp.
    Optimized for Android player client and includes Piped API fallbacks.
    """
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',
            # Mimic a modern browser to reduce bot detection
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        # Multi-instance fallback for reliability
        self.piped_instances = [
            "https://pipedapi.kavin.rocks",
            "https://pipedapi.leptons.xyz",
            "https://pipedapi.adminforge.de",
            "https://piped-api.lunar.icu",
            "https://api.piped.projectsegfau.lt"
        ]

    def _get_cookie_file(self) -> Optional[str]:
        """
        Search for the writable cookies.txt created by the startup event.
        """
        paths = [
            # Guaranteed writable location created in main.py
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies.txt"),
            "cookies.txt",
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    async def search_youtube(self, query: str, max_results: int = 15) -> List[dict]:
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
            print(f"🔍 Searching YouTube for: {query}", flush=True)
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
            
            print(f"✅ Found {len(tracks)} tracks via yt-dlp", flush=True)
            if tracks:
                cache_manager.set_search(query, tracks)
                return tracks
        except Exception as e:
            print(f"❌ yt-dlp search failed for '{query}': {e}", flush=True)
            pass

        return await self._piped_search_fallback(query)

    async def get_stream_url(self, video_id: str) -> Optional[dict]:
        cached = cache_manager.get_stream(video_id)
        if cached:
            return cached
        opts = self.ydl_opts.copy()
        # Clean options for cloud reliability
        opts.update({
            'format': 'bestaudio/best', 
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
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
            print(f"🎬 Extracting stream URL for {video_id}...", flush=True)
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract)
            
            direct_url = info.get('url')
            if not direct_url and 'formats' in info:
                # Filter for best possible audio match
                formats = info['formats']
                audio_only = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                
                if audio_only:
                    audio_only.sort(key=lambda x: x.get('abr') or x.get('tbr') or 0, reverse=True)
                    direct_url = audio_only[0]['url']
                else:
                    # Last ditch fallback: find ANY format with a URL
                    any_with_url = [f for f in formats if f.get('url')]
                    if any_with_url:
                        any_with_url.sort(key=lambda x: x.get('tbr') or 0, reverse=True)
                        direct_url = any_with_url[0]['url']

            if direct_url:
                print(f"✅ yt-dlp extraction successful for {video_id}", flush=True)
                data = {
                    "stream_url": direct_url,
                    "format": info.get('ext', 'unknown'),
                    "duration": int(info.get('duration', 0))
                }
                cache_manager.set_stream(video_id, data)
                return data
        except Exception as e:
            print(f"⚠️ yt-dlp extraction failed for {video_id}: {e}", flush=True)

        # FINAL LAYER: Automatic Piped API Fallback for extraction
        print(f"🔄 Falling back to Piped API for extraction: {video_id}", flush=True)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Try multiple Piped instances if one is down
                instances = [
                    "https://pipedapi.kavin.rocks", 
                    "https://api.piped.victr.me",
                    "https://pipedapi.col7a.me",
                    "https://pipedapi.privacydev.net"
                ]
                for base_url in instances:
                    try:
                        resp = await client.get(f"{base_url}/streams/{video_id}")
                        if resp.status_code == 200:
                            data = resp.json()
                            audio_streams = data.get("audioStreams", [])
                            if audio_streams:
                                # Sort by bitrate and pick best
                                audio_streams.sort(key=lambda x: x.get("bitrate", 0), reverse=True)
                                print(f"✅ Piped extraction successful via {base_url}", flush=True)
                                data = {
                                    "stream_url": audio_streams[0]["url"],
                                    "format": audio_streams[0].get("format", "m4a"),
                                    "duration": data.get("duration", 0)
                                }
                                cache_manager.set_stream(video_id, data)
                                return data
                    except Exception as e:
                        print(f"⚠️ Piped instance {base_url} failed: {e}", flush=True)
                        continue
        except Exception as e:
            print(f"❌ All extraction methods failed for {video_id}: {e}", flush=True)
        
        return None

    async def _piped_search_fallback(self, query: str) -> List[dict]:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            for instance in self.piped_instances:
                try:
                    res = await client.get(f"{instance}/search", params={"q": query, "filter": "music_songs"})
                    if res.status_code == 200:
                        data = res.json()
                        tracks = []
                        for item in data.get("items", []):
                            if item.get("type") == "stream":
                                tracks.append({
                                    "title": item.get("title", ""),
                                    "artist": item.get("uploaderName", "Unknown Artist"),
                                    "video_id": item.get("url", "").split("=")[-1],
                                    "duration": item.get("duration", 0),
                                    "thumbnail": item.get("thumbnail", "")
                                })
                        return tracks
                except Exception: continue
        return []

    async def _piped_stream_fallback(self, video_id: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            for instance in self.piped_instances:
                try:
                    res = await client.get(f"{instance}/streams/{video_id}")
                    if res.status_code == 200:
                        data = res.json()
                        audio = sorted(data.get("audioStreams", []), key=lambda x: x.get("bitrate", 0), reverse=True)
                        if audio:
                            return {
                                "title": data.get("title", "Unknown Title"),
                                "stream_url": audio[0]["url"],
                                "thumbnail": data.get("thumbnailUrl", ""),
                                "duration": data.get("duration", 0),
                                "video_id": video_id
                            }
                except Exception: continue
        return None

youtube_service = YouTubeService()
