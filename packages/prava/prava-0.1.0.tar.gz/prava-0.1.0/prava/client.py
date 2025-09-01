import os
import json
import typing as t
from dataclasses import dataclass

import requests


DEFAULT_BASE_URL = os.getenv("PRAVA_BASE_URL", "https://api.prava.ai/v1").rstrip("/")


class APIError(RuntimeError):
    def __init__(self, status: int, message: str, data: t.Any | None = None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.data = data


def _request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: t.Any | None = None,
    timeout: int = 60,
) -> t.Any:
    resp = requests.request(method, url, headers=headers, json=json_body, timeout=timeout)
    text = resp.text or ""
    data: t.Any | None = None
    try:
        data = json.loads(text) if text else None
    except Exception:
        data = None
    if not resp.ok:
        message = (data or {}).get("error", {}).get("message") or (data or {}).get("message") or resp.reason
        raise APIError(resp.status_code, message, data)
    return data


@dataclass
class _ChatCompletions:
    api_key: str
    base_url: str
    timeout: int

    def create(self, body: dict) -> dict:
        """Create a chat completion.

        Args:
            body: Request body. Keys mirror OpenAI's shape.
        Returns:
            Parsed JSON response as dict.
        """
        return _request_json(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {self.api_key}",
            },
            json_body=body,
            timeout=self.timeout,
        )


class _ChatNamespace:
    def __init__(self, completions: _ChatCompletions):
        self.completions = completions


class Prava:
    """Prava API client.

    Example:
        >>> from prava import Prava
        >>> client = Prava()
        >>> client.chat.completions.create({"model": "x", "messages": []})
    """

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None, timeout: int = 60):
        api_key = api_key or os.getenv("PRAVA_API_KEY")
        if not api_key:
            raise ValueError("Missing API key: pass api_key or set PRAVA_API_KEY")
        base = (base_url or DEFAULT_BASE_URL).rstrip("/")

        self.api_key = api_key
        self.base_url = base
        self.timeout = int(timeout)

        self.chat = _ChatNamespace(
            _ChatCompletions(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        )

