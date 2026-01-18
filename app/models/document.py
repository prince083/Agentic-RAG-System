from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ProcessedChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    chunk_index: int
    source_document: str

class IngestionResponse(BaseModel):
    filename: str
    total_chunks: int
    chunks: List[ProcessedChunk]
    status: str = "success"
