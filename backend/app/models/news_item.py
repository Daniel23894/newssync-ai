from pydantic import BaseModel
from typing import Optional

# BaseModel will work as data validation 
class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    category: Optional[str] = "General"
    topic: Optional[str] = "General"
    published_hour: Optional[float] = None
    sentiment: Optional[float] = 0.0