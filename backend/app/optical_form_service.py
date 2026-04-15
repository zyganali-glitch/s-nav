from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .exam_service import (
    build_answer_key_profile,
    has_explicit_canonical_mapping_evidence,
    has_explicit_weight_evidence,
    normalize_answer,
    normalize_token,
)
from .form_template_service import list_form_templates, resolve_form_template, slugify_form_template_name


class SynthesisPartialResult(ValueError):
    """Count mismatch — partial questions up to min_count are available."""

    def __init__(self, message: str, questions: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.questions = questions


EXPLICIT_TEMPLATE_COORDINATE_ALIASES = {
    "bsr-katipcelebi-snf": "katipcelebi",
}

TURKISH_ALPHABET_FULL = "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZ"
TURKISH_ALPHABET_COMPACT = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
REPLACEMENT_CHAR = "�"
TEXT_FIELD_NAMES = {"student_name", "student_surname"}
AUTO_REVERSE_FIELD_NAMES = TEXT_FIELD_NAMES
SOFT_SINGLE_AUXILIARY_FIELD_NAMES = {
    "student_number",
    "class_number",
    "exam_date_day",
    "exam_date_month",
    "exam_date_year",
}
EXPLICIT_METADATA_SOURCES = {"explicit", "manual", "profile", "copied-profile"}

EXPLICIT_TEMPLATE_COORDINATE_SOURCES: dict[str, dict[str, Any]] = {
    "varsayilan": {
        "booklet_region": {
            "name": "booklet_code",
            "start_row": 37,
            "end_row": 37,
            "start_column": 36,
            "end_column": 42,
            "axis": "Y",
            "normalized_choices": "DCBA",
        },
        "named_fields": [
            {
                "name": "student_number",
                "start_row": 23,
                "end_row": 32,
                "start_column": 35,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "0123456789",
            },
            {
                "name": "class_number",
                "start_row": 23,
                "end_row": 32,
                "start_column": 31,
                "end_column": 34,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_code_prefix",
                "start_row": 44,
                "end_row": 53,
                "start_column": 45,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "ABCDEFGHIJ",
                "virtual": True,
            },
            {
                "name": "exam_code_number",
                "start_row": 44,
                "end_row": 53,
                "start_column": 42,
                "end_column": 44,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_day",
                "start_row": 44,
                "end_row": 53,
                "start_column": 39,
                "end_column": 40,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_month",
                "start_row": 44,
                "end_row": 53,
                "start_column": 37,
                "end_column": 38,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_year",
                "start_row": 44,
                "end_row": 53,
                "start_column": 33,
                "end_column": 36,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "student_surname",
                "start_row": 2,
                "end_row": 33,
                "start_column": 6,
                "end_column": 15,
                "axis": "D",
            },
            {
                "name": "student_name",
                "start_row": 2,
                "end_row": 33,
                "start_column": 19,
                "end_column": 28,
                "axis": "D",
            }
        ],
        "answer_regions": [
            {
                "name": "answer_block_1",
                "start_row": 36,
                "end_row": 65,
                "start_column": 26,
                "end_column": 30,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_2",
                "start_row": 36,
                "end_row": 65,
                "start_column": 20,
                "end_column": 24,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_3",
                "start_row": 36,
                "end_row": 65,
                "start_column": 14,
                "end_column": 18,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_4",
                "start_row": 36,
                "end_row": 45,
                "start_column": 8,
                "end_column": 12,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
        ],
    },
    "katipcelebi": {
        "booklet_region": {
            "name": "booklet_code",
            "start_row": 37,
            "end_row": 37,
            "start_column": 37,
            "end_column": 41,
            "axis": "Y",
            "normalized_choices": "CBA",
        },
        "named_fields": [
            {
                "name": "student_number",
                "start_row": 23,
                "end_row": 32,
                "start_column": 35,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "0123456789",
            },
            {
                "name": "class_number",
                "start_row": 23,
                "end_row": 32,
                "start_column": 31,
                "end_column": 34,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_code_prefix",
                "start_row": 44,
                "end_row": 53,
                "start_column": 45,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "ABCDEFGHIJ",
                "virtual": True,
            },
            {
                "name": "exam_code_number",
                "start_row": 44,
                "end_row": 53,
                "start_column": 42,
                "end_column": 44,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_day",
                "start_row": 44,
                "end_row": 53,
                "start_column": 39,
                "end_column": 40,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_month",
                "start_row": 44,
                "end_row": 53,
                "start_column": 37,
                "end_column": 38,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_year",
                "start_row": 44,
                "end_row": 53,
                "start_column": 33,
                "end_column": 36,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "student_surname",
                "start_row": 2,
                "end_row": 33,
                "start_column": 6,
                "end_column": 15,
                "axis": "D",
            },
            {
                "name": "student_name",
                "start_row": 2,
                "end_row": 33,
                "start_column": 19,
                "end_column": 28,
                "axis": "D",
            }
        ],
        "answer_regions": [
            {
                "name": "answer_block_1",
                "start_row": 36,
                "end_row": 65,
                "start_column": 26,
                "end_column": 30,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_2",
                "start_row": 36,
                "end_row": 65,
                "start_column": 20,
                "end_column": 24,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_3",
                "start_row": 36,
                "end_row": 65,
                "start_column": 14,
                "end_column": 18,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_4",
                "start_row": 36,
                "end_row": 45,
                "start_column": 8,
                "end_column": 12,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
        ],
    },
    "katipcelebi63": {
        "booklet_region": {
            "name": "booklet_code",
            "start_row": 35,
            "end_row": 35,
            "start_column": 37,
            "end_column": 41,
            "axis": "Y",
            "normalized_choices": "CBA",
        },
        "named_fields": [
            {
                "name": "student_number",
                "start_row": 21,
                "end_row": 30,
                "start_column": 35,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "0123456789",
            },
            {
                "name": "class_number",
                "start_row": 23,
                "end_row": 32,
                "start_column": 31,
                "end_column": 34,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_code_prefix",
                "start_row": 44,
                "end_row": 53,
                "start_column": 45,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "ABCDEFGHIJ",
                "virtual": True,
            },
            {
                "name": "exam_code_number",
                "start_row": 44,
                "end_row": 53,
                "start_column": 42,
                "end_column": 44,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_day",
                "start_row": 44,
                "end_row": 53,
                "start_column": 39,
                "end_column": 40,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_month",
                "start_row": 44,
                "end_row": 53,
                "start_column": 37,
                "end_column": 38,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "exam_date_year",
                "start_row": 44,
                "end_row": 53,
                "start_column": 33,
                "end_column": 36,
                "axis": "D",
                "normalized_choices": "0123456789",
                "virtual": True,
                "reverse_columns": True,
            },
            {
                "name": "student_surname",
                "start_row": 2,
                "end_row": 33,
                "start_column": 6,
                "end_column": 15,
                "axis": "D",
            },
            {
                "name": "student_name",
                "start_row": 2,
                "end_row": 33,
                "start_column": 19,
                "end_column": 28,
                "axis": "D",
            }
        ],
        "answer_regions": [
            {
                "name": "answer_block_1",
                "start_row": 34,
                "end_row": 63,
                "start_column": 26,
                "end_column": 30,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_2",
                "start_row": 34,
                "end_row": 63,
                "start_column": 20,
                "end_column": 24,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_3",
                "start_row": 34,
                "end_row": 63,
                "start_column": 14,
                "end_column": 18,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_4",
                "start_row": 34,
                "end_row": 43,
                "start_column": 8,
                "end_column": 12,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
        ],
    },
    "katipcelebi7-1": {
        "booklet_region": {
            "name": "booklet_code",
            "start_row": 17,
            "end_row": 17,
            "start_column": 37,
            "end_column": 41,
            "axis": "Y",
            "normalized_choices": "CBA",
        },
        "named_fields": [
            {
                "name": "student_number",
                "start_row": 21,
                "end_row": 30,
                "start_column": 35,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "0123456789",
            }
        ],
        "answer_regions": [
            {
                "name": "answer_block_1",
                "start_row": 34,
                "end_row": 63,
                "start_column": 38,
                "end_column": 42,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_2",
                "start_row": 34,
                "end_row": 63,
                "start_column": 32,
                "end_column": 36,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_3",
                "start_row": 34,
                "end_row": 63,
                "start_column": 26,
                "end_column": 30,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_4",
                "start_row": 34,
                "end_row": 63,
                "start_column": 20,
                "end_column": 24,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_5",
                "start_row": 34,
                "end_row": 63,
                "start_column": 14,
                "end_column": 18,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_6",
                "start_row": 34,
                "end_row": 63,
                "start_column": 8,
                "end_column": 12,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_7",
                "start_row": 34,
                "end_row": 63,
                "start_column": 2,
                "end_column": 6,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
        ],
    },
    "katipcel-tip": {
        "booklet_region": {
            "name": "booklet_code",
            "start_row": 17,
            "end_row": 17,
            "start_column": 37,
            "end_column": 41,
            "axis": "Y",
            "normalized_choices": "CBA",
        },
        "named_fields": [
            {
                "name": "student_number",
                "start_row": 21,
                "end_row": 30,
                "start_column": 35,
                "end_column": 45,
                "axis": "D",
                "normalized_choices": "0123456789",
            }
        ],
        "answer_regions": [
            {
                "name": "answer_block_1",
                "start_row": 34,
                "end_row": 63,
                "start_column": 38,
                "end_column": 42,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_2",
                "start_row": 34,
                "end_row": 63,
                "start_column": 32,
                "end_column": 36,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_3",
                "start_row": 34,
                "end_row": 63,
                "start_column": 26,
                "end_column": 30,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_4",
                "start_row": 34,
                "end_row": 63,
                "start_column": 20,
                "end_column": 24,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_5",
                "start_row": 34,
                "end_row": 63,
                "start_column": 14,
                "end_column": 18,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_6",
                "start_row": 34,
                "end_row": 63,
                "start_column": 8,
                "end_column": 12,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
            {
                "name": "answer_block_7",
                "start_row": 34,
                "end_row": 63,
                "start_column": 2,
                "end_column": 6,
                "axis": "Y",
                "normalized_choices": "EDCBA",
            },
        ],
    },
}

EXPLICIT_TEMPLATE_COORDINATE_SOURCES["bsr-katipcelebi-snf"] = deepcopy(
    EXPLICIT_TEMPLATE_COORDINATE_SOURCES["katipcelebi"]
)
EXPLICIT_TEMPLATE_COORDINATE_SOURCES["bsr-katipcelebi-snf"]["named_fields"] = [
    {
        "name": "student_number",
        "start_row": 23,
        "end_row": 32,
        "start_column": 34,
        "end_column": 45,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "class_number",
        "start_row": 23,
        "end_row": 32,
        "start_column": 31,
        "end_column": 34,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "exam_code_prefix",
        "start_row": 44,
        "end_row": 53,
        "start_column": 45,
        "end_column": 45,
        "axis": "D",
        "normalized_choices": "ABCDEFGHIJ",
        "virtual": True,
    },
    {
        "name": "exam_code_number",
        "start_row": 44,
        "end_row": 53,
        "start_column": 42,
        "end_column": 44,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "exam_date_day",
        "start_row": 45,
        "end_row": 54,
        "start_column": 33,
        "end_column": 34,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "exam_date_month",
        "start_row": 46,
        "end_row": 55,
        "start_column": 33,
        "end_column": 34,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "exam_date_year",
        "start_row": 44,
        "end_row": 53,
        "start_column": 33,
        "end_column": 36,
        "axis": "D",
        "normalized_choices": "0123456789",
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "student_surname",
        "start_row": 2,
        "end_row": 33,
        "start_column": 8,
        "end_column": 16,
        "axis": "D",
        "pattern": TURKISH_ALPHABET_FULL,
        "virtual": True,
        "reverse_columns": True,
    },
    {
        "name": "student_name",
        "start_row": 2,
        "end_row": 33,
        "start_column": 21,
        "end_column": 30,
        "axis": "D",
        "pattern": TURKISH_ALPHABET_FULL,
        "virtual": True,
        "reverse_columns": True,
    },
]


def decode_template_text(file_path: Path) -> str:
    blob = file_path.read_bytes()
    for encoding in ("utf-8", "cp1254", "latin-1"):
        try:
            return blob.decode(encoding)
        except UnicodeDecodeError:
            continue
    return blob.decode("utf-8", errors="replace")


def repair_pattern_text(pattern: str) -> str:
    if REPLACEMENT_CHAR not in pattern:
        return pattern

    stripped_pattern = "".join(character for character in pattern if character.strip())
    candidates = [
        TURKISH_ALPHABET_FULL,
        TURKISH_ALPHABET_COMPACT,
    ]
    for candidate in candidates:
        if len(stripped_pattern) != len(candidate):
            continue
        if all(
            source == REPLACEMENT_CHAR or source == target
            for source, target in zip(stripped_pattern, candidate)
        ):
            rebuilt: list[str] = []
            candidate_index = 0
            for character in pattern:
                if not character.strip():
                    rebuilt.append(character)
                    continue
                rebuilt.append(candidate[candidate_index])
                candidate_index += 1
            return "".join(rebuilt)
    return pattern


def normalize_decoded_text(value: str) -> str:
    normalized = str(value or "").strip().upper()
    return "".join(character for character in normalized if character.isalnum() or character in "ÇĞİÖŞÜ")


def normalize_decoded_field_value(field_name: str, value: str) -> str:
    if field_name in {"student_number", "class_number", "exam_date", "exam_date_day", "exam_date_month", "exam_date_year", "exam_code_number"}:
        return "".join(character for character in str(value or "") if character.isdigit())
    if field_name in TEXT_FIELD_NAMES | {"class_section", "student_full_name", "classroom", "exam_code", "exam_code_prefix"}:
        return normalize_decoded_text(value)
    return normalize_token(value)


def format_exam_date_value(value: str) -> str:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if len(digits) == 8:
        return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"
    return digits


def normalize_exam_date_parts(day: str, month: str, year: str) -> str:
    normalized_day = "".join(character for character in str(day or "") if character.isdigit())[:2].zfill(2)
    normalized_month = "".join(character for character in str(month or "") if character.isdigit())[:2].zfill(2)
    normalized_year = "".join(character for character in str(year or "") if character.isdigit())[:4].zfill(4)
    return f"{normalized_day}.{normalized_month}.{normalized_year}"


def is_plausible_exam_date(day: str, month: str, year: str) -> bool:
    day_value = int(day)
    month_value = int(month)
    year_value = int(year)
    if not 1 <= day_value <= 31:
        return False
    if not 1 <= month_value <= 12:
        return False
    if not 1900 <= year_value <= 2100:
        return False
    return True


def decode_single_with_soft_threshold(
    values: list[int],
    tokens: list[str],
    threshold: int,
    allow_soft_single: bool = True,
) -> tuple[str, str]:
    def has_adjacent_ambiguity(ranked_entries: list[tuple[int, str, int]], competitor_floor: int) -> bool:
        if len(ranked_entries) < 2:
            return False
        top_value, _, top_index = ranked_entries[0]
        second_value, _, second_index = ranked_entries[1]
        if second_value < competitor_floor:
            return False
        if abs(top_index - second_index) != 1:
            return False
        return top_value - second_value <= 1

    hits = [token for token, value in zip(tokens, values) if token and value >= threshold]
    if len(hits) == 1:
        ranked = sorted(
            ((value, token, index) for index, (token, value) in enumerate(zip(tokens, values)) if token),
            key=lambda item: item[0],
            reverse=True,
        )
        if has_adjacent_ambiguity(ranked, max(1, threshold - 1)):
            return "", "adjacent_ambiguous"
        return hits[0], "single"
    if len(hits) > 1:
        return "", "multiple"

    ranked = sorted(
        ((value, token, index) for index, (token, value) in enumerate(zip(tokens, values)) if token),
        key=lambda item: item[0],
        reverse=True,
    )
    if not ranked:
        return "", "blank"

    top_value, top_token, _ = ranked[0]
    second_value = ranked[1][0] if len(ranked) > 1 else 0
    if not allow_soft_single:
        return "", "blank"

    soft_threshold = max(1, threshold - 2)
    if (
        top_value >= soft_threshold
        and top_value - second_value >= 2
        and sum(1 for value, _, _ in ranked if value == top_value) == 1
    ):
        if has_adjacent_ambiguity(ranked, soft_threshold):
            return "", "adjacent_ambiguous"
        return top_token, "soft_single"

    return "", "blank"


def relaxed_candidate_is_safe(base_candidate: dict[str, Any], relaxed_candidate: dict[str, Any]) -> bool:
    base_answers = base_candidate.get("answers") or {}
    relaxed_answers = relaxed_candidate.get("answers") or {}
    for position, base_answer in base_answers.items():
        relaxed_answer = relaxed_answers.get(position)
        if relaxed_answer and relaxed_answer != base_answer:
            return False

    base_booklet = normalize_token(base_candidate.get("booklet_code"))
    relaxed_booklet = normalize_token(relaxed_candidate.get("booklet_code"))
    if base_booklet and relaxed_booklet and base_booklet != relaxed_booklet:
        return False

    adds_missing_answers = len(relaxed_answers) > len(base_answers)
    fills_missing_booklet = not base_booklet and bool(relaxed_booklet)
    return adds_missing_answers or fills_missing_booklet


def parse_form_template(project_root: Path, template_id: str | None) -> dict[str, Any]:
    catalog = list_form_templates(project_root)
    selected = resolve_form_template(template_id, catalog)
    file_name = selected.get("file_name")
    if not file_name:
        raise ValueError("Secilen optik format dosyasi bulunamadi.")

    file_path = project_root / "optik_kagit_formatlari" / file_name
    if not file_path.exists():
        raise ValueError(f"Optik format dosyasi bulunamadi: {file_path.name}")

    lines = [line.strip() for line in decode_template_text(file_path).splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"Optik format dosyasi bos: {file_path.name}")

    header = lines[0].split("=")
    if len(header) < 2:
        raise ValueError(f"Optik format basligi ayrisamadi: {file_path.name}")

    rows = int(header[0])
    columns = int(header[1])
    regions: list[dict[str, Any]] = []

    for index, line in enumerate(lines[1:], start=1):
        parts = line.split("=")
        if len(parts) < 7:
            continue
        start_row = int(parts[0])
        end_row = int(parts[1])
        start_column = int(parts[2])
        end_column = int(parts[3])
        axis = parts[4].strip().upper() or "D"
        pattern = repair_pattern_text(parts[5])
        region_type = parts[6].strip().upper() or "T"
        regions.append(
            {
                "index": index,
                "start_row": start_row,
                "end_row": end_row,
                "start_column": start_column,
                "end_column": end_column,
                "row_count": end_row - start_row + 1,
                "column_count": end_column - start_column + 1,
                "axis": axis,
                "pattern": pattern,
                "region_type": region_type,
                "choices": [character for character in pattern if character.strip()],
            }
        )

    return {
        "rows": rows,
        "columns": columns,
        "regions": regions,
        "template": selected,
        "file_path": str(file_path),
    }


def get_answer_regions(template: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_regions = resolve_coordinate_source_regions(template, "answer_regions")
    if explicit_regions:
        return explicit_regions

    regions = []
    for region in template.get("regions", []):
        if region["axis"] != "Y":
            continue
        if region["row_count"] <= 1:
            continue
        choices = region["choices"]
        if len(choices) < 4 or len(choices) > 5:
            continue
        if region["column_count"] != len(region["pattern"]):
            continue
        regions.append(region)
    return regions


def get_booklet_region(template: dict[str, Any], booklet_codes: list[str]) -> dict[str, Any] | None:
    expected = {normalize_token(code) for code in booklet_codes if normalize_token(code)}
    if not expected or len(expected) == 1:
        return None

    explicit_region = resolve_coordinate_source_region(template, "booklet_region")
    if explicit_region:
        choices = {normalize_token(choice) for choice in explicit_region["choices"] if normalize_token(choice)}
        if expected.issubset(choices):
            return explicit_region

    for region in template.get("regions", []):
        if region["axis"] != "Y" or region["row_count"] != 1:
            continue
        choices = {normalize_token(choice) for choice in region["choices"] if normalize_token(choice)}
        if expected.issubset(choices):
            return region
    return None


def find_template_region(
    template: dict[str, Any],
    *,
    start_row: int,
    end_row: int,
    start_column: int,
    end_column: int,
    axis: str,
    normalized_choices: str | None = None,
) -> dict[str, Any] | None:
    for region in template.get("regions", []):
        if region["start_row"] != start_row or region["end_row"] != end_row:
            continue
        if region["start_column"] != start_column or region["end_column"] != end_column:
            continue
        if region["axis"] != axis:
            continue
        if normalized_choices is not None:
            current_choices = "".join(normalize_token(choice) for choice in region["choices"])
            if current_choices != normalized_choices:
                continue
        return region
    return None


def build_virtual_template_region(template: dict[str, Any], spec: dict[str, Any], index_seed: int) -> dict[str, Any] | None:
    row_count = template.get("rows") or 0
    column_count = template.get("columns") or 0
    start_row = int(spec["start_row"])
    end_row = int(spec["end_row"])
    start_column = int(spec["start_column"])
    end_column = int(spec["end_column"])
    if start_row < 1 or end_row > row_count or start_column < 1 or end_column > column_count:
        return None
    pattern = str(spec.get("pattern") or spec.get("normalized_choices") or "")
    choices = [character for character in pattern if character.strip()]
    return {
        "index": index_seed,
        "start_row": start_row,
        "end_row": end_row,
        "start_column": start_column,
        "end_column": end_column,
        "row_count": end_row - start_row + 1,
        "column_count": end_column - start_column + 1,
        "axis": str(spec.get("axis") or "D").upper(),
        "pattern": pattern,
        "region_type": str(spec.get("region_type") or "T").upper(),
        "choices": choices,
    }


def class_number_region_consumes_section_column(region: dict[str, Any] | None) -> bool:
    if not region:
        return False
    choices = "".join(normalize_token(choice) for choice in region.get("choices") or [])
    return (
        str(region.get("axis") or "").upper() == "D"
        and choices == "0123456789"
        and int(region.get("start_column") or 0) <= 34 <= int(region.get("end_column") or 0)
    )


def get_named_field_regions(template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    explicit_regions = resolve_coordinate_source_regions(template, "named_fields")
    named_regions: dict[str, dict[str, Any]] = {}
    for region in explicit_regions:
        named_regions[region["semantic_name"]] = region

    student_number_region = find_template_region(
        template,
        start_row=23,
        end_row=32,
        start_column=35,
        end_column=45,
        axis="D",
        normalized_choices="0123456789",
    )
    if student_number_region:
        student_number_region = dict(student_number_region)
        student_number_region["reverse_columns"] = True
        named_regions.setdefault("student_number", student_number_region)

    class_number_region = find_template_region(
        template,
        start_row=23,
        end_row=32,
        start_column=31,
        end_column=33,
        axis="D",
        normalized_choices="0123456789",
    )
    if class_number_region:
        class_number_region = dict(class_number_region)
        class_number_region["reverse_columns"] = True
        named_regions.setdefault("class_number", class_number_region)

    class_section_region = find_template_region(
        template,
        start_row=23,
        end_row=32,
        start_column=34,
        end_column=34,
        axis="D",
        normalized_choices="ABCDEFGHIJ",
    )
    if class_section_region and not class_number_region_consumes_section_column(named_regions.get("class_number")):
        named_regions.setdefault("class_section", dict(class_section_region))

    for field_name, end_row, normalized_choices, start_column, end_column in (
        ("student_surname", 33, None, 6, 15),
        ("student_name", 33, None, 19, 28),
        ("student_surname", 30, None, 6, 15),
        ("student_name", 30, None, 19, 28),
    ):
        if field_name in named_regions:
            continue
        region = find_template_region(
            template,
            start_row=2,
            end_row=end_row,
            start_column=start_column,
            end_column=end_column,
            axis="D",
            normalized_choices=normalized_choices,
        )
        if region:
            named_regions[field_name] = dict(region)

    return named_regions


def get_template_coordinate_source(template: dict[str, Any]) -> dict[str, Any]:
    template_id = slugify_form_template_name(template.get("template", {}).get("id"))
    direct_source = EXPLICIT_TEMPLATE_COORDINATE_SOURCES.get(template_id)
    if direct_source:
        return direct_source
    normalized_id = EXPLICIT_TEMPLATE_COORDINATE_ALIASES.get(template_id, template_id)
    return EXPLICIT_TEMPLATE_COORDINATE_SOURCES.get(normalized_id, {})


def resolve_coordinate_source_region(template: dict[str, Any], key: str) -> dict[str, Any] | None:
    spec = get_template_coordinate_source(template).get(key)
    if not spec:
        return None
    region = find_template_region(
        template,
        start_row=spec["start_row"],
        end_row=spec["end_row"],
        start_column=spec["start_column"],
        end_column=spec["end_column"],
        axis=spec["axis"],
        normalized_choices=spec.get("normalized_choices"),
    )
    if not region:
        if not spec.get("virtual"):
            return None
        region = build_virtual_template_region(template, spec, 9000)
        if not region:
            return None
    annotated_region = dict(region)
    annotated_region["semantic_name"] = spec.get("name", key)
    annotated_region["reverse_columns"] = bool(spec.get("reverse_columns")) or annotated_region["semantic_name"] in {
        "student_number",
    }
    return annotated_region


def resolve_coordinate_source_regions(template: dict[str, Any], key: str) -> list[dict[str, Any]]:
    specs = get_template_coordinate_source(template).get(key) or []
    regions: list[dict[str, Any]] = []
    for index, spec in enumerate(specs, start=1):
        semantic_name = spec.get("name", key)
        region = find_template_region(
            template,
            start_row=spec["start_row"],
            end_row=spec["end_row"],
            start_column=spec["start_column"],
            end_column=spec["end_column"],
            axis=spec["axis"],
            normalized_choices=spec.get("normalized_choices"),
        )
        if not region:
            if not spec.get("virtual"):
                continue
            region = build_virtual_template_region(template, spec, 9000 + index)
            if not region:
                continue
        annotated_region = dict(region)
        annotated_region["semantic_name"] = semantic_name
        annotated_region["reverse_columns"] = bool(spec.get("reverse_columns")) or annotated_region["semantic_name"] in {
            "student_number",
        }
        regions.append(annotated_region)
    return regions


def decode_horizontal_pattern(segment: list[int], pattern: str, threshold: int) -> tuple[str, str]:
    tokens = []
    values = []
    for index, value in enumerate(segment):
        token = pattern[index] if index < len(pattern) else " "
        if not token.strip():
            continue
        tokens.append(token)
        values.append(value)

    token, status = decode_single_with_soft_threshold(values, tokens, threshold)
    return normalize_token(token) if token else "", status


def decode_vertical_pattern(
    segment: list[int],
    choices: list[str],
    threshold: int,
    allow_soft_single: bool = True,
) -> tuple[str, str]:
    tokens = []
    values = []
    for index, value in enumerate(segment):
        if index >= len(choices):
            break
        token = str(choices[index] or "").strip()
        if not token:
            continue
        tokens.append(token)
        values.append(value)

    return decode_single_with_soft_threshold(values, tokens, threshold, allow_soft_single=allow_soft_single)


def count_nonblank_prefix(tokens: list[str]) -> int:
    prefix_length = 0
    for token in tokens:
        if not token:
            break
        prefix_length += 1
    return prefix_length


def count_alnum_tokens(tokens: list[str]) -> int:
    return sum(1 for token in tokens if token and token.isalnum())


def decode_vertical_region_once(
    matrix: list[list[int]],
    region: dict[str, Any],
    threshold: int,
    row_shift: int,
    allow_soft_single: bool,
) -> tuple[list[str], list[str]]:
    decoded_tokens: list[str] = []
    warnings: list[str] = []
    column_offsets = list(range(region["column_count"]))
    if region.get("reverse_columns"):
        column_offsets.reverse()
    region_has_strong_mark = False

    if allow_soft_single:
        for column_offset in column_offsets:
            column_index = region["start_column"] - 1 + column_offset
            for row_offset in range(region["row_count"]):
                row_index = region["start_row"] - 1 + row_offset + row_shift
                if row_index < 0 or row_index >= len(matrix):
                    continue
                row = matrix[row_index]
                if column_index < len(row) and row[column_index] >= threshold:
                    region_has_strong_mark = True
                    break
            if region_has_strong_mark:
                break

    for output_index, column_offset in enumerate(column_offsets, start=1):
        column_index = region["start_column"] - 1 + column_offset
        segment: list[int] = []

        for row_offset in range(region["row_count"]):
            row_index = region["start_row"] - 1 + row_offset + row_shift
            if row_index < 0 or row_index >= len(matrix):
                segment.append(0)
                continue
            row = matrix[row_index]
            segment.append(row[column_index] if column_index < len(row) else 0)

        token, status = decode_vertical_pattern(
            segment,
            region["choices"],
            threshold,
            allow_soft_single=allow_soft_single and region_has_strong_mark,
        )
        decoded_tokens.append(token if token else "")
        if status == "multiple":
            warnings.append(f"Alan {region['index']} / kolon {output_index}: birden fazla isaret")

    return decoded_tokens, warnings


def get_named_field_row_shift_candidates(region: dict[str, Any]) -> list[int]:
    semantic_name = str(region.get("semantic_name") or "")
    if semantic_name in {
        "student_name",
        "student_surname",
        "class_number",
        "class_section",
        "student_number",
        "exam_code_prefix",
        "exam_code_number",
        "exam_date_day",
        "exam_date_month",
        "exam_date_year",
    }:
        return [0, 1, -1, 2]
    return [0]


def get_named_field_shift_group(region: dict[str, Any]) -> str:
    semantic_name = str(region.get("semantic_name") or "")
    if semantic_name in {"student_name", "student_surname"}:
        return "student_identity_text"
    if semantic_name in {"class_number", "class_section"}:
        return "classroom"
    if semantic_name in {"exam_code_prefix", "exam_code_number"}:
        return "exam_code"
    if semantic_name in {"exam_date_day", "exam_date_month", "exam_date_year"}:
        return "exam_date"
    return semantic_name or str(region["index"])


def build_vertical_region_candidates(
    matrix: list[list[int]],
    region: dict[str, Any],
    threshold: int,
    allow_soft_single: bool,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    semantic_name = str(region.get("semantic_name") or "")
    default_reverse_columns = bool(region.get("reverse_columns"))
    reverse_options = [default_reverse_columns]
    if semantic_name in AUTO_REVERSE_FIELD_NAMES:
        reverse_options = list(dict.fromkeys([default_reverse_columns, not default_reverse_columns]))

    for reverse_columns in reverse_options:
        candidate_region = dict(region)
        candidate_region["reverse_columns"] = reverse_columns
        for row_shift in get_named_field_row_shift_candidates(region):
            decoded_tokens, warnings = decode_vertical_region_once(
                matrix,
                candidate_region,
                threshold,
                row_shift,
                allow_soft_single,
            )
            candidates.append(
                {
                    "base_score": (
                        count_nonblank_prefix(decoded_tokens),
                        sum(1 for token in decoded_tokens if token),
                        count_alnum_tokens(decoded_tokens),
                        -len(warnings),
                    ),
                    "row_shift": row_shift,
                    "reverse_columns": reverse_columns,
                    "default_reverse_columns": default_reverse_columns,
                    "decoded_tokens": decoded_tokens,
                    "warnings": warnings,
                }
            )
    return candidates


def choose_preferred_field_variant(candidates_by_region: dict[str, list[dict[str, Any]]]) -> tuple[int, bool] | None:
    variant_support: dict[tuple[int, bool], int] = {}
    variant_default_support: dict[tuple[int, bool], int] = {}
    for candidates in candidates_by_region.values():
        if not candidates:
            continue
        best_base_score = max(candidate["base_score"] for candidate in candidates)
        for candidate in candidates:
            if candidate["base_score"] != best_base_score:
                continue
            if not any(candidate["decoded_tokens"]):
                continue
            prefix_length, nonblank_count, alnum_count, warning_penalty = candidate["base_score"]
            variant_key = (int(candidate["row_shift"]), bool(candidate.get("reverse_columns")))
            variant_support[variant_key] = variant_support.get(variant_key, 0) + (
                prefix_length + nonblank_count + alnum_count + max(warning_penalty, -1) + 1
            )
            variant_default_support[variant_key] = variant_default_support.get(variant_key, 0) + int(
                bool(candidate.get("reverse_columns")) == bool(candidate.get("default_reverse_columns"))
            )

    if not variant_support:
        return None

    return max(
        variant_support.items(),
        key=lambda item: (
            item[1],
            variant_default_support.get(item[0], 0),
            item[0][0] == 0,
            -abs(item[0][0]),
            item[0][1] is False,
        ),
    )[0]


def decode_vertical_region(
    matrix: list[list[int]],
    region: dict[str, Any],
    threshold: int,
    preferred_shift: int | None = None,
    preferred_reverse_columns: bool | None = None,
    allow_soft_single: bool = True,
) -> tuple[str, list[str]]:
    candidates = build_vertical_region_candidates(matrix, region, threshold, allow_soft_single)
    selected_candidate = max(
        candidates,
        key=lambda candidate: (
            candidate["base_score"],
            candidate["row_shift"] == preferred_shift,
            candidate.get("reverse_columns") == preferred_reverse_columns,
            candidate["row_shift"] == 0,
            candidate.get("reverse_columns") == bool(region.get("reverse_columns")),
            candidate.get("reverse_columns") is False,
            -abs(candidate["row_shift"]),
        ),
    )
    selected_shift = int(selected_candidate["row_shift"])
    decoded_tokens = list(selected_candidate["decoded_tokens"])
    warnings = list(selected_candidate["warnings"])
    selected_reverse_columns = bool(selected_candidate.get("reverse_columns"))
    if selected_shift != 0 and any(decoded_tokens):
        warnings = list(warnings) + [
            f"Alan {region.get('semantic_name') or region['index']} icin satir ofseti {selected_shift:+d} ile cozum iyilestirildi."
        ]
    if selected_reverse_columns != bool(region.get("reverse_columns")) and any(decoded_tokens):
        warnings = list(warnings) + [
            f"Alan {region.get('semantic_name') or region['index']} icin sagdan-sola kolon cozumlemesi tercih edildi."
        ]

    return "".join(decoded_tokens).strip(), warnings


def decode_auxiliary_fields(
    matrix: list[list[int]],
    template: dict[str, Any],
    threshold: int,
) -> tuple[dict[str, str], list[str]]:
    decoded_fields: dict[str, str] = {}
    warnings: list[str] = []
    field_regions = get_named_field_regions(template)
    preferred_variant_by_group: dict[str, tuple[int, bool]] = {}

    grouped_candidates: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for field_name, region in field_regions.items():
        shift_group = get_named_field_shift_group(region)
        allow_soft_single = field_name in SOFT_SINGLE_AUXILIARY_FIELD_NAMES
        grouped_candidates.setdefault(shift_group, {})[field_name] = build_vertical_region_candidates(
            matrix,
            region,
            threshold,
            allow_soft_single=allow_soft_single,
        )

    for shift_group, candidates_by_region in grouped_candidates.items():
        preferred_variant = choose_preferred_field_variant(candidates_by_region)
        if preferred_variant is not None:
            preferred_variant_by_group[shift_group] = preferred_variant

    for field_name, region in field_regions.items():
        preferred_variant = preferred_variant_by_group.get(get_named_field_shift_group(region))
        allow_soft_single = field_name in SOFT_SINGLE_AUXILIARY_FIELD_NAMES
        decoded_text, region_warnings = decode_vertical_region(
            matrix,
            region,
            threshold,
            preferred_shift=preferred_variant[0] if preferred_variant else None,
            preferred_reverse_columns=preferred_variant[1] if preferred_variant else None,
            allow_soft_single=allow_soft_single,
        )
        warnings.extend(region_warnings)
        normalized_text = normalize_decoded_field_value(field_name, decoded_text)
        if normalized_text:
            decoded_fields[field_name] = normalized_text

    student_name = decoded_fields.get("student_name") or ""
    student_surname = decoded_fields.get("student_surname") or ""
    if student_name or student_surname:
        decoded_fields["student_full_name"] = " ".join(
            part for part in (student_name, student_surname) if part
        ).strip()

    class_number = decoded_fields.get("class_number") or ""
    class_section = decoded_fields.get("class_section") or ""
    if class_number or class_section:
        decoded_fields["classroom"] = f"{class_section}{class_number}".strip()

    exam_code_prefix = decoded_fields.get("exam_code_prefix") or ""
    exam_code_number = decoded_fields.get("exam_code_number") or ""
    if exam_code_prefix and len(exam_code_number) >= 1:
        decoded_fields["exam_code"] = f"{exam_code_prefix}{exam_code_number.zfill(3)}"
    elif exam_code_number and len(exam_code_number) >= 4:
        decoded_fields["exam_code"] = exam_code_number
    elif decoded_fields.get("exam_code") and len(decoded_fields["exam_code"]) < 4:
        decoded_fields.pop("exam_code", None)

    exam_date_parts = [
        decoded_fields.get("exam_date_day") or "",
        decoded_fields.get("exam_date_month") or "",
        decoded_fields.get("exam_date_year") or "",
    ]
    if any(exam_date_parts):
        if (
            len(exam_date_parts[0]) == 2
            and len(exam_date_parts[1]) == 2
            and len(exam_date_parts[2]) == 4
            and is_plausible_exam_date(*exam_date_parts)
        ):
            decoded_fields["exam_date"] = normalize_exam_date_parts(*exam_date_parts)
        else:
            decoded_fields.pop("exam_date", None)
    elif decoded_fields.get("exam_date"):
        decoded_fields["exam_date"] = format_exam_date_value(decoded_fields["exam_date"])

    return decoded_fields, warnings


def count_candidate_marks(matrix: list[list[int]], threshold: int) -> int:
    return sum(1 for row in matrix for value in row if value >= threshold)


def count_candidate_marks_in_regions(
    matrix: list[list[int]],
    regions: list[dict[str, Any]],
    threshold: int,
) -> int:
    count = 0
    for region in regions:
        for row_index in range(region["start_row"] - 1, region["end_row"]):
            if row_index >= len(matrix):
                continue
            row = matrix[row_index]
            for column_index in range(region["start_column"] - 1, region["end_column"]):
                if column_index >= len(row):
                    continue
                if row[column_index] >= threshold:
                    count += 1
    return count


def build_decode_diagnostics(
    matrix: list[list[int]],
    template: dict[str, Any],
    threshold: int,
) -> dict[str, int]:
    answer_regions = get_answer_regions(template)
    named_regions = list(get_named_field_regions(template).values())
    total_candidate_mark_count = count_candidate_marks(matrix, threshold)
    answer_region_candidate_mark_count = count_candidate_marks_in_regions(matrix, answer_regions, threshold)
    named_field_candidate_mark_count = count_candidate_marks_in_regions(matrix, named_regions, threshold)
    outside_candidate_mark_count = max(
        total_candidate_mark_count - answer_region_candidate_mark_count - named_field_candidate_mark_count,
        0,
    )
    return {
        "total_candidate_mark_count": total_candidate_mark_count,
        "answer_region_candidate_mark_count": answer_region_candidate_mark_count,
        "named_field_candidate_mark_count": named_field_candidate_mark_count,
        "outside_candidate_mark_count": outside_candidate_mark_count,
        "expected_answer_slot_count": sum(region["row_count"] for region in answer_regions),
    }


def build_low_confidence_decode_error(decoded_sheet: dict[str, Any], exam: dict[str, Any] | None = None) -> str | None:
    diagnostics = decoded_sheet.get("diagnostics") or {}
    total_candidate_mark_count = int(diagnostics.get("total_candidate_mark_count", 0))
    answer_region_candidate_mark_count = int(diagnostics.get("answer_region_candidate_mark_count", 0))
    named_field_candidate_mark_count = int(diagnostics.get("named_field_candidate_mark_count", 0))
    outside_candidate_mark_count = int(diagnostics.get("outside_candidate_mark_count", 0))
    recognized_candidate_mark_count = answer_region_candidate_mark_count + named_field_candidate_mark_count
    decoded_fields = decoded_sheet.get("decoded_fields") or {}
    structured_identity_evidence_count = 0
    if len(str(decoded_fields.get("student_number") or "")) >= 8:
        structured_identity_evidence_count += 1
    if len(normalize_decoded_text(decoded_fields.get("student_full_name") or "")) >= 5:
        structured_identity_evidence_count += 1
    if len(str(decoded_fields.get("class_number") or "")) >= 3 or len(normalize_decoded_text(decoded_fields.get("classroom") or "")) >= 4:
        structured_identity_evidence_count += 1
    if len(str(decoded_fields.get("exam_date") or "")) == 10:
        structured_identity_evidence_count += 1

    relevant_answer_count = 0
    if exam:
        expected_positions = get_expected_answer_positions(exam, decoded_sheet.get("booklet_code"))
        answer_positions = get_sorted_answer_positions(decoded_sheet.get("answers") or {})
        relevant_answer_count = len(
            [position for position in answer_positions if not expected_positions or position in expected_positions]
        )

    if total_candidate_mark_count <= 0:
        return None
    if (
        named_field_candidate_mark_count >= 18
        and structured_identity_evidence_count >= 3
        and (relevant_answer_count > 0 or answer_region_candidate_mark_count > 0)
    ):
        return None
    if outside_candidate_mark_count < 20:
        return None
    if outside_candidate_mark_count <= recognized_candidate_mark_count:
        return None

    return (
        "Cihaz verisi geldi ancak isaretlerin cogu beklenen cevap/kimlik bloklarinin disinda kaldi. "
        f"Blok ici aday isaret={recognized_candidate_mark_count} "
        f"(cevap={answer_region_candidate_mark_count}, kimlik={named_field_candidate_mark_count}), "
        f"blok disi aday isaret={outside_candidate_mark_count}, toplam aday isaret={total_candidate_mark_count}. "
        "Bu form guvenilir cozulmedi; secilen optik formati, kagit yonunu ve cihaz hizalamasini kontrol edip yeniden okutun."
    )


def decode_answers_from_sheet(
    matrix: list[list[int]],
    template: dict[str, Any],
    threshold: int,
) -> tuple[dict[str, str], list[str]]:
    answers: dict[str, str] = {}
    warnings: list[str] = []
    position = 1

    for region in get_answer_regions(template):
        for row_offset in range(region["row_count"]):
            row_index = region["start_row"] - 1 + row_offset
            if row_index >= len(matrix):
                warnings.append(f"Q{position}: satir matriste yok")
                position += 1
                continue

            row = matrix[row_index]
            start = region["start_column"] - 1
            end = region["end_column"]
            answer, status = decode_horizontal_pattern(row[start:end], region["pattern"], threshold)
            if answer:
                answers[str(position)] = normalize_answer(answer)
            elif status == "multiple":
                warnings.append(f"Q{position}: birden fazla isaret")
            elif status == "adjacent_ambiguous":
                warnings.append(f"Q{position}: komsu siklar birbirine cok yakin, operator kontrolu gerekli")
            position += 1

    return answers, warnings


def detect_booklet_code(
    matrix: list[list[int]],
    template: dict[str, Any],
    booklet_codes: list[str],
    threshold: int,
    fallback_booklet: str | None = None,
) -> str:
    normalized_fallback = normalize_token(fallback_booklet)
    normalized_booklets = [normalize_token(code) for code in booklet_codes if normalize_token(code)]
    if len(normalized_booklets) == 1:
        return normalized_booklets[0]

    region = get_booklet_region(template, normalized_booklets)
    if not region:
        return ""

    row_index = region["start_row"] - 1
    if row_index >= len(matrix):
        return ""

    row = matrix[row_index]
    start = region["start_column"] - 1
    end = region["end_column"]
    booklet_code, status = decode_horizontal_pattern(row[start:end], region["pattern"], threshold)
    if status != "single":
        return normalized_fallback
    return booklet_code if booklet_code in normalized_booklets else ""


def build_decoded_sheet_payload(
    sheet: dict[str, Any],
    matrix: list[list[int]],
    template: dict[str, Any],
    exam: dict[str, Any],
    threshold: int,
    fallback_booklet: str | None,
    matrix_orientation: str,
    auxiliary_threshold: int | None = None,
) -> dict[str, Any]:
    booklet_code = detect_booklet_code(matrix, template, exam.get("booklet_codes", []), threshold, fallback_booklet)
    answers, warnings = decode_answers_from_sheet(matrix, template, threshold)
    field_threshold = auxiliary_threshold if auxiliary_threshold is not None else threshold
    decoded_fields, field_warnings = decode_auxiliary_fields(matrix, template, field_threshold)
    diagnostics = build_decode_diagnostics(matrix, template, threshold)
    warnings.extend(field_warnings)
    return {
        "sheet_no": sheet.get("sheet_no", 0),
        "student_id": decoded_fields.get("student_number") or f"FORM-{sheet.get('sheet_no', 0):03d}",
        "booklet_code": booklet_code,
        "answers": answers,
        "source_row": sheet.get("sheet_no", 0),
        "warnings": warnings,
        "decoded_fields": decoded_fields,
        "decoded_question_count": len(answers),
        "analysis_threshold_used": threshold,
        "diagnostics": diagnostics,
        "matrix_orientation": matrix_orientation,
        "matrix_orientation_corrected": matrix_orientation != "as_is",
    }


def build_orientation_candidates(matrix: list[list[int]]) -> list[tuple[str, list[list[int]]]]:
    if not matrix:
        return [("as_is", matrix)]
    return [
        ("flip_vertical", list(reversed(matrix))),
        ("as_is", matrix),
    ]


def decode_sheet(
    sheet: dict[str, Any],
    template: dict[str, Any],
    exam: dict[str, Any],
    threshold: int,
    fallback_booklet: str | None = None,
) -> dict[str, Any]:
    matrix = sheet.get("front_matrix") or []
    candidates = [
        build_decoded_sheet_payload(sheet, candidate_matrix, template, exam, threshold, fallback_booklet, orientation)
        for orientation, candidate_matrix in build_orientation_candidates(matrix)
    ]
    best_candidate = max(candidates, key=lambda candidate: score_decoded_sheet_candidate(candidate, exam))

    if threshold > 1:
        relaxed_threshold = threshold - 1
        relaxed_candidates = [
            build_decoded_sheet_payload(
                sheet,
                candidate_matrix,
                template,
                exam,
                relaxed_threshold,
                fallback_booklet,
                orientation,
                auxiliary_threshold=threshold,
            )
            for orientation, candidate_matrix in build_orientation_candidates(matrix)
        ]
        best_relaxed_candidate = max(relaxed_candidates, key=lambda candidate: score_decoded_sheet_candidate(candidate, exam))
        if (
            score_decoded_sheet_candidate(best_relaxed_candidate, exam) > score_decoded_sheet_candidate(best_candidate, exam)
            and relaxed_candidate_is_safe(best_candidate, best_relaxed_candidate)
        ):
            best_candidate = deepcopy(best_relaxed_candidate)
            best_candidate.setdefault("warnings", []).append(
                f"Analiz esigi {relaxed_threshold}'e dusurulerek zayif isaretler geri kazanildi."
            )

    if best_candidate["matrix_orientation_corrected"]:
        best_candidate = deepcopy(best_candidate)
        best_candidate.setdefault("warnings", []).append("Form matrisi dikey terslik algilanarak cozuldu.")
    return best_candidate


def get_sorted_answer_positions(answers: dict[str, str]) -> list[int]:
    positions: list[int] = []
    for value in answers:
        try:
            positions.append(int(value))
        except (TypeError, ValueError):
            continue
    return sorted(set(positions))


def contiguous_answer_prefix_length(answer_positions: list[int]) -> int:
    expected = 1
    for position in answer_positions:
        if position != expected:
            break
        expected += 1
    return expected - 1


def get_expected_answer_positions(exam: dict[str, Any], booklet_code: str | None = None) -> list[int]:
    normalized_booklet = normalize_token(booklet_code)
    positions: set[int] = set()

    for question in exam.get("questions") or []:
        booklet_mappings = question.get("booklet_mappings") or {}
        if normalized_booklet:
            target_mapping = None
            for mapping_booklet, mapping in booklet_mappings.items():
                if normalize_token(mapping_booklet) == normalized_booklet:
                    target_mapping = mapping
                    break
            candidate_mappings = [target_mapping] if target_mapping else []
        else:
            candidate_mappings = list(booklet_mappings.values())

        for mapping in candidate_mappings:
            if not isinstance(mapping, dict):
                continue
            try:
                position = int(mapping.get("position"))
            except (TypeError, ValueError):
                continue
            if position > 0:
                positions.add(position)

    if positions:
        return sorted(positions)

    question_count = len(exam.get("questions") or [])
    return list(range(1, question_count + 1))


def contiguous_expected_answer_prefix_length(answer_positions: list[int], expected_positions: list[int]) -> int:
    if not expected_positions:
        return contiguous_answer_prefix_length(answer_positions)
    answer_set = set(answer_positions)
    prefix_length = 0
    for expected_position in expected_positions:
        if expected_position not in answer_set:
            break
        prefix_length += 1
    return prefix_length


def score_decoded_sheet_candidate(decoded_sheet: dict[str, Any], exam: dict[str, Any]) -> tuple[int, int, int, int, int, int, int, int]:
    diagnostics = decoded_sheet.get("diagnostics") or {}
    answer_positions = get_sorted_answer_positions(decoded_sheet.get("answers") or {})
    expected_positions = get_expected_answer_positions(exam, decoded_sheet.get("booklet_code"))
    relevant_answer_positions = [
        position for position in answer_positions if not expected_positions or position in expected_positions
    ]
    out_of_range_answer_count = max(len(answer_positions) - len(relevant_answer_positions), 0)
    contiguous_prefix = contiguous_expected_answer_prefix_length(relevant_answer_positions, expected_positions)
    decoded_question_count = len(relevant_answer_positions)
    booklet_detected = 1 if normalize_token(decoded_sheet.get("booklet_code")) else 0
    named_field_detected = len(decoded_sheet.get("decoded_fields") or {})
    answer_region_candidate_mark_count = int(diagnostics.get("answer_region_candidate_mark_count", 0))
    outside_candidate_mark_count = int(diagnostics.get("outside_candidate_mark_count", 0))
    expected_question_count = len(expected_positions)

    score = decoded_question_count * 200
    score += contiguous_prefix * 60
    score += min(answer_region_candidate_mark_count, max(expected_question_count, decoded_question_count)) * 20
    score += booklet_detected * 150
    score += named_field_detected * 25
    if relevant_answer_positions and (not expected_positions or relevant_answer_positions[0] == expected_positions[0]):
        score += 300
    if expected_question_count:
        score -= abs(expected_question_count - decoded_question_count) * 50
    score -= out_of_range_answer_count * 220
    score -= min(outside_candidate_mark_count, 200)

    flip_preference = 1 if decoded_sheet.get("matrix_orientation") == "flip_vertical" else 0
    return (
        score,
        contiguous_prefix,
        decoded_question_count,
        booklet_detected,
        named_field_detected,
        -out_of_range_answer_count,
        -outside_candidate_mark_count,
        flip_preference,
    )


def build_answer_key_decode_error(decoded_sheet: dict[str, Any]) -> str | None:
    answers = {str(index): normalize_answer(answer) for index, answer in decoded_sheet.get("answers", {}).items() if normalize_answer(answer)}
    diagnostics = decoded_sheet.get("diagnostics") or {}
    total_candidate_mark_count = int(diagnostics.get("total_candidate_mark_count", 0))
    answer_region_candidate_mark_count = int(diagnostics.get("answer_region_candidate_mark_count", 0))

    if not answers:
        if total_candidate_mark_count:
            return (
                "Optik cevap anahtarinda beklenen cevap bloklarinda tekil isaret bulunamadi. "
                f"Cihaz verisi geldi (aday isaret={total_candidate_mark_count}, cevap blogu aday isaret={answer_region_candidate_mark_count}). "
                "Muhtemel neden: yanlis format secimi, kagit yonu veya analiz esigi."
            )
        return "Optik cevap anahtarinda anlamli cevap isareti bulunamadi."

    answer_positions = get_sorted_answer_positions(answers)
    if not answer_positions:
        return "Optik cevap anahtarindaki isaret pozisyonlari ayrisamadi."

    if answer_positions[0] != 1:
        preview = ", ".join(f"Q{position}" for position in answer_positions[:8])
        return (
            "Cihaz verisi geldi ancak cevap anahtari Q1'den baslamiyor. "
            f"Cozulen tekil isaretler: {preview}. "
            "Muhtemel neden: yanlis format secimi, kagit yonu/ters besleme veya formun cevap anahtari yerine farkli bir bolgesinin okunmasi."
        )

    contiguous_length = contiguous_answer_prefix_length(answer_positions)
    if contiguous_length != len(answer_positions):
        first_gap_position = answer_positions[contiguous_length]
        return (
            "Cihaz verisi geldi ancak cevap anahtari kesintisiz okunmadi. "
            f"Q1-Q{contiguous_length} araligi tekil cozuldu, sonraki ilk tekil isaret Q{first_gap_position}. "
            "Muhtemel neden: yanlis format secimi, eksik/yanlis kodlanmis cevap anahtari veya kagit hizalama sorunu."
        )

    return None


def build_questions_from_scanned_booklets(
    booklet_codes: list[str],
    booklet_answers: dict[str, dict[str, str]],
    existing_questions: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    normalized_booklets = [normalize_token(code) for code in booklet_codes if normalize_token(code)]
    existing_questions = list(existing_questions or [])

    if existing_questions:
        question_count = len(existing_questions)
        for booklet, answers in booklet_answers.items():
            if len(answers) != question_count:
                diff = question_count - len(answers)
                hint = (
                    f" Analiz esigini {max(1, 12 - 2)}'e dusurup yeniden okuyun."
                    if diff > 0
                    else f" Fazladan {-diff} isaret algilandi; form yonunu ve formati kontrol edin."
                )
                raise ValueError(
                    f"Optik cevap anahtari {booklet} kitapcigi icin {len(answers)} soru verdi; "
                    f"mevcut sinavda ise {question_count} soru var (fark: {diff:+d}).{hint}"
                )

        merged_questions = deepcopy(existing_questions)
        for question in merged_questions:
            canonical_no = int(question["canonical_no"])
            for booklet, answers in booklet_answers.items():
                if booklet not in normalized_booklets:
                    continue
                existing_mapping = (question.get("booklet_mappings") or {}).get(booklet) or {}
                existing_position = int(existing_mapping.get("position") or canonical_no)
                question.setdefault("booklet_mappings", {})[booklet] = {
                    "position": existing_position,
                    "correct_answer": normalize_answer(answers.get(str(existing_position), "")),
                }
        return merged_questions

    if not normalized_booklets or any(booklet not in booklet_answers for booklet in normalized_booklets):
        return []

    lengths = {booklet: len(booklet_answers[booklet]) for booklet in normalized_booklets}
    if len(set(lengths.values())) != 1:
        count_detail = ", ".join(f"{b}={c}" for b, c in sorted(lengths.items()))
        modal_count = max(set(lengths.values()), key=list(lengths.values()).count)
        min_count = min(lengths.values())
        outliers = [b for b, c in lengths.items() if c != modal_count]
        warning_msg = (
            f"Optik cevap anahtari kitapciklari arasinda soru sayisi uyusmuyor ({count_detail}). "
            f"Cogunluk: {modal_count} soru. "
            f"Uyumsuz kitapcik(lar): {', '.join(sorted(outliers))} ({min_count} soru verdi). "
            f"Gecici olarak {min_count} ortak soru uzerine anahtar olusturuldu; "
            f"uyumsuz kitapcigin formunu analiz esigini dusurup (ornegin 10) yeniden okuyunca tam anahtar guncellenecek."
        )
        partial_questions: list[dict[str, Any]] = []
        for canonical_no in range(1, min_count + 1):
            booklet_mappings: dict[str, Any] = {}
            valid = True
            for booklet in normalized_booklets:
                correct_answer = normalize_answer(booklet_answers[booklet].get(str(canonical_no), ""))
                if not correct_answer:
                    valid = False
                    break
                booklet_mappings[booklet] = {"position": canonical_no, "correct_answer": correct_answer}
            if valid:
                partial_questions.append(
                    {"canonical_no": canonical_no, "group_label": "Genel", "weight": 1, "booklet_mappings": booklet_mappings}
                )
        raise SynthesisPartialResult(warning_msg, partial_questions)

    question_count = next(iter(lengths.values()), 0)
    questions: list[dict[str, Any]] = []
    for canonical_no in range(1, question_count + 1):
        booklet_mappings = {}
        for booklet in normalized_booklets:
            correct_answer = normalize_answer(booklet_answers[booklet].get(str(canonical_no), ""))
            if not correct_answer:
                raise ValueError(f"{booklet} kitapcigi icin {canonical_no}. soruda isaret bulunamadi.")
            booklet_mappings[booklet] = {
                "position": canonical_no,
                "correct_answer": correct_answer,
            }
        questions.append(
            {
                "canonical_no": canonical_no,
                "group_label": "Genel",
                "weight": 1,
                "booklet_mappings": booklet_mappings,
            }
        )
    return questions


def apply_optical_answer_key(
    exam: dict[str, Any],
    decoded_sheet: dict[str, Any],
    source_file: str,
) -> dict[str, Any]:
    booklet_code = normalize_token(decoded_sheet.get("booklet_code"))
    if not booklet_code:
        raise ValueError("Optik cevap anahtarinda kitapcik kodu tespit edilemedi. Gerekirse kitapcik override kullanin.")

    if booklet_code not in {normalize_token(code) for code in exam.get("booklet_codes", [])}:
        raise ValueError(f"Optik cevap anahtari bilinmeyen kitapcik kodu verdi: {booklet_code}")

    answers = {str(index): normalize_answer(answer) for index, answer in decoded_sheet.get("answers", {}).items() if normalize_answer(answer)}
    decode_error = build_answer_key_decode_error(decoded_sheet)
    if decode_error:
        raise ValueError(decode_error)

    updated_exam = deepcopy(exam)
    scanned_booklets = deepcopy(updated_exam.get("optical_answer_key_booklets") or {})
    scanned_booklets[booklet_code] = answers
    updated_exam["optical_answer_key_booklets"] = scanned_booklets

    # When the answer key was previously built from optical reads, rebuild from
    # scratch so a corrected re-read (e.g. lower threshold on booklet C) can
    # replace the old partial set without hitting the "count != existing count"
    # guard.  For teacher-defined or uploaded answer keys, preserve existing
    # questions so the optical read only patches booklet mappings.
    source_type = (updated_exam.get("answer_key_profile") or {}).get("source_type", "")
    rebuild_from_scratch = source_type in ("", "optical-read")
    try:
        questions = build_questions_from_scanned_booklets(
            updated_exam.get("booklet_codes", []),
            scanned_booklets,
            existing_questions=[] if rebuild_from_scratch else (updated_exam.get("questions") or []),
        )
    except SynthesisPartialResult as partial:
        # All booklets stored; partial questions (min_count) keep the button active.
        questions = partial.questions
        updated_exam["_synthesis_warning"] = str(partial)
    except ValueError as build_err:
        # Kitapçık verisi yukarıda zaten kaydedildi; sentez fatal değil.
        questions = []
        updated_exam["_synthesis_warning"] = str(build_err)
    if questions:
        updated_exam["questions"] = questions

    ready_count = sum(1 for booklet in updated_exam.get("booklet_codes", []) if normalize_token(booklet) in scanned_booklets)
    existing_profile = deepcopy(updated_exam.get("answer_key_profile") or {})
    prep_method_code = str(updated_exam.get("prep_method_code") or "manual").strip() or "manual"
    booklet_count = len(updated_exam.get("booklet_codes", []))
    preserved_canonical_mapping_source = str(existing_profile.get("canonical_mapping_source") or "")
    if preserved_canonical_mapping_source not in EXPLICIT_METADATA_SOURCES:
        preserved_canonical_mapping_source = ""
    if not preserved_canonical_mapping_source and has_explicit_canonical_mapping_evidence(
        updated_exam,
        list(updated_exam.get("booklet_codes") or []),
        list(updated_exam.get("questions") or []),
    ):
        preserved_canonical_mapping_source = "explicit"

    preserved_weight_source = "explicit" if str(existing_profile.get("weight_source") or "") == "explicit" else ""
    if not preserved_weight_source and has_explicit_weight_evidence(
        updated_exam,
        list(updated_exam.get("questions") or []),
    ):
        preserved_weight_source = "explicit"
    metadata_source_file = existing_profile.get("metadata_source_file") or existing_profile.get("source_file")
    metadata_import_format = str(existing_profile.get("metadata_import_format") or existing_profile.get("import_format") or "manual")
    if metadata_import_format.endswith("+device-optical"):
        metadata_import_format = metadata_import_format[: -len("+device-optical")]

    if preserved_canonical_mapping_source or preserved_weight_source:
        existing_source_type = str(existing_profile.get("source_type") or "")
        hybrid_source_type = "hybrid-definition-optical" if existing_source_type in {"definition-file", "hybrid-definition-optical"} else "hybrid-metadata-optical"
        hybrid_source_label = "Excel metadata + operator optik cevap anahtari" if hybrid_source_type == "hybrid-definition-optical" else "Operator metadata + operator optik cevap anahtari"
        updated_exam["answer_key_profile"] = build_answer_key_profile(
            source_type=hybrid_source_type,
            source_label=hybrid_source_label,
            question_count=len(updated_exam.get("questions") or []),
            import_format=f"{metadata_import_format}+device-optical",
            booklet_strategy=str(existing_profile.get("booklet_strategy") or "manual"),
            source_file=source_file,
            canonical_mapping_source=preserved_canonical_mapping_source or ("single-booklet-sequential" if booklet_count == 1 else "inferred-sequential"),
            weight_source=preserved_weight_source or "defaulted",
            answer_source="optical",
        )
        if metadata_source_file:
            updated_exam["answer_key_profile"]["metadata_source_file"] = metadata_source_file
        if metadata_import_format:
            updated_exam["answer_key_profile"]["metadata_import_format"] = metadata_import_format
    else:
        updated_exam["answer_key_profile"] = build_answer_key_profile(
            source_type="optical-read",
            source_label="Operator optik cevap anahtari",
            question_count=len(updated_exam.get("questions") or []),
            import_format="device-optical",
            booklet_strategy="sequential",
            source_file=source_file,
            canonical_mapping_source="single-booklet-sequential" if booklet_count == 1 else "inferred-sequential",
            weight_source="defaulted",
            answer_source="optical",
        )
    updated_exam["answer_key_profile"]["detected_booklet_code"] = booklet_code
    updated_exam["answer_key_profile"]["ready_booklet_count"] = ready_count
    updated_exam["answer_key_profile"]["total_booklet_count"] = len(updated_exam.get("booklet_codes", []))
    updated_exam["answer_key_profile"]["pending_booklets"] = [
        normalize_token(booklet)
        for booklet in updated_exam.get("booklet_codes", [])
        if normalize_token(booklet) not in scanned_booklets
    ]
    return updated_exam


def infer_last_pending_booklet_for_decoded_sheets(
    exam: dict[str, Any],
    decoded_sheets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    known_booklets = {
        normalize_token(booklet)
        for booklet in (exam.get("optical_answer_key_booklets") or {}).keys()
        if normalize_token(booklet)
    }
    # Sadece bu toplu okumada YENİ tespit edilen kitapçıkları say;
    # zaten kayıtlı olanları (known) explicit_batch'e alma —  false-positive
    # tespitinin pending hesabını bozmasını önler.
    explicit_batch_booklets = {
        normalize_token(sheet.get("booklet_code"))
        for sheet in decoded_sheets
        if normalize_token(sheet.get("booklet_code"))
        and normalize_token(sheet.get("booklet_code")) not in known_booklets
    }
    pending_booklets = [
        normalize_token(booklet)
        for booklet in exam.get("booklet_codes", [])
        if normalize_token(booklet)
        and normalize_token(booklet) not in known_booklets
        and normalize_token(booklet) not in explicit_batch_booklets
    ]
    # "Atanmamış" = boş booklet_code VEYA zaten kayıtlı bir kitapçık kodu
    # (ikincisi, dikey-terslik gibi durumlarda false-positive detection'ı yakalar).
    unassigned_indexes = [
        index
        for index, sheet in enumerate(decoded_sheets)
        if (
            not normalize_token(sheet.get("booklet_code"))
            or normalize_token(sheet.get("booklet_code")) in known_booklets
        )
    ]

    if len(pending_booklets) != 1 or len(unassigned_indexes) != 1:
        return decoded_sheets

    unassigned_index = unassigned_indexes[0]
    unassigned_sheet = decoded_sheets[unassigned_index]
    if build_answer_key_decode_error(unassigned_sheet):
        return decoded_sheets

    inferred_sheets = deepcopy(decoded_sheets)
    inferred_sheet = deepcopy(unassigned_sheet)
    inferred_sheet["booklet_code"] = pending_booklets[0]
    inferred_warnings = list(inferred_sheet.get("warnings") or [])
    detected_code = normalize_token(unassigned_sheet.get("booklet_code"))
    if detected_code and detected_code in known_booklets:
        inferred_warnings.append(
            f"Kitapçık tespiti mevcut kayıtlı kitapçık ({detected_code}) ile çakıştı; "
            f"kalan tek eksik kitapçık {pending_booklets[0]} olarak materyalize edildi."
        )
    else:
        inferred_warnings.append(
            f"Kitapçık balonu zayıf kaldığı için form kalan tek eksik kitapçık {pending_booklets[0]} olarak materyalize edildi."
        )
    inferred_sheet["warnings"] = inferred_warnings
    inferred_sheets[unassigned_index] = inferred_sheet
    return inferred_sheets


def apply_optical_answer_keys(
    exam: dict[str, Any],
    decoded_sheets: list[dict[str, Any]],
    source_file: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    updated_exam = deepcopy(exam)
    processed_booklets: list[str] = []
    messages: list[str] = []
    decoded_sheets = infer_last_pending_booklet_for_decoded_sheets(updated_exam, decoded_sheets)

    for decoded_sheet in decoded_sheets:
        booklet_code = normalize_token(decoded_sheet.get("booklet_code"))
        if booklet_code and booklet_code in processed_booklets:
            messages.append(
                f"Form {decoded_sheet.get('sheet_no', 0)}: {booklet_code} kitapcigi ayni okumada birden fazla kez geldi; ilk cozum korundu."
            )
            continue

        try:
            updated_exam = apply_optical_answer_key(updated_exam, decoded_sheet, source_file)
        except ValueError as error:
            messages.append(f"Form {decoded_sheet.get('sheet_no', 0)}: {error}")
            continue

        # Kitapçık başarıyla kaydedildi; soru sentezi uyarısı varsa mesajlara ekle.
        synthesis_warning = updated_exam.pop("_synthesis_warning", None)
        booklet_code = normalize_token(decoded_sheet.get("booklet_code"))
        if booklet_code:
            processed_booklets.append(booklet_code)
        if synthesis_warning:
            messages.append(f"Form {decoded_sheet.get('sheet_no', 0)}: {synthesis_warning}")
        messages.extend(
            [f"Form {decoded_sheet.get('sheet_no', 0)}: {warning}" for warning in decoded_sheet.get("warnings", [])]
        )

    if not processed_booklets:
        raise ValueError(messages[0] if messages else "Optik cevap anahtari formu cihazdan okunamadi.")

    return updated_exam, processed_booklets, messages


def decode_exam_sheets(
    project_root: Path,
    exam: dict[str, Any],
    sheets: list[dict[str, Any]],
    threshold: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    template = parse_form_template(project_root, exam.get("form_template_id"))
    decoded_rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for sheet in sheets:
        decoded = decode_sheet(sheet, template, exam, threshold)
        low_confidence_error = build_low_confidence_decode_error(decoded, exam)
        if low_confidence_error:
            warnings.append(f"Form {decoded['sheet_no']}: {low_confidence_error}")
            continue
        if not decoded["booklet_code"]:
            warnings.append(f"Form {decoded['sheet_no']}: kitapcik kodu cozulemedi")
            continue
        warnings.extend([f"Form {decoded['sheet_no']}: {item}" for item in decoded.get("warnings", [])])
        decoded_rows.append(
            {
                "student_id": decoded["student_id"],
                "booklet_code": decoded["booklet_code"],
                "answers": decoded["answers"],
                "source_row": decoded["source_row"],
                "decoded_fields": decoded.get("decoded_fields", {}),
            }
        )

    if not decoded_rows and warnings:
        raise ValueError(warnings[0])
    return decoded_rows, warnings
