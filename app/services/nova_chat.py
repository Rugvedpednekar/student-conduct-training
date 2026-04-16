from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.services.knowledge_base import retrieve_relevant_context


SYSTEM_PROMPT = """You are the Student Conduct Training AI assistant.
You support students and Student Conduct Graduate Assistants.
Rules you must follow:
- Use only the provided training and handbook context.
- If the context is missing or uncertain, say you are unsure and tell the user to contact Student Conduct staff.
- Never invent policy details.
- Never present yourself as making disciplinary outcomes or official case decisions.
- Keep answers concise, professional, and calm.
"""


class NovaChatService:
    def __init__(self) -> None:
        self.api_key = settings.nova_api_key
        self.base_url = settings.nova_base_url.rstrip("/")
        self.model = settings.nova_model

    def _validate_config(self) -> None:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Missing NOVA_API_KEY for AI Chat.")
        if not self.model:
            raise HTTPException(status_code=500, detail="Missing NOVA_MODEL for AI Chat.")
        if not self.base_url:
            raise HTTPException(status_code=500, detail="Missing NOVA_BASE_URL for AI Chat.")

    @staticmethod
    def _normalize_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        for item in history[-10:]:
            role = item.get("role", "user")
            if role not in {"user", "assistant"}:
                continue
            text = (item.get("content") or "").strip()
            if not text:
                continue
            messages.append({"role": role, "content": text})
        return messages

    def ask(self, message: str, history: list[dict[str, str]]) -> tuple[str, list[str]]:
        self._validate_config()
        clean_message = message.strip()
        if not clean_message:
            raise HTTPException(status_code=400, detail="Message is required.")

        context, labels = retrieve_relevant_context(clean_message)
        if not context:
            raise HTTPException(
                status_code=500,
                detail="Knowledge sources are unavailable. Configure handbook and training content paths.",
            )

        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self._normalize_history(history))
        messages.append(
            {
                "role": "user",
                "content": (
                    "Use only the context below.\n\n"
                    f"Context:\n{context}\n\n"
                    f"Question: {clean_message}"
                ),
            }
        )

        request_payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 550,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions"

        try:
            with httpx.Client(timeout=25.0) as client:
                response = client.post(endpoint, json=request_payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="Nova API request timed out. Please try again.") from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="Unable to reach Nova API. Check NOVA_BASE_URL and network access.",
            ) from exc

        if response.status_code in {401, 403}:
            raise HTTPException(status_code=502, detail="Nova API key is invalid or unauthorized.")
        if response.status_code == 404:
            raise HTTPException(status_code=502, detail="Nova model or endpoint was not found. Check NOVA_MODEL and NOVA_BASE_URL.")
        if response.status_code >= 500:
            raise HTTPException(status_code=502, detail="Nova API is temporarily unavailable. Please try again shortly.")
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message") or error_data.get("detail")
            except ValueError:
                error_message = response.text.strip()
            raise HTTPException(status_code=502, detail=error_message or "Nova API rejected the request.")

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="Nova API returned an invalid JSON response.") from exc

        answer = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not answer:
            raise HTTPException(status_code=502, detail="Nova API returned an empty response.")

        return answer, labels
