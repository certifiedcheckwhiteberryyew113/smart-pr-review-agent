import asyncio
import os
import shutil
from pathlib import Path

import httpx
from langsmith import traceable

from backend.auth.github_auth import generate_jwt, get_installation_token
from backend.models.state import WorkflowState
from backend.rag.code_indexer import chunk_to_document, clone_repository, index_to_chroma, parse_with_treesitter


@traceable(run_type="agent", name="index_repository")
async def index_repository(state: WorkflowState) -> WorkflowState:
    """Indexes repository code with tree-sitter chunking into Chroma."""
    owner, repo = state["repo_full_name"].split("/", 1)
    jwt_token = generate_jwt()
    installation_url = f"https://api.github.com/repos/{owner}/{repo}/installation"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(installation_url, headers=headers)
        response.raise_for_status()
        payload = response.json()
    installation_id = int(payload["id"])
    installation_token = await get_installation_token(installation_id)
    repo_url = f"https://github.com/{owner}/{repo}.git"
    clone_dir = await asyncio.to_thread(clone_repository, repo_url, installation_token)
    temp_root = Path(clone_dir).parent
    documents = []
    try:
        for root, dirnames, filenames in os.walk(clone_dir):
            dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".venv", "venv", "dist", "build"}]
            for filename in filenames:
                if not filename.endswith((".py", ".js", ".ts")):
                    continue
                file_path = os.path.join(root, filename)
                chunks = parse_with_treesitter(file_path)
                for chunk in chunks:
                    documents.append(chunk_to_document(chunk))
        doc_ids = index_to_chroma(documents, state["repo_full_name"])
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
    updated = dict(state)
    updated["rag_context_ids"] = doc_ids
    updated["error"] = ""
    return updated
