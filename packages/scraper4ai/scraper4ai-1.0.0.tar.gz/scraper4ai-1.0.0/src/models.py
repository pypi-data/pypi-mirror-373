from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LinkData:
    url: str
    text: Optional[str] = None  

@dataclass
class ImageData:
    url: str
    alt_text: Optional[str] = None 

@dataclass
class VideoData:
    url: str
    title: Optional[str] = None  

@dataclass
class ScrapedResult:
    url: str
    status_code: int
    raw_html: str
    markdown: str
    links: List[LinkData] = field(default_factory=list)
    image_links: List[ImageData] = field(default_factory=list)
    video_links: List[VideoData] = field(default_factory=list)
