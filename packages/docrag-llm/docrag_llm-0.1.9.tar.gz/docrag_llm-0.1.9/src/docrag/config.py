from __future__ import annotations
from pydantic import BaseModel, Field

class DocragSettings(BaseModel):
    persist_path: str = Field(default="./.chroma", description="Chroma persistent directory")
    collection: str = Field(default="demo", description="Chroma collection name")
    embed_model: str = Field(default="nomic-embed-text", description="Ollama embedding model")
    llm_model: str = Field(default="deepseek-r1:8b", description="Ollama chat model")
    chunk_chars: int = Field(default=1000, ge=200, description="Approx characters per chunk")
    chunk_overlap: int = Field(default=200, ge=0, description="Chunk overlap")
    top_k: int = Field(default=5, ge=1, description="Top-k retrieved chunks")
    fail_on_empty: bool = Field(default=True, description="Abort if extracted text is empty")
