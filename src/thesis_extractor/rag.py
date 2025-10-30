from __future__ import annotations
from typing import List, Optional
import os

from haystack import Document, Pipeline
from haystack.nodes import BM25Retriever, PromptTemplate, PromptNode
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import PreProcessor


def build_document_store() -> InMemoryDocumentStore:
    return InMemoryDocumentStore(use_bm25=True)


def make_documents(texts: List[str], meta: Optional[List[dict]] = None) -> List[Document]:
    docs = []
    meta = meta or [{}] * len(texts)
    for t, m in zip(texts, meta):
        docs.append(Document(content=t, meta=m))
    return docs


def index_texts(store: InMemoryDocumentStore, texts: List[str]) -> None:
    docs = make_documents(texts)
    pre = PreProcessor(split_length=256, split_overlap=32, split_by="word")
    processed = pre.process(docs)
    store.write_documents(processed)
    store.update_embeddings(retriever=BM25Retriever(store))


def build_qa_pipeline(store: InMemoryDocumentStore, model: str = "google/flan-t5-base") -> Pipeline:
    retriever = BM25Retriever(store)
    prompt_tmpl = PromptTemplate(
        name="qa",
        prompt_text=("Given the question and context, answer concisely.\n"
                     "Question: {query}\n"
                     "Context: {join(documents)}\n"
                     "Answer:")
    )
    node = PromptNode(model_name_or_path=model, default_prompt_template=prompt_tmpl, api_key=os.getenv("HF_TOKEN"))
    pipe = Pipeline()
    pipe.add_node(component=retriever, name="retriever", inputs=["Query"])
    pipe.add_node(component=node, name="llm", inputs=["retriever"])
    return pipe


def ask(pipe: Pipeline, question: str, top_k: int = 5) -> str:
    res = pipe.run(query=question, params={"retriever": {"top_k": top_k}})
    return res["results"][0] if "results" in res and res["results"] else ""
