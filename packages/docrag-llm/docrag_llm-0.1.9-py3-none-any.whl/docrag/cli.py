# src/docrag/cli.py
from __future__ import annotations
import json
from pathlib import Path
import typer
from .config import DocragSettings
from .retrieve import RAGPipeline
from .convert import DoclingConverter

app = typer.Typer(help="DocRAG: Docling → Chroma → Ollama")

@app.command()
def ingest(
    source: str,
    persist: str = "./.chroma",
    collection: str = "demo",
    embed_model: str = "nomic-embed-text",
    chunk_chars: int = 1000,
    chunk_overlap: int = 200,
    fail_on_empty: bool = True,
):
    cfg = DocragSettings(
        persist_path=persist,
        collection=collection,
        embed_model=embed_model,
        chunk_chars=chunk_chars,
        chunk_overlap=chunk_overlap,
        fail_on_empty=fail_on_empty,
    )
    pipe = RAGPipeline(cfg)
    n = pipe.ingest(source)
    typer.echo(f"Ingested {n} chunks into '{collection}' at '{persist}'.")

@app.command()
def ask(
    question: str,
    persist: str = "./.chroma",
    collection: str = "demo",
    llm_model: str = "llama3.2:1b",
    top_k: int = 5,
):
    cfg = DocragSettings(
        persist_path=persist,
        collection=collection,
        llm_model=llm_model,
        top_k=top_k,
    )
    pipe = RAGPipeline(cfg)
    ans = pipe.ask(question)
    typer.echo("\n=== ANSWER ===\n")
    typer.echo(ans)

@app.command()
def export(source: str, out_dir: str = "./exports"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    conv = DoclingConverter()
    md, dct = conv.to_both(source)
    (out / "output.md").write_text(md, encoding="utf-8")
    (out / "output.json").write_text(json.dumps(dct, indent=2, ensure_ascii=False), encoding="utf-8")
    typer.echo(f"Saved: {out/'output.md'} and {out/'output.json'}")

def main() -> None:
    app()

if __name__ == "__main__":
    main()