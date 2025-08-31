from __future__ import annotations
from typing import List
import ollama
from .config import DocragSettings
from .convert import DoclingConverter
from .index import ChromaIndexer
from .utils import sentence_chunks

class RAGPipeline:
    def __init__(self, settings: DocragSettings) -> None:
        self.cfg = settings
        self.converter = DoclingConverter()
        self.indexer = ChromaIndexer(
            persist_path=self.cfg.persist_path,
            collection=self.cfg.collection,
            embed_model=self.cfg.embed_model,
        )
    def ingest(self, source: str) -> int:
        md = self.converter.to_markdown(source)
        if self.cfg.fail_on_empty and not md.strip():
            raise ValueError("Empty text extracted from source.")
        chunks = sentence_chunks(md, target=self.cfg.chunk_chars, overlap=self.cfg.chunk_overlap)
        self.indexer.reset_ids(len(chunks))
        self.indexer.add(chunks)
        return len(chunks)
    def ask(self, question: str) -> str:
        docs: List[str] = self.indexer.query(question, top_k=self.cfg.top_k)
        context = "\n\n".join(docs) if docs else ""
        prompt = (
            "Use ONLY the provided context to answer. If insufficient, say so briefly.\n\n"
            f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"
        )
        resp = ollama.chat(model=self.cfg.llm_model, messages=[{"role": "user", "content": prompt}])
        return resp["message"]["content"]
