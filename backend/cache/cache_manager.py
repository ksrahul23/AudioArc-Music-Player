from cachetools import TTLCache
import time

class CacheManager:
    def __init__(self, ttl: int = 1800, maxsize: int = 1000):
        """
        Initialize the cache manager.
        :param ttl: Time to live in seconds (default: 1800s / 30m)
        :param maxsize: Maximum number of items in the cache
        """
        self.stream_cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.search_cache = TTLCache(maxsize=maxsize, ttl=(ttl // 2))  # Search results cache for 15m

    def get_stream(self, video_id: str):
        return self.stream_cache.get(video_id)

    def set_stream(self, video_id: str, data: dict):
        self.stream_cache[video_id] = data

    def get_search(self, query: str):
        return self.search_cache.get(query)

    def set_search(self, query: str, results: list):
        self.search_cache[query] = results

# Global cache instance
cache_manager = CacheManager()
