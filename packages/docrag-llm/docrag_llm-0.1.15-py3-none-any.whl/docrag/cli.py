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
    source: str = typer.Argument(..., help="Path or URL to document"),
    persist: str = typer.Option("./.chroma", help="Chroma persist dir", show_default=True),
    collection: str = typer.Option("demo", help="Chroma collection name", show_default=True),
    embed_model: str = typer.Option(
        "nomic-embed-text",
        "--embed",
        help="Embedding model to use (Ollama model tag)",
        show_default=True,
    ),
    chunk_chars: int = typer.Option(1000, help="Approx characters per chunk", show_default=True),
    chunk_overlap: int = typer.Option(200, help="Chunk overlap", show_default=True),
    fail_on_empty: bool = typer.Option(True, help="Abort if extracted text is empty", show_default=True),
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
    question: str = typer.Argument(..., help="Your query"),
    persist: str = typer.Option("./.chroma", help="Chroma persist dir", show_default=True),
    collection: str = typer.Option("demo", help="Chroma collection name", show_default=True),
    llm_model: str = typer.Option(
        "llama3.2:1b",
        "--llm",
        help="LLM model to use (Ollama model tag)",
        show_default=True,
    ),
    top_k: int = typer.Option(5, help="Top-k chunks to retrieve", show_default=True),
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