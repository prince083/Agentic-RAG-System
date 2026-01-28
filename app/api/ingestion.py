from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.ingestion.processor import processor
from app.models.document import IngestionResponse, ProcessedChunk

router = APIRouter()

@router.post("/ingest", response_model=List[IngestionResponse])
async def ingest_documents(files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        if not file.filename:
            continue
            
        try:
            content = await file.read()
            filename = file.filename.lower()
            extracted_chunks = []
            
            if filename.endswith(".pdf"):
                extracted_chunks = await processor.parse_pdf(content, file.filename)
            elif filename.endswith(".docx"):
                extracted_chunks = await processor.parse_docx(content, file.filename)
            else:
                # Skip unsupported files or log error, but don't crash whole batch
                print(f"Skipping unsupported file: {filename}")
                continue

            # Convert to Pydantic models (with global chunk indexing)
            processed_chunks = []
            for i, chunk in enumerate(extracted_chunks):
                processed_chunks.append(ProcessedChunk(
                    text=chunk["text"],
                    metadata=chunk["metadata"],
                    chunk_index=i, # Use global index i instead of chunk specific index
                    source_document=file.filename
                ))
            
            # Store in Vector DB
            if not processed_chunks:
                results.append(IngestionResponse(
                    filename=file.filename,
                    status="error",
                    error_message="No text extracted. Is this a scanned PDF or image?"
                ))
                continue

            from app.services.retrieval.vector_db import vector_db
            await vector_db.add_chunks(processed_chunks)
            
            results.append(IngestionResponse(
                filename=file.filename,
                total_chunks=len(processed_chunks),
                chunks=processed_chunks
            ))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error processing {file.filename}: {e}")
            
            results.append(IngestionResponse(
                filename=file.filename,
                status="error",
                error_message=str(e)
            ))

    return results
