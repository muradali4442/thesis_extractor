from __future__ import annotations

import sys
from pathlib import Path
import click
from . import pdf as pdfmod
from . import rag as ragmod
from . import eval as evalmod
from . import visualize as viz


@click.group()
def main():
    """Thesis Extractor CLI."""


@main.group()
def pdf():
    """PDF utilities."""


@pdf.command("extract")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_path", type=click.Path(dir_okay=False), required=True)
def pdf_extract(pdf_path: str, out_path: str):
    text = pdfmod.extract_text_from_pdf(pdf_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(text, encoding="utf-8")
    click.echo(f"Wrote text to {out_path}")


@pdf.command("tables")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_csv", type=click.Path(dir_okay=False), required=True)
def pdf_tables(pdf_path: str, out_csv: str):
    tables = pdfmod.extract_tables_from_pdf(pdf_path)
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    pdfmod.save_tables_to_csv(tables, out_csv)
    click.echo(f"Wrote tables to {out_csv}")


@main.group()
def ocr():
    """OCR utilities."""


@ocr.command("images")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_dir", type=click.Path(file_okay=False), required=True)
def ocr_images(pdf_path: str, out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    images = pdfmod.pdf_to_images(pdf_path)
    for i, img in enumerate(images):
        img.save(Path(out_dir) / f"page_{i+1:03d}.png")
    click.echo(f"Saved {len(images)} images to {out_dir}")


@ocr.command("text")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
def ocr_text(pdf_path: str):
    images = pdfmod.pdf_to_images(pdf_path)
    text = pdfmod.ocr_images(images)
    click.echo(text)


@main.group()
def rag():
    """RAG pipeline (Haystack)."""


@rag.command("index")
@click.option("--data", "data_path", type=click.Path(exists=True), required=True, help="Text file to index.")
def rag_index(data_path: str):
    store = ragmod.build_document_store()
    text = Path(data_path).read_text(encoding="utf-8")
    ragmod.index_texts(store, [text])
    click.echo("Indexed 1 document.")


@rag.command("ask")
@click.option("--question", required=True)
@click.option("--top-k", default=5, show_default=True)
def rag_ask(question: str, top_k: int):
    store = ragmod.build_document_store()
    pipe = ragmod.build_qa_pipeline(store)
    # This is a minimal demo; in a real run, you'd persist the store and reuse it.
    ragmod.index_texts(store, [question])  # placeholder to avoid empty store
    ans = ragmod.ask(pipe, question, top_k=top_k)
    click.echo(ans)


@main.group()
def eval():
    """Evaluation utilities."""


@eval.command("run")
@click.option("--pred", "pred_csv", type=click.Path(exists=True), required=True)
@click.option("--gold", "gold_csv", type=click.Path(exists=True), required=True)
@click.option("--out", "out_csv", type=click.Path(dir_okay=False), required=True)
def eval_run(pred_csv: str, gold_csv: str, out_csv: str):
    df = evalmod.evaluate_csv(pred_csv, gold_csv, out_csv)
    click.echo(df.to_string(index=False))


@main.group()
def viz():
    """Visualization helpers."""


@viz.command("metrics")
@click.option("--csv", "csv_path", type=click.Path(exists=True), required=True)
def viz_metrics(csv_path: str):
    viz.plot_metrics(csv_path)
