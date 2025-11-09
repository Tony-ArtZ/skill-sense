#!/usr/bin/env python3
"""
RAG Manager for SkillSense Platform.
Handles document ingestion, embedding, and semantic search using FAISS.
"""

import os
import json
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager
import PyPDF2
from pathlib import Path
import asyncio
import httpx

# Optional imports for document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class RAGManager:
    def __init__(self, dimension=1024):
        self.dimension = dimension
        self.db_manager = DatabaseManager("data/talent_database.db")
        self.llm_manager = LLMManager()

        try:
            class OpenRouterEmbedder:
                def __init__(self):
                    self.api_key = os.getenv('OPENROUTER_API_KEY')
                    self.base_url = "https://openrouter.ai/api/v1"
                    self.model = "qwen/qwen3-embedding-0.6b"
                    self.async_client = httpx.AsyncClient(timeout=30.0)

                async def encode(self, texts, convert_to_numpy=True):
                    if isinstance(texts, str):
                        texts = [texts]

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://openrouter.ai",
                        "Content-Type": "application/json"
                    }
                    data = {"model": self.model, "input": texts, "encoding_format": "float"}

                    response = await self.async_client.post(f"{self.base_url}/embeddings", headers=headers, json=data)
                    response.raise_for_status()

                    result = response.json()
                    if "data" in result and len(result["data"]) > 0:
                        embeddings = [item["embedding"] for item in result["data"]]
                        if convert_to_numpy:
                            return np.array(embeddings, dtype='float32')
                        return embeddings
                    else:
                        raise Exception("No embedding data in response")

            self.embedder = OpenRouterEmbedder()
            print("✅ Using OpenRouter embeddings (async)")
        except Exception as e:
            print(f"Falling back to local embeddings: {str(e)}")
            self.embedder = SentenceTransformer('all-mpnet-base-v2')
            self.dimension = 768
            print("✅ Using local sentence transformer embeddings")

        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.embeddings = []
        self._load_index()

    def _load_index(self):
        try:
            if os.path.exists("data/faiss_index.bin"): self.index = faiss.read_index("data/faiss_index.bin")
            if os.path.exists("data/documents.pkl"):
                with open("data/documents.pkl", 'rb') as f: self.documents = pickle.load(f)
            if os.path.exists("data/embeddings.npy"): self.embeddings = np.load("data/embeddings.npy")
            print(f"Loaded {len(self.documents)} document chunks from existing index")
        except Exception as e:
            print(f"No existing index found, starting fresh: {str(e)}")

    def _save_index(self):
        os.makedirs("data", exist_ok=True)
        faiss.write_index(self.index, "data/faiss_index.bin")
        with open("data/documents.pkl", 'wb') as f: pickle.dump(self.documents, f)
        if self.embeddings.size > 0: np.save("data/embeddings.npy", self.embeddings)

    def _get_content_from_file(self, file_path: str, file_extension: str) -> str:
        """Extract text content from a file based on its extension."""
        if file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_extension == ".pdf":
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)
        elif file_extension == ".docx":
            if not DOCX_AVAILABLE:
                raise ImportError("python-docx is not installed. Please install it with 'pip install python-docx'")
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    async def add_document(self, file_path: str, employee_id: int, document_type: str = "resume") -> Dict[str, Any]:
        """
        Adds a document to the RAG system, processing its content based on file type.
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            text_content = await asyncio.to_thread(self._get_content_from_file, file_path, file_extension)
            
            if not text_content.strip():
                return {"success": False, "error": "No text content found in document"}

            doc_id = await asyncio.to_thread(
                self.db_manager.execute_query,
                "INSERT INTO employee_documents (employee_id, document_type, content, file_path) VALUES (?, ?, ?, ?)",
                (employee_id, document_type, text_content, file_path)
            )

            chunks = self._chunk_text(text_content)
            new_embeddings = await self.embedder.encode(chunks, convert_to_numpy=True)
            
            self.index.add(new_embeddings)
            
            for i, chunk in enumerate(chunks):
                self.documents.append({'doc_id': doc_id, 'chunk_text': chunk, 'employee_id': employee_id, 'file_path': file_path, 'file_type': file_extension, 'chunk_index': i, 'total_chunks': len(chunks)})
            
            if self.embeddings.size == 0:
                self.embeddings = new_embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            await asyncio.to_thread(self._save_index)

            return {"success": True, "doc_id": doc_id, "chunks_processed": len(chunks), "message": f"Successfully processed {file_extension} document"}
        except Exception as e:
            return {"success": False, "error": f"Failed to add document: {str(e)}"}


    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if chunk_words: chunks.append(" ".join(chunk_words))
        return chunks

    async def semantic_search_and_generate(self, query: str) -> Dict[str, Any]:
        """
        Performs semantic search and then generates a RAG response.
        Returns a dictionary with 'success', 'answer', and 'sources'.
        """
        try:
            print("[RAG_TRACE] Starting semantic_search_and_generate...")
            relevant_chunks = await self.semantic_search(query, top_k=5)
            print(f"[RAG_TRACE] Found {len(relevant_chunks)} relevant chunks.")
            rag_answer = await self.generate_rag_response(query, relevant_chunks)
            print("[RAG_TRACE] Generated RAG answer.")
            
            sources = [{'employee_id': chunk["employee_id"], 'similarity_score': chunk["similarity_score"], 'file_path': chunk["file_path"], 'snippet': chunk["chunk_text"][:200] + "..."} for chunk in relevant_chunks[:3]] if relevant_chunks else []

            print("[RAG_TRACE] Finished semantic_search_and_generate successfully.")
            return {"success": True, "answer": rag_answer, "sources": sources, "result_count": len(relevant_chunks)}
        except Exception as e:
            print(f"[RAG_TRACE] Exception in semantic_search_and_generate: {e}")
            return {"success": False, "answer": f"Failed to retrieve RAG response: {str(e)}", "sources": [], "result_count": 0, "error": str(e)}

    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search for relevant document chunks."""
        try:
            print("[RAG_TRACE] Starting semantic_search...")
            print("[RAG_TRACE] Encoding query for semantic search...")
            query_embedding = await self.embedder.encode([query], convert_to_numpy=True)
            print("[RAG_TRACE] Query encoded successfully.")

            if self.index.ntotal == 0:
                print("[RAG_TRACE] Index is empty, returning no results.")
                return []
            
            print("[RAG_TRACE] Searching FAISS index...")
            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            print("[RAG_TRACE] FAISS index search complete.")
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['similarity_score'] = float(1 / (1 + distance))
                    doc['rank'] = i + 1
                    results.append(doc)
            
            print(f"[RAG_TRACE] Prepared {len(results)} results.")
            return results
        except Exception as e:
            print(f"❌ Semantic search failed: {str(e)}")
            return []

    async def generate_rag_response(self, query: str, context_chunks: List[Dict]) -> str:
        if not context_chunks:
            print("[RAG_TRACE] No context chunks provided, returning generic response.")
            return "No relevant information found in the documents."
        
        context = "\n\n".join([f"Document {i+1} (Employee {chunk['employee_id']}): {chunk['chunk_text']}" for i, chunk in enumerate(context_chunks[:3])])
        prompt = f"You are a talent analytics expert... Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        print("[RAG_TRACE] Invoking LLM to generate final answer...")
        llm = self.llm_manager.get_llm("default")
        response = await asyncio.to_thread(llm.invoke, prompt)
        print("[RAG_TRACE] LLM invocation complete.")
        
        return response.content.strip()

    def get_document_stats(self) -> Dict[str, Any]:
        return {"total_chunks": len(self.documents), "total_documents": len(set(doc['doc_id'] for doc in self.documents)), "index_size": self.index.ntotal, "embedding_dimension": self.dimension}