import io
from typing import List, Dict, Any
import pypdf
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    async def parse_pdf(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page numbers."""
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
        start_page = 1
        chunks = []
        
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if not text.strip():
                continue
                
            page_metadata = {"page": i + start_page, "source": filename}
            page_chunks = self.process_text(text, page_metadata)
            chunks.extend(page_chunks)
            
        return chunks

    async def parse_docx(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Extract text from DOCX."""
        doc = docx.Document(io.BytesIO(file_content))
        full_text = "\n".join([para.text for para in doc.paragraphs])
        
        metadata = {"source": filename}
        return self.process_text(full_text, metadata)

    def process_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk text and attach metadata."""
        split_docs = self.text_splitter.create_documents([text], metadatas=[metadata])
        
        results = []
        for i, doc in enumerate(split_docs):
            results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "chunk_index": i
            })
        return results

processor = DocumentProcessor()
