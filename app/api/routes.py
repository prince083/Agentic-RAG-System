from fastapi import APIRouter
from app.api.ingestion import router as ingestion_router
from app.api.retrieval import router as retrieval_router
from app.api.chat import router as chat_router

router = APIRouter()

router.include_router(ingestion_router, tags=["ingestion"])
router.include_router(retrieval_router, tags=["retrieval"])
router.include_router(chat_router, tags=["chat"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}
