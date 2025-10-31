from __future__ import annotations

import os
from typing import List, Optional, Dict, Any, Tuple

from haystack import Document, Pipeline
from haystack.nodes import BM25Retriever, PromptTemplate, PromptNode
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import PreProcessor


def build_document_store() -> InMemoryDocumentStore:
    # BM25 enabled store; no embeddings needed for this thesis setup
    return InMemoryDocumentStore(use_bm25=True)


def make_documents(texts: List[str], meta: Optional[List[dict]] = None) -> List[Document]:
    docs: List[Document] = []
    meta = meta or [{} for _ in range(len(texts))]
    for t, m in zip(texts, meta, strict=False):
        docs.append(Document(content=t, meta=m))
    return docs


def index_texts(
    store: InMemoryDocumentStore,
    texts: List[str],
    split_length: int = 256,
    split_overlap: int = 32,
    split_by: str = "word",
) -> None:
    docs = make_documents(texts)
    pre = PreProcessor(split_length=split_length, split_overlap=split_overlap, split_by=split_by)
    processed = pre.process(docs)
    store.write_documents(processed)
    store.update_embeddings(retriever=BM25Retriever(store))


def _make_prompt_node(
    model: str,
    api_key: Optional[str] = None,
    api_base_url: Optional[str] = None,
    model_kwargs: Optional[Dict[str, Any]] = None,
) -> PromptNode:
    """
    Create a PromptNode that can talk to Hugging Face Inference Endpoints (or local backends).
    Tested with Mixtral 8x7B Instruct on HF endpoints.
    """
    api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
    kwargs = dict(model_kwargs or {})
    # Sensible defaults for long answers but grounded, low temperature
    kwargs.setdefault("max_new_tokens", 512)
    kwargs.setdefault("temperature", 0.2)

    node = PromptNode(
        model_name_or_path=model,
        api_key=api_key,
        api_base_url=api_base_url,  # None uses provider default
        default_prompt_template=None,
        stop_words=None,
        model_kwargs=kwargs,
    )
    return node


def build_qa_pipeline(
    store: InMemoryDocumentStore,
    model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
    api_base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Pipeline:
    retriever = BM25Retriever(store)

    # Prompt that encourages citation-like grounding from retrieved snippets
    prompt_tmpl = PromptTemplate(
        name="cq_prompt",
        prompt_text=(
            "You are answering a biomedical competency question based ONLY on the provided context.\n"
            "Cite table/section identifiers when useful (e.g., 'TABLE 2', 'Section 3').\n"
            "Be concise, faithful, and state uncertainty when evidence is insufficient.\n"
            "Question: {query}\n"
            "Context:\n{join(documents)}\n\n"
            "Answer:"
        ),
    )

    node = _make_prompt_node(model=model, api_key=api_key, api_base_url=api_base_url)
    node.default_prompt_template = prompt_tmpl

    pipe = Pipeline()
    pipe.add_node(component=retriever, name="retriever", inputs=["Query"])
    pipe.add_node(component=node, name="llm", inputs=["retriever"])
    return pipe


def ask(pipe: Pipeline, question: str, top_k: int = 5) -> Tuple[str, List[Document]]:
    res = pipe.run(query=question, params={"retriever": {"top_k": top_k}})
    answer = ""
    if "results" in res and res["results"]:
        answer = res["results"][0]
    # Get the actual retrieved docs for downstream logging/eval
    ctx_docs = res.get("documents", [])
    return answer, ctx_docs  # type: ignore[return-value]
