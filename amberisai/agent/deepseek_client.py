"""
deepseek_client.py
==================
Handles AI API calls with streaming.
Auto-detects provider from API key:
  - sk-...   -> DeepSeek
  - gsk_...  -> Groq (FREE, no credit card needed)
"""
import requests
import logging
from typing import Generator

logger = logging.getLogger(__name__)


def detect_provider(api_key: str):
    if api_key.startswith("gsk_"):
        return "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"
    else:
        return "https://api.deepseek.com/v1", "deepseek-chat"


def validate_api_key(api_key: str) -> bool:
    return api_key and (api_key.startswith("sk-") or api_key.startswith("gsk_"))


def stream_deepseek(
    messages: list,
    api_key: str,
    model: str = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> Generator[str, None, None]:

    base_url, default_model = detect_provider(api_key)
    chosen_model = model or default_model

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True
    }

    try:
        with requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        ) as response:

            if response.status_code != 200:
                raise RuntimeError(response.text)

            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data = decoded[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue

    except Exception as e:
        logger.error(f"[DeepSeek] API error: {e}")
        raise
