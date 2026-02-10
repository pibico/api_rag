"""
LEANN Vector Database Service
Integration with LEANN for efficient vector storage and retrieval
Optimized for Markdown documents
"""
import os
import glob
from typing import List, Dict, Any, Optional
from leann import LeannBuilder, LeannSearcher
import fitz  # PyMuPDF
from app.config import settings


class LeannService:
    """Service for managing LEANN vector indices"""

    def __init__(self):
        self.index_base_path = settings.leann_index_path
        self.backend = settings.leann_backend
        self.batch_size = settings.leann_embedding_batch_size
        self.use_gpu = settings.leann_use_gpu
        self.num_threads = settings.leann_num_threads
        os.makedirs(self.index_base_path, exist_ok=True)

    def _get_index_path(self, document_id: str) -> str:
        """Get the path for a document's index"""
        return os.path.join(self.index_base_path, f"doc_{document_id}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            full_text = ""

            for page_num, page in enumerate(doc):
                full_text += f"\n--- Page {page_num + 1} ---\n"
                full_text += page.get_text()

            doc.close()
            return full_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def extract_text_from_md(self, file_path: str) -> str:
        """Extract text from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading markdown file: {str(e)}")

    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text from various file types"""
        if file_type == "application/pdf" or file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_type in ["text/plain", "text/markdown", "text/md"] or file_path.endswith(('.txt', '.md', '.markdown')):
            return self.extract_text_from_md(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Chunk text into overlapping segments
        Optimized for markdown with section awareness
        """
        chunks = []
        text_length = len(text)

        if text_length <= chunk_size:
            return [text]

        # Try to split by markdown headers first
        lines = text.split('\n')
        current_chunk = ""

        for line in lines:
            # Check if adding this line would exceed chunk size
            if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap by including last few lines
                overlap_text = '\n'.join(current_chunk.split('\n')[-3:])
                current_chunk = overlap_text + '\n' + line
            else:
                current_chunk += line + '\n'

        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def build_index(
        self,
        document_id: str,
        file_path: str,
        file_type: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Build LEANN index for a document
        Returns: dict with status and metadata
        """
        try:
            # Extract text
            text = self.extract_text_from_file(file_path, file_type)

            # Chunk text
            chunks = self.chunk_text(text, chunk_size, overlap)

            # Create LEANN builder - use CUDA if available
            index_path = self._get_index_path(document_id)

            # Auto-detect CUDA availability (can be overridden by config)
            import torch
            device = 'cuda' if (torch.cuda.is_available() and self.use_gpu) else 'cpu'

            # Initialize builder with optimized settings
            builder = LeannBuilder(
                backend_name=self.backend,
                device=device,
                batch_size=self.batch_size
            )

            # Add chunks to index
            for chunk in chunks:
                if chunk.strip():  # Only add non-empty chunks
                    builder.add_text(chunk)

            # Build and save index
            builder.build_index(index_path)

            return {
                "status": "success",
                "num_chunks": len(chunks),
                "index_path": index_path,
                "text_length": len(text)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def search(
        self,
        document_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search LEANN index for relevant chunks
        Returns: list of dicts with chunk text and score
        """
        try:
            index_path = self._get_index_path(document_id)

            # Check if LEANN index files exist (LEANN stores as files with prefix, not directory)
            meta_file = f"{index_path}.meta.json"
            if not os.path.exists(meta_file):
                raise ValueError(f"Index not found for document {document_id}")

            # Create searcher - use CUDA if available
            import torch
            device = 'cuda' if (torch.cuda.is_available() and self.use_gpu) else 'cpu'

            # Initialize searcher with optimized settings
            searcher = LeannSearcher(
                index_path,
                device=device,
                batch_size=self.batch_size
            )

            # Search
            results = searcher.search(query, top_k=top_k)

            # Format results
            formatted_results = []
            for idx, result in enumerate(results):
                # Handle both tuple format (text, score) and SearchResult objects
                if isinstance(result, tuple):
                    text, score = result
                else:
                    # SearchResult object has .text and .score attributes
                    text = result.text if hasattr(result, 'text') else str(result)
                    score = result.score if hasattr(result, 'score') else 0.0

                formatted_results.append({
                    "rank": idx + 1,
                    "text": text,
                    "score": float(score) if hasattr(score, '__float__') else score
                })

            return formatted_results

        except Exception as e:
            raise Exception(f"Error searching index: {str(e)}")

    def delete_index(self, document_id: str) -> bool:
        """Delete LEANN index for a document"""
        try:
            index_path = self._get_index_path(document_id)

            # LEANN stores index as multiple files with prefix, not as directory
            # Delete all files matching the pattern
            pattern = f"{index_path}.*"
            files_to_delete = glob.glob(pattern)

            if files_to_delete:
                for file in files_to_delete:
                    os.remove(file)
                return True
            return False

        except Exception as e:
            raise Exception(f"Error deleting index: {str(e)}")

    def index_exists(self, document_id: str) -> bool:
        """Check if index exists for a document"""
        index_path = self._get_index_path(document_id)
        # Check for LEANN meta file (LEANN stores as files with prefix, not directory)
        meta_file = f"{index_path}.meta.json"
        return os.path.exists(meta_file)


# Singleton instance
leann_service = LeannService()
