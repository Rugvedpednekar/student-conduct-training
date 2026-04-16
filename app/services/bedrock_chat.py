from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import HTTPException

from app.services.knowledge_base import retrieve_relevant_context


SYSTEM_PROMPT = """You are the Student Conduct Training AI assistant.
You support students and Student Conduct Graduate Assistants.
Rules you must follow:
- Use only the provided training and handbook context.
- If the context is missing or uncertain, say you are unsure and tell the user to contact Student Conduct staff.
- Never invent policy details.
- Never present yourself as making disciplinary outcomes or official case decisions.
- Keep answers concise, professional, and calm.
- Do not add a separate Sources line if the application already shows source tags.
"""


class BedrockChatService:
    def __init__(self) -> None:
        self.api_key = os.getenv("NOVA_API_KEY")
        self.base_url = os.getenv("NOVA_BASE_URL", "https://nova.amazon.com/api")
        self.model = os.getenv("NOVA_MODEL", "amazon.nova-pro")

    def _validate_config(self) -> None:
        if not self.api_key:
            raise HTTPException(
                status_code=500,
                detail="Missing NOVA_API_KEY.",
            )

    @staticmethod
    def _normalize_history(history: list[dict[str, str]] | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        if not history:
            return messages

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
                detail="Knowledge sources are unavailable. Configure training and handbook content paths.",
            )

        messages = self._normalize_history(history)
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"User question: {clean_message}\n\n"
                    "Answer using only the context."
                ),
            }
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ],
            "temperature": 0.2,
            "max_tokens": 550,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"Nova API request failed: {response.text}",
                )

            data = response.json()
            answer = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if not answer:
                raise HTTPException(status_code=502, detail="Model returned an empty response.")

            return answer, labels

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Nova API network error: {exc}",
            ) from exc
