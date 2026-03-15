from pydantic import BaseModel
from typing import List, Optional

class TrackBase(BaseModel):
    videoId: str
    title: str
    artist: str
    thumbnail: str
    duration: int

class SearchResponse(BaseModel):
    results: List[TrackBase]

class StreamInfo(BaseModel):
    videoId: str
    title: str
    artist: str
    thumbnail: str
    duration: int
    stream_url: str

class ErrorResponse(BaseModel):
    detail: str
