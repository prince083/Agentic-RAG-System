from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    query: str
    k: int = 5

class SearchResult(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
