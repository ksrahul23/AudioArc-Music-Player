from cachetools import TTLCache
from typing import Any, Optional

class CacheManager:
    """
    In-memory TTL Cache Manager.
    Results are cached for 30 minutes to reduce IP blocking risk.
    """
    def __init__(self, ttl_seconds: int = 1800, max_size: int = 1000):
        # 30 minutes cache for stream URLs
        self._stream_cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        # 15 minutes cache for search results
        self._search_cache = TTLCache(maxsize=max_size, ttl=900)

    def get_stream(self, video_id: str) -> Optional[Any]:
        return self._stream_cache.get(video_id)

    def set_stream(self, video_id: str, data: Any):
        self._stream_cache[video_id] = data

    def get_search(self, query: str) -> Optional[Any]:
        return self._search_cache.get(query)

    def set_search(self, query: str, results: Any):
        self._search_cache[query] = results

# Singleton instance
cache_manager = CacheManager()
