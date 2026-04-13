from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_FORM_TEMPLATE_ID = "varsayilan"
DEFAULT_FORM_TEMPLATE_NAME = "Varsayılan"
FORMAT_FILE_GLOB = "*.fmt"
SLUG_SAFE_RE = re.compile(r"[^a-z0-9]+")
TR_ASCII_MAP = str.maketrans(
    {
        "ç": "c",
        "Ç": "C",
        "ğ": "g",
        "Ğ": "G",
        "ı": "i",
        "İ": "I",
        "ö": "o",
        "Ö": "O",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
    }
)


def slugify_form_template_name(value: str | None) -> str:
    text = str(value or "").strip().translate(TR_ASCII_MAP)
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = SLUG_SAFE_RE.sub("-", ascii_text.lower()).strip("-")
    return slug or DEFAULT_FORM_TEMPLATE_ID


def default_form_template() -> dict[str, Any]:
    return {
        "id": DEFAULT_FORM_TEMPLATE_ID,
        "name": DEFAULT_FORM_TEMPLATE_NAME,
        "file_name": "Varsayılan.fmt",
        "is_default": True,
        "line_count": 0,
        "preview": [],
    }


def list_form_templates(project_root: Path) -> list[dict[str, Any]]:
    format_dir = project_root / "optik_kagit_formatlari"
    if not format_dir.exists():
        return [default_form_template()]

    templates: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for file_path in sorted(format_dir.glob(FORMAT_FILE_GLOB), key=lambda item: item.name.lower()):
        template_id = slugify_form_template_name(file_path.stem)
        candidate_id = template_id
        suffix = 2
        while candidate_id in used_ids:
            candidate_id = f"{template_id}-{suffix}"
            suffix += 1
        used_ids.add(candidate_id)

        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        preview_lines = [line.strip() for line in raw_text.splitlines() if line.strip()][:3]
        templates.append(
            {
                "id": candidate_id,
                "name": file_path.stem,
                "file_name": file_path.name,
                "is_default": candidate_id == DEFAULT_FORM_TEMPLATE_ID,
                "line_count": len(raw_text.splitlines()),
                "preview": preview_lines,
            }
        )

    if not templates:
        return [default_form_template()]

    templates.sort(key=lambda item: (not item["is_default"], str(item["name"]).lower()))
    if not any(item["is_default"] for item in templates):
        templates.insert(0, default_form_template())
    return templates


def resolve_form_template(form_template_id: str | None, catalog: list[dict[str, Any]]) -> dict[str, Any]:
    if not catalog:
        return default_form_template()

    normalized_id = slugify_form_template_name(form_template_id)
    for item in catalog:
        if item["id"] == normalized_id:
            return item

    for item in catalog:
        if item.get("is_default"):
            return item

    return catalog[0]