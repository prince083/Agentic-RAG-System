from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.agent.rag import rag_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert Pydantic models to list of dicts for the service
        history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
        response = await rag_service.answer_question(request.message, history_dicts)
        return ChatResponse(
            answer=response["answer"],
            sources=list(set(response["sources"])) # Deduplicate sources
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return a polite error message to the AI instead of crashing
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
