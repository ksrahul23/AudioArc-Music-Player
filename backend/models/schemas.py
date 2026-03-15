from pydantic import BaseModel, Field
from typing import List, Optional

class TrackSearchResult(BaseModel):
    """
    Schema for individual search result items.
    """
    title: str
    artist: str = Field(..., alias="artist/channel")
    video_id: str
    duration: int
    thumbnail: str

    class Config:
        allow_population_by_field_name = True

class SearchResponse(BaseModel):
    """
    Schema for the /search endpoint response.
    """
    results: List[TrackSearchResult]

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "title": "Song Title",
                        "artist/channel": "Artist Name",
                        "video_id": "videoId123",
                        "duration": 240,
                        "thumbnail": "https://example.com/thumb.jpg"
                    }
                ]
            }
        }

class StreamInfo(BaseModel):
    """
    Schema for the /stream endpoint response.
    """
    title: str
    stream_url: str
    thumbnail: str
    duration: int
    video_id: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Song Title",
                "stream_url": "https://manifest.googlevideo.com/...",
                "thumbnail": "https://example.com/thumb.jpg",
                "duration": 240
            }
        }
