from cachetools import TTLCache
from typing import Any, Optional

class CacheManager:
    """
    CacheManager handles in-memory caching of YouTube metadata and stream URLs.
    This reduces the number of calls to yt-dlp, minimizing the risk of IP blocking
    and significantly improving response times for repeated requests.
    """
    def __init__(self, ttl: int = 1800, maxsize: int = 1000):
        # Result cache for video stream URLs (30 minutes TTL)
        self.stream_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        # Search results cache (15 minutes TTL for variety)
        self.search_cache = TTLCache(maxsize=maxsize, ttl=ttl // 2)

    def get_stream(self, video_id: str) -> Optional[Any]:
        return self.stream_cache.get(video_id)

    def set_stream(self, video_id: str, data: Any):
        self.stream_cache[video_id] = data

    def get_search(self, query: str) -> Optional[Any]:
        return self.search_cache.get(query)

    def set_search(self, query: str, results: Any):
        self.search_cache[query] = results

# Singleton instance for high-performance access
cache_manager = CacheManager()
