from fastapi import APIRouter, HTTPException
from app.models.search import SearchRequest, SearchResult
from app.services.retrieval.vector_db import vector_db
from typing import List

router = APIRouter()

@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    try:
        results = await vector_db.search(request.query, request.k)
        
        # Convert to Pydantic models
        return [
            SearchResult(
                text=res["text"],
                metadata=res["metadata"],
                score=res["distance"]
            ) for res in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
