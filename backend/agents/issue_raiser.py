import httpx
from langsmith import traceable

from backend.auth.github_auth import generate_jwt, get_installation_token
from backend.models.state import WorkflowState


@traceable(run_type="agent", name="raise_issues")
async def raise_issues(state: WorkflowState) -> WorkflowState:
    """Creates GitHub issues for detected bugs and returns their URLs."""
    owner, repo = state["repo_full_name"].split("/", 1)
    jwt_token = generate_jwt()
    installation_url = f"https://api.github.com/repos/{owner}/{repo}/installation"
    headers_jwt = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        installation_resp = await client.get(installation_url, headers=headers_jwt)
        installation_resp.raise_for_status()
        installation_payload = installation_resp.json()
        installation_id = int(installation_payload["id"])
        installation_token = await get_installation_token(installation_id)
        api_headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        issue_urls: list[str] = []
        for bug in state.get("bugs_found", []):
            file = str(bug.get("file", ""))
            line = int(bug.get("line", 0))
            severity = str(bug.get("severity", ""))
            description = str(bug.get("description", ""))
            suggested_fix = str(bug.get("suggested_fix", ""))
            title = f"[{severity or 'bug'}] {file}:{line}"
            body = (
                "## Bug detected by smart-pr-review-bot\n"
                f"**File:** {file}:{line}\n"
                f"**Severity:** {severity}\n"
                f"**Description:** {description}\n"
                f"**Suggested fix:** {suggested_fix}\n"
                "---\n"
                f"  *Auto-detected via RAG analysis of PR #{state['pr_number']}*\n"
            )
            create_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            payload = {
                "title": title,
                "body": body,
                "labels": ["bug", "ai-detected"],
                "assignees": [],
            }
            issue_resp = await client.post(create_url, headers=api_headers, json=payload)
            issue_resp.raise_for_status()
            issue_payload = issue_resp.json()
            issue_urls.append(str(issue_payload["html_url"]))
    updated = dict(state)
    updated["issues_raised"] = issue_urls
    updated["error"] = ""
    return updated
