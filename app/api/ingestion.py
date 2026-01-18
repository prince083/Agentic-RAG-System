from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.ingestion.processor import processor
from app.models.document import IngestionResponse, ProcessedChunk

router = APIRouter()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    content = await file.read()
    filename = file.filename.lower()
    
    extracted_chunks = []
    
    try:
        if filename.endswith(".pdf"):
            extracted_chunks = await processor.parse_pdf(content, file.filename)
        elif filename.endswith(".docx"):
            extracted_chunks = await processor.parse_docx(content, file.filename)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX supported.")
            
        # Convert to Pydantic models
        processed_chunks = [
            ProcessedChunk(
                text=chunk["text"],
                metadata=chunk["metadata"],
                chunk_index=chunk["chunk_index"],
                source_document=file.filename
            ) for chunk in extracted_chunks
        ]
        
        # Store in Vector DB (Day 3 Addition)
        from app.services.retrieval.vector_db import vector_db
        await vector_db.add_chunks(processed_chunks)
        
        return IngestionResponse(
            filename=file.filename,
            total_chunks=len(processed_chunks),
            chunks=processed_chunks
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
