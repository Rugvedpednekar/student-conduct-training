from __future__ import annotations

import html
import re
from functools import lru_cache
from pathlib import Path

from app.config import settings

DEFAULT_TRAINING_FILES = [
    "case-handling.html",
    "hearing.html",
    "sanctions.html",
    "parent-letters.html",
    "responsibilities.html",
    "systems.html",
    "office-overview.html",
    "training-flow.html",
    "index.html",
]


class KnowledgeSource:
    def __init__(self, label: str, content: str):
        self.label = label
        self.content = content
        self.tokens = _tokenize(content)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9']+", text.lower()))


def _clean_html_to_text(raw_html: str) -> str:
    no_script = re.sub(r"<(script|style).*?>.*?</\1>", " ", raw_html, flags=re.S | re.I)
    without_tags = re.sub(r"<[^>]+>", " ", no_script)
    normalized = re.sub(r"\s+", " ", html.unescape(without_tags)).strip()
    return normalized


def _load_training_sources() -> list[KnowledgeSource]:
    training_dir = Path(settings.training_content_path)
    sources: list[KnowledgeSource] = []

    if not training_dir.exists():
        return sources

    for file_name in DEFAULT_TRAINING_FILES:
        file_path = training_dir / file_name
        if not file_path.exists():
            continue
        text = _clean_html_to_text(file_path.read_text(encoding="utf-8"))
        label = f"Training: {file_name.replace('.html', '').replace('-', ' ').title()}"
        sources.append(KnowledgeSource(label=label, content=text))

    return sources


def _load_handbook_text() -> str:
    handbook_path = Path(settings.handbook_path)
    if not handbook_path.exists():
        return ""

    if handbook_path.suffix.lower() in {".txt", ".md"}:
        return handbook_path.read_text(encoding="utf-8")

    if handbook_path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception:
            return ""
        reader = PdfReader(str(handbook_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    return handbook_path.read_text(encoding="utf-8")


def _build_sources() -> list[KnowledgeSource]:
    sources = _load_training_sources()
    handbook_text = _load_handbook_text()
    if handbook_text.strip():
        sources.append(KnowledgeSource(label="Student Handbook", content=handbook_text.strip()))
    return sources


@lru_cache(maxsize=1)
def get_knowledge_sources() -> list[KnowledgeSource]:
    return _build_sources()


def retrieve_relevant_context(query: str, max_sources: int = 4, max_chars: int = 3600) -> tuple[str, list[str]]:
    sources = get_knowledge_sources()
    if not sources:
        return "", []

    query_tokens = _tokenize(query)
    ranked: list[tuple[int, KnowledgeSource]] = []
    for source in sources:
        overlap = len(query_tokens.intersection(source.tokens))
        ranked.append((overlap, source))

    ranked.sort(key=lambda item: item[0], reverse=True)
    chosen = [item[1] for item in ranked[:max_sources] if item[0] > 0]
    if not chosen:
        chosen = ranked[:2]
        chosen = [item[1] for item in chosen]

    context_parts: list[str] = []
    labels: list[str] = []
    remaining = max_chars
    for source in chosen:
        snippet = source.content[: min(len(source.content), remaining)]
        context_parts.append(f"[{source.label}]\n{snippet}")
        labels.append(source.label)
        remaining -= len(snippet)
        if remaining <= 0:
            break

    return "\n\n".join(context_parts), labels
