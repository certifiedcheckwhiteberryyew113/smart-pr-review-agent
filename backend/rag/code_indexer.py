from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langsmith import traceable

from backend.config import settings


@traceable(run_type="tool", name="clone_repository")
def clone_repository(repo_url: str, token: str) -> str:
    """Clones a repository into a temporary directory using git."""
    temp_dir = tempfile.mkdtemp(prefix="pr_index_repo_")
    clone_dir = os.path.join(temp_dir, "repo")
    auth_url = repo_url
    if token and repo_url.startswith("https://"):
        auth_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
    subprocess.run(["git", "clone", "--depth", "1", auth_url, clone_dir], check=True)
    return clone_dir


def _language_for_path(file_path: str) -> str:
    """Infers a tree-sitter language key from a file extension."""
    lower = file_path.lower()
    if lower.endswith(".py"):
        return "python"
    if lower.endswith(".ts") or lower.endswith(".js"):
        return "javascript"
    return "unknown"


def _load_source_bytes(file_path: str) -> bytes:
    """Reads source bytes from disk with tolerant error handling."""
    return Path(file_path).read_bytes()


def parse_with_treesitter(file_path: str) -> list[dict[str, Any]]:
    """Parses function and class level chunks using tree-sitter."""
    language_key = _language_for_path(file_path)
    if language_key == "unknown":
        return []
    try:
        from tree_sitter import Parser
        from tree_sitter_javascript import language as javascript_language
        from tree_sitter_python import language as python_language
    except ImportError:
        return []
    parser = Parser()
    if language_key == "python":
        parser.set_language(python_language())
    else:
        parser.set_language(javascript_language())
    source_bytes = _load_source_bytes(file_path)
    tree = parser.parse(source_bytes)
    root = tree.root_node
    chunks: list[dict[str, Any]] = []

    def _emit(node: Any, function_name: str) -> None:
        """Emits a function/class chunk into the in-memory list."""
        text = source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")
        chunks.append(
            {
                "file_path": file_path,
                "function_name": function_name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "chunk_text": text,
            }
        )

    def _walk(node: Any) -> None:
        """Walks the syntax tree and emits matching nodes."""
        if language_key == "python":
            if node.type in {"function_definition", "class_definition"}:
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf-8", errors="ignore") if name_node else "unknown"
                _emit(node, name)
        else:
            if node.type in {"function_declaration", "class_declaration", "method_definition"}:
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf-8", errors="ignore") if name_node else "unknown"
                _emit(node, name)
        for child in node.children:
            _walk(child)

    _walk(root)
    return chunks


def chunk_to_document(chunk: dict[str, Any]) -> Document:
    """Converts a parsed chunk into a LangChain Document with metadata."""
    return Document(
        page_content=str(chunk.get("chunk_text", "")),
        metadata={
            "file": str(chunk.get("file_path", "")),
            "function_name": str(chunk.get("function_name", "unknown")),
            "start_line": int(chunk.get("start_line", 0)),
            "end_line": int(chunk.get("end_line", 0)),
        },
    )


@traceable(run_type="tool", name="index_to_chroma")
def index_to_chroma(documents: list[Document], repo_name: str) -> list[str]:
    """Embeds and indexes documents into Chroma under a repo collection."""
    from chromadb import PersistentClient

    safe_name = repo_name.replace("/", "__")
    collection_name = safe_name
    client = PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(name=collection_name)
    embeddings = OpenAIEmbeddings(api_key=settings.langchain_api_key)
    ids: list[str] = []
    metadatas: list[dict[str, Any]] = []
    for doc in documents:
        file = str(doc.metadata.get("file", ""))
        start_line = int(doc.metadata.get("start_line", 0))
        end_line = int(doc.metadata.get("end_line", 0))
        fn = str(doc.metadata.get("function_name", "unknown"))
        raw_id = f"{collection_name}:{file}:{fn}:{start_line}:{end_line}:{doc.page_content[:200]}"
        ids.append(hashlib.sha256(raw_id.encode("utf-8")).hexdigest())
        metadatas.append(dict(doc.metadata))
    texts = [doc.page_content for doc in documents]
    vectors = embeddings.embed_documents(texts) if texts else []
    if ids:
        collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=vectors)
    return ids


def search_codebase(query: str, repo_name: str, k: int = 5) -> list[Document]:
    """Searches a repo collection for the top-k relevant chunks."""
    from chromadb import PersistentClient

    safe_name = repo_name.replace("/", "__")
    collection_name = safe_name
    client = PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_collection(name=collection_name)
    embeddings = OpenAIEmbeddings(api_key=settings.langchain_api_key)
    query_vector = embeddings.embed_query(query)
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    documents: list[Document] = []
    docs_by_rank = result.get("documents", [[]])
    metas_by_rank = result.get("metadatas", [[]])
    for doc_text, meta in zip(docs_by_rank[0], metas_by_rank[0] if metas_by_rank else []):
        documents.append(Document(page_content=str(doc_text), metadata=dict(meta or {})))
    return documents

