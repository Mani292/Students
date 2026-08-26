import json
from typing import Optional
from urllib import error, request

from app.core.config import settings


class AIProvider:
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        raise NotImplementedError


class LocalFallbackProvider(AIProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        return None


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            req = request.Request(
                f"{self.base_url}/chat/completions",
                data=payload,
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=settings.AI_TIMEOUT_SECONDS) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (error.URLError, error.HTTPError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
            return None


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "glm":
        base_url = settings.AI_BASE_URL or "https://open.bigmodel.cn/api/paas/v4"
        return OpenAICompatibleProvider(base_url, settings.AI_API_KEY, settings.AI_MODEL)
    if provider in {"nvidia", "nvidia_nemo", "nemo"}:
        base_url = settings.AI_BASE_URL or "http://localhost:8001/v1"
        return OpenAICompatibleProvider(base_url, settings.AI_API_KEY, settings.AI_MODEL)
    return LocalFallbackProvider()