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

    model_config = {
        "populate_by_name": True
    }

class SearchResponse(BaseModel):
    """
    Schema for the /search endpoint response.
    """
    results: List[TrackSearchResult]

    model_config = {
        "json_schema_extra": {
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Song Title",
                "stream_url": "https://manifest.googlevideo.com/...",
                "thumbnail": "https://example.com/thumb.jpg",
                "duration": 240,
                "video_id": "videoId123"
            }
        }
    }
