from __future__ import annotations

import csv
import io
import re
import unicodedata
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from openpyxl import load_workbook

from .exam_service import normalize_answer, normalize_token


QUESTION_RE = re.compile(r"^(?:Q|S|SORU)?\s*(\d+)$", re.IGNORECASE)
STUDENT_ID_HEADERS = {"student_id", "ogrenci_no", "ogrencino", "student", "id", "numara"}
BOOKLET_HEADERS = {"booklet_code", "booklet", "kitapcik", "kitapcik_kodu", "grup", "group"}
SUMMARY_REPORT_HEADERS = {"dogru", "yanlis", "neti", "puani"}
FIXED_WIDTH_ANSWER_RE = re.compile(r"([A-E\s]{5,})\s*$", re.IGNORECASE)
FIXED_WIDTH_STUDENT_ID_RE = re.compile(r"\d{5,}")


def normalize_header(value: Any) -> str:
    raw = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "_", raw).strip("_").lower()


def parse_question_headers(headers: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw_header in headers:
        match = QUESTION_RE.match(normalize_header(raw_header))
        if match:
            mapping[raw_header] = match.group(1)
    return mapping


def sniff_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ";" if sample.count(";") > sample.count(",") else ","


def decode_bytes(blob: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
        try:
            return blob.decode(encoding)
        except UnicodeDecodeError:
            continue
    return blob.decode("utf-8", errors="ignore")


def is_fixed_width_candidate(text: str) -> bool:
    first_line = next((line.strip("\ufeff") for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return False
    if any(delimiter in first_line for delimiter in (",", ";", "\t", "|")):
        return False
    return FIXED_WIDTH_ANSWER_RE.search(first_line) is not None


def read_text_rows(blob: bytes) -> list[dict[str, Any]]:
    decoded = decode_bytes(blob)
    reader = csv.DictReader(io.StringIO(decoded), delimiter=sniff_delimiter(decoded[:2048]))
    return list(reader)


def read_excel_rows(blob: bytes) -> list[dict[str, Any]]:
    workbook = load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
    sheet = workbook[workbook.sheetnames[0]]
    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    headers = [str(item or "").strip() for item in rows[0]]
    return [{headers[index]: raw_row[index] for index in range(len(headers))} for raw_row in rows[1:]]


def parse_fixed_width_vendor_rows(text: str, *, default_booklet_code: str = "") -> list[dict[str, Any]]:
    parsed_rows: list[dict[str, Any]] = []
    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if not line.strip():
            continue

        match = FIXED_WIDTH_ANSWER_RE.search(line)
        if not match:
            continue

        answer_blob = match.group(1).strip().upper()
        if not answer_blob:
            continue

        answers = {
            str(position): token
            for position, token in enumerate(answer_blob, start=1)
            if normalize_answer(token)
        }
        student_match = FIXED_WIDTH_STUDENT_ID_RE.search(line[: match.start()])
        parsed_rows.append(
            {
                "student_id": student_match.group(0) if student_match else f"SATIR-{index}",
                "booklet_code": normalize_token(default_booklet_code),
                "answers": answers,
                "question_count": len(answer_blob),
                "source_row": index,
            }
        )

    if not parsed_rows:
        raise ValueError("Header'siz sabit-genislik TXT icinde soru-cevap verisi bulunamadi.")
    return parsed_rows


def parse_tabular_student_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    headers = list(rows[0].keys())
    normalized_headers = {normalize_header(header): header for header in headers}
    question_headers = parse_question_headers(headers)
    if not question_headers:
        if SUMMARY_REPORT_HEADERS.issubset(set(normalized_headers.keys())):
            raise ValueError("Bu dosya soru-cevap exportu degil, ozet rapor. Import icin ogrenci cevap kolonlari gerekir.")
        raise ValueError("Soru kolonlari bulunamadi. Beklenen basliklar: Q1, Q2 veya S1, S2.")

    student_header = next((normalized_headers[key] for key in STUDENT_ID_HEADERS if key in normalized_headers), None)
    booklet_header = next((normalized_headers[key] for key in BOOKLET_HEADERS if key in normalized_headers), None)
    if not booklet_header:
        raise ValueError("Kitapcik kolonu bulunamadi. Beklenen basliklar: booklet_code, kitapcik veya grup.")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=2):
        parsed_rows.append(
            {
                "student_id": str(row.get(student_header) or f"SATIR-{index}").strip(),
                "booklet_code": normalize_token(row.get(booklet_header)),
                "answers": {position: normalize_answer(row.get(header)) for header, position in question_headers.items()},
                "source_row": index,
            }
        )
    return parsed_rows


def build_questions_from_mapping_rows(rows: list[dict[str, Any]], booklet_codes: list[str]) -> list[dict[str, Any]]:
    headers = list(rows[0].keys()) if rows else []
    normalized_headers = {normalize_header(header): header for header in headers}
    if "canonical_no" not in normalized_headers:
        raise ValueError("Detayli cevap anahtari dosyasinda canonical_no kolonu zorunludur.")

    questions: list[dict[str, Any]] = []
    for row in rows:
        canonical_no = int(row.get(normalized_headers["canonical_no"]) or 0)
        if canonical_no <= 0:
            raise ValueError("Detayli cevap anahtarinda canonical_no pozitif olmalidir.")

        question = {
            "canonical_no": canonical_no,
            "group_label": str(row.get(normalized_headers.get("group_label", ""), "") or "Genel").strip() or "Genel",
            "weight": float(row.get(normalized_headers.get("weight", ""), 1) or 1),
            "booklet_mappings": {},
        }

        for booklet_code in booklet_codes:
            position_key = f"{normalize_header(booklet_code)}_position"
            answer_key = f"{normalize_header(booklet_code)}_answer"
            if position_key not in normalized_headers or answer_key not in normalized_headers:
                raise ValueError(f"{booklet_code} kitapcigi icin position/answer kolonlari eksik.")

            question["booklet_mappings"][booklet_code] = {
                "position": int(row.get(normalized_headers[position_key]) or 0),
                "correct_answer": normalize_answer(row.get(normalized_headers[answer_key])),
            }

        questions.append(question)

    return questions


def build_questions_from_sequential_rows(rows: list[dict[str, Any]], booklet_codes: list[str]) -> list[dict[str, Any]]:
    headers = list(rows[0].keys()) if rows else []
    normalized_headers = {normalize_header(header): header for header in headers}
    booklet_header = next((normalized_headers[key] for key in BOOKLET_HEADERS if key in normalized_headers), None)
    if not booklet_header:
        raise ValueError("Sirali cevap anahtarinda booklet_code kolonu zorunludur.")

    question_headers = parse_question_headers(headers)
    answer_key_header = normalized_headers.get("answer_key")
    if not question_headers and not answer_key_header:
        raise ValueError("Sirali cevap anahtarinda Q1...Qn kolonlari veya answer_key kolonu gerekir.")

    expected_booklets = [normalize_token(code) for code in booklet_codes if normalize_token(code)]
    booklet_answers: dict[str, list[str]] = {}
    for row in rows:
        booklet_code = normalize_token(row.get(booklet_header))
        if booklet_code not in expected_booklets:
            continue

        if question_headers:
            ordered_headers = sorted(question_headers.items(), key=lambda item: int(item[1]))
            answers = [normalize_answer(row.get(header)) for header, _ in ordered_headers]
        else:
            answers = [normalize_answer(character) for character in str(row.get(answer_key_header) or "").strip().upper()]

        booklet_answers[booklet_code] = answers

    missing_booklets = [code for code in expected_booklets if code not in booklet_answers]
    if missing_booklets:
        raise ValueError(f"Sirali cevap anahtarinda eksik kitapcik satiri var: {', '.join(missing_booklets)}")

    lengths = {booklet: len(answers) for booklet, answers in booklet_answers.items()}
    if len(set(lengths.values())) != 1:
        detail = ", ".join(f"{booklet}={count}" for booklet, count in sorted(lengths.items()))
        raise ValueError(f"Sirali cevap anahtarinda kitapcik soru sayilari uyusmuyor: {detail}")

    question_count = next(iter(lengths.values()), 0)
    questions: list[dict[str, Any]] = []
    for canonical_no in range(1, question_count + 1):
        booklet_mappings: dict[str, dict[str, Any]] = {}
        for booklet_code in expected_booklets:
            correct_answer = booklet_answers[booklet_code][canonical_no - 1]
            if not correct_answer:
                raise ValueError(f"Sirali cevap anahtarinda {booklet_code} / Q{canonical_no} bos birakilamaz.")
            booklet_mappings[booklet_code] = {"position": canonical_no, "correct_answer": correct_answer}
        questions.append(
            {
                "canonical_no": canonical_no,
                "group_label": "Genel",
                "weight": 1,
                "booklet_mappings": booklet_mappings,
            }
        )
    return questions


def build_questions_from_fixed_width_answer_key(rows: list[dict[str, Any]], booklet_code: str) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("Sabit-genislik cevap anahtarinda gecerli satir bulunamadi.")

    answers = rows[0].get("answers") or {}
    question_count = int(rows[0].get("question_count") or 0)
    questions: list[dict[str, Any]] = []
    for canonical_no in range(1, question_count + 1):
        correct_answer = normalize_answer(answers.get(str(canonical_no)))
        if not correct_answer:
            raise ValueError(f"Sabit-genislik cevap anahtarinda Q{canonical_no} bos birakilamaz.")
        questions.append(
            {
                "canonical_no": canonical_no,
                "group_label": "Genel",
                "weight": 1,
                "booklet_mappings": {
                    normalize_token(booklet_code): {"position": canonical_no, "correct_answer": correct_answer}
                },
            }
        )
    return questions


async def parse_upload_file(upload: UploadFile) -> tuple[list[dict[str, Any]], str]:
    blob = await upload.read()
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        return parse_tabular_student_rows(read_excel_rows(blob)), "excel"

    decoded = decode_bytes(blob)
    if is_fixed_width_candidate(decoded):
        return parse_fixed_width_vendor_rows(decoded), "vendor-fixed"
    return parse_tabular_student_rows(read_text_rows(blob)), "text"


async def parse_answer_key_upload(upload: UploadFile, booklet_codes: list[str]) -> tuple[list[dict[str, Any]], str, str]:
    blob = await upload.read()
    suffix = Path(upload.filename or "").suffix.lower()
    normalized_booklets = [normalize_token(code) for code in booklet_codes if normalize_token(code)]

    if suffix in {".xlsx", ".xlsm"}:
        rows = read_excel_rows(blob)
    else:
        decoded = decode_bytes(blob)
        if is_fixed_width_candidate(decoded):
            if len(normalized_booklets) != 1:
                raise ValueError("Header'siz sabit-genislik cevap anahtari yalnizca tek kitapcikli sinavlarda kabul edilir.")
            fixed_rows = parse_fixed_width_vendor_rows(decoded, default_booklet_code=normalized_booklets[0])
            return (
                build_questions_from_fixed_width_answer_key(fixed_rows, normalized_booklets[0]),
                "answer-key-vendor-fixed",
                "sequential",
            )
        rows = read_text_rows(blob)

    if not rows:
        raise ValueError("Cevap anahtari dosyasinda islenecek satir bulunamadi.")

    headers = list(rows[0].keys())
    normalized_headers = {normalize_header(header): header for header in headers}
    if "canonical_no" in normalized_headers:
        return build_questions_from_mapping_rows(rows, normalized_booklets), "answer-key-mapping", "detailed"
    if any(key in normalized_headers for key in BOOKLET_HEADERS):
        return build_questions_from_sequential_rows(rows, normalized_booklets), "answer-key-sequential", "sequential"
    raise ValueError(
        "Cevap anahtari formati taninamadi. Detayli mapping icin canonical_no/A_position/A_answer; pratik format icin booklet_code ve Q1...Qn kullanin."
    )
