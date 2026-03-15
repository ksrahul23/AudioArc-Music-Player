from pydantic import BaseModel
from typing import List, Optional

class TrackSearchResult(BaseModel):
    """
    Search endpoint response model.
    """
    title: str
    artist: str  # maps to uploader in yt-dlp
    videoId: str
    duration: int
    thumbnail: str

class SearchResponse(BaseModel):
    results: List[TrackSearchResult]

class StreamInfo(BaseModel):
    """
    Stream endpoint response model.
    """
    title: str
    stream_url: str
    thumbnail: str
    duration: int
    videoId: str

class ErrorResponse(BaseModel):
    detail: str
