from __future__ import annotations

from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
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
- Include a brief source line at the end in this format: Sources: <labels>
"""


class BedrockChatService:
    def __init__(self) -> None:
        self.region = settings.aws_region or settings.aws_default_region
        self.model_id = settings.bedrock_model_id

    def _validate_config(self) -> None:
        if not self.region:
            raise HTTPException(
                status_code=500,
                detail="Missing AWS region. Set AWS_REGION or AWS_DEFAULT_REGION.",
            )
        if not self.model_id:
            raise HTTPException(status_code=500, detail="Missing model ID. Set BEDROCK_MODEL_ID.")

    def _client(self):
        self._validate_config()
        try:
            return boto3.client("bedrock-runtime", region_name=self.region)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Could not initialize Bedrock client: {exc}") from exc

    @staticmethod
    def _normalize_history(history: list[dict[str, str]]) -> list[dict[str, Any]]:
        messages = []
        for item in history[-10:]:
            role = item.get("role", "user")
            if role not in {"user", "assistant"}:
                continue
            text = (item.get("content") or "").strip()
            if not text:
                continue
            messages.append({"role": role, "content": [{"text": text}]})
        return messages

    def ask(self, message: str, history: list[dict[str, str]]) -> tuple[str, list[str]]:
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
                "content": [
                    {
                        "text": (
                            f"Context:\n{context}\n\n"
                            f"User question: {clean_message}\n\n"
                            "Answer using only the context."
                        )
                    }
                ],
            }
        )

        client = self._client()

        try:
            response = client.converse(
                modelId=self.model_id,
                system=[{"text": SYSTEM_PROMPT}],
                messages=messages,
                inferenceConfig={
                    "temperature": 0.2,
                    "topP": 0.9,
                    "maxTokens": 550,
                },
            )
            output_message = response["output"]["message"]["content"]
            text_parts = [chunk.get("text", "") for chunk in output_message if "text" in chunk]
            answer = "\n".join(part for part in text_parts if part).strip()
            if not answer:
                raise HTTPException(status_code=502, detail="Model returned an empty response.")
            return answer, labels
        except NoCredentialsError as exc:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials are not configured. Set credentials in environment variables.",
            ) from exc
        except (ClientError, BotoCoreError) as exc:
            raise HTTPException(status_code=502, detail=f"Bedrock request failed: {exc}") from exc
