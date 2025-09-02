"""
Azure Responses API adapter
===========================

Lightweight utility to call Azure OpenAI Responses API using the official
OpenAI Python client in a way that's compatible with our SK plugin flow.

This allows using reasoning-capable deployments (e.g., gpt-5) via the
"/openai/v1/responses" endpoint when AZURE_OPENAI_USE_RESPONSES=true.

Notes
- Expects base_url like: https://<resource>.openai.azure.com/openai/v1/
- Uses deployment name for the "model" field per Azure docs
- Returns plain output_text string, or empty string on error
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

try:
    # OpenAI v1 client (present in uv.lock)
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional import guard
    OpenAI = None  # type: ignore

logger = logging.getLogger(__name__)


class AzureResponsesClient:
    """Thin wrapper around OpenAI client configured for Azure Responses API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
        # Accept either resource root or full /openai/v1/ and normalize
        endpoint = base_url or os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        if endpoint:
            # Normalize trailing slash
            if not endpoint.endswith("/"):
                endpoint = endpoint + "/"
            # Ensure it ends with /openai/v1/
            low = endpoint.lower()
            if low.endswith("/openai/v1/"):
                pass
            elif low.endswith("/openai/"):
                endpoint = endpoint + "v1/"
            elif low.endswith("/openai"):
                endpoint = endpoint + "/v1/"
            elif "/openai/" not in low:
                endpoint = endpoint.rstrip("/") + "/openai/v1/"

        self.base_url = endpoint
        # Prefer specialized env var, then deployment name, then model
        self.model = (
            model
            or os.getenv("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME")
            or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            or os.getenv("AZURE_OPENAI_DEPLOYMENT")
            or os.getenv("AZURE_OPENAI_MODEL")
        )

        self._client = None
        if OpenAI is not None and self.api_key and self.base_url:
            try:
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as e:  # pragma: no cover
                logger.warning(
                    f"Failed to initialize OpenAI client for Azure Responses: {e}"
                )

    def is_ready(self) -> bool:
        return bool(self._client and self.model)

    def create_text_response(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        reasoning: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Synchronous call to Responses API; returns output_text or ''."""
        if not self.is_ready():
            return ""
        try:
            # The Responses API uses max_output_tokens. Temperature is supported.
            # Cast model to str to satisfy typing in the OpenAI client
            create_args: Dict[str, Any] = {
                "model": str(self.model),
                "input": prompt,
                "temperature": float(temperature),
                "max_output_tokens": int(max_tokens) if max_tokens else None,
            }
            # Attach reasoning configuration when provided (gpt-5 / O-series)
            if reasoning:
                create_args["reasoning"] = reasoning

            resp = self._client.responses.create(**create_args)  # type: ignore[attr-defined]
            # Prefer output_text; fallback to first output item text
            text = getattr(resp, "output_text", None)
            if text:
                return str(text)
            # Fallback: assemble from output list
            outputs = getattr(resp, "output", None) or []
            for item in outputs:
                if getattr(item, "type", "") in {"message", "output_text"}:
                    # item.content may be a list of segments
                    content = getattr(item, "content", None)
                    if isinstance(content, list) and content:
                        seg = content[0]
                        seg_text = getattr(seg, "text", None)
                        if seg_text:
                            return str(seg_text)
            return ""
        except Exception as e:
            logger.error(f"Azure Responses API call failed: {e}")
            return ""

    async def acreate_text_response(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        reasoning: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Async wrapper using a thread to avoid blocking the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.create_text_response(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                reasoning=reasoning,
            ),
        )


def use_responses_api() -> bool:
    """Check env flag to route calls to Responses API."""
    return os.getenv("AZURE_OPENAI_USE_RESPONSES", "false").lower() in {
        "1",
        "true",
        "yes",
    }


def get_reasoning_config_from_env() -> Optional[Dict[str, Any]]:
    """Build a reasoning config from env vars if present.

    Supported env vars:
      - AZURE_OPENAI_REASONING_EFFORT: one of low|medium|high
      - AZURE_OPENAI_REASONING_SUMMARY: set to 'detailed' to request summaries (if supported)
    """
    effort = os.getenv("AZURE_OPENAI_REASONING_EFFORT", "").strip().lower()
    summary = os.getenv("AZURE_OPENAI_REASONING_SUMMARY", "").strip().lower()
    reasoning: Dict[str, Any] = {}
    if effort in {"low", "medium", "high"}:
        reasoning["effort"] = effort
    if summary in {"detailed"}:
        reasoning["summary"] = summary
    return reasoning or None


async def chat_text_via_responses(
    prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    reasoning: Optional[Dict[str, Any]] = None,
) -> str:
    """Convenience async function to fetch a text response via Responses API."""
    client = AzureResponsesClient()
    if not client.is_ready():
        return ""
    return await client.acreate_text_response(
        prompt, temperature=temperature, max_tokens=max_tokens, reasoning=reasoning
    )
