import hashlib
import hmac
import time
from typing import Any

import httpx
import jwt

from backend.config import settings


def generate_jwt() -> str:
    """Generates a GitHub App JWT signed using RS256."""
    now = int(time.time())
    payload: dict[str, Any] = {
        "iat": now - 60,
        "exp": now + 600,
        "iss": str(settings.github_app_id),
    }
    token = jwt.encode(payload, settings.github_private_key, algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


async def get_installation_token(installation_id: int) -> str:
    """Fetches an installation access token using a freshly generated JWT."""
    jwt_token = generate_jwt()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
    return str(payload["token"])


def verify_webhook_signature(body: bytes, signature_header: str) -> bool:
    """Verifies the webhook signature using X-Hub-Signature-256."""
    if not signature_header.startswith("sha256="):
        return False
    provided = signature_header.removeprefix("sha256=")
    expected = hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(provided, expected)


async def get_github_headers(installation_id: int) -> dict[str, str]:
    """Creates GitHub API headers backed by an installation access token."""
    token = await get_installation_token(installation_id)
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
