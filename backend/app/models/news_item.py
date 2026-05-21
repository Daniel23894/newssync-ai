from pydantic import BaseModel
from typing import Optional

# BaseModel will work as data validation 
class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    category: Optional[str] = "General"