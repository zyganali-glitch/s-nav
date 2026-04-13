from __future__ import annotations

import csv
from datetime import datetime
import html
import io
import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .exam_service import enrich_session_for_reporting


WINDOWS_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
]
SECTION_FILL = PatternFill(fill_type="solid", fgColor="D9E8FF")
HEADER_FILL = PatternFill(fill_type="solid", fgColor="EEF4FF")
LTR_MARK = "\u200e"
LTR_SENSITIVE_COLUMNS = {"Sinif", "Form kodu", "Form tarihi"}
LTR_SENSITIVE_SUMMARY_LABELS = {"Sistem sinav kodu"}


def resolve_session(exam: dict[str, Any], session_id: str) -> dict[str, Any]:
    sessions = list(exam.get("sessions", []))
    if not sessions:
        raise ValueError("Export icin once bir sonuc oturumu olusmalidir.")
    if session_id == "latest":
        return enrich_session_for_reporting(exam, sessions[0])
    for session in sessions:
        if session.get("session_id") == session_id:
            return enrich_session_for_reporting(exam, session)
    raise ValueError("Istenen sonuc oturumu bulunamadi.")


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")
    if isinstance(value, list):
        return " | ".join(stringify(item) for item in value)
    if isinstance(value, dict):
        return " | ".join(f"{key}: {stringify(item)}" for key, item in value.items())
    return str(value)


def format_export_datetime(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone()
    return parsed.strftime("%d.%m.%Y %H:%M")


def stringify_export_value(section: dict[str, Any], row: list[Any], column_index: int) -> str:
    value = row[column_index] if column_index < len(row) else ""
    text = stringify(value)
    if not text:
        return ""

    column_name = section["columns"][column_index] if column_index < len(section["columns"]) else ""
    summary_label = stringify(row[0]) if row else ""
    should_force_ltr = column_name in LTR_SENSITIVE_COLUMNS or (
        section.get("title") == "Genel Ozet"
        and column_name == "Deger"
        and summary_label in LTR_SENSITIVE_SUMMARY_LABELS
    )
    if should_force_ltr and not text.startswith(LTR_MARK):
        return f"{LTR_MARK}{text}"
    return text


def build_section(title: str, columns: list[str], rows: list[list[Any]]) -> dict[str, Any]:
    return {"title": title, "columns": columns, "rows": rows}


def question_numbers_from_session(session: dict[str, Any]) -> list[int]:
    numbers = [int(item.get("canonical_no")) for item in (session.get("question_summary") or []) if item.get("canonical_no")]
    if numbers:
        return numbers
    first_student = next(iter(session.get("student_results") or []), None)
    if not first_student:
        return []
    return [int(item.get("canonical_no")) for item in first_student.get("question_responses") or [] if item.get("canonical_no")]


def response_lookup(student_row: dict[str, Any]) -> dict[int, str]:
    return {
        int(item.get("canonical_no")): stringify(item.get("display_value") or item.get("marked_answer") or "-(B)")
        for item in (student_row.get("question_responses") or [])
        if item.get("canonical_no") is not None
    }


def format_choice_distribution_cell(row: dict[str, Any], choice: str) -> str:
    distribution = (row.get("choice_distribution") or {}).get(choice) or {}
    count = distribution.get("count")
    rate = distribution.get("rate")
    if count in (None, "") and rate in (None, ""):
        return ""
    return f"{stringify(count)} / %{stringify(rate)}"


def build_methodology_rows(glossary: list[dict[str, Any]], commentary: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in commentary:
        rows.append([
            "Akademik yorum",
            str(item.get("title") or ""),
            str(item.get("text") or ""),
            "",
        ])
    for item in glossary:
        rows.append([
            "Metodoloji",
            str(item.get("term") or ""),
            str(item.get("how") or ""),
            " ".join(part for part in [str(item.get("why") or ""), str(item.get("value_use") or "")] if part).strip(),
        ])
    return rows


def build_report_sections(
    exam: dict[str, Any],
    session: dict[str, Any],
    *,
    response_chunk_size: int | None,
) -> list[dict[str, Any]]:
    summary = session.get("summary") or {}
    net_policy = session.get("net_policy") or {}
    highlights = session.get("assessment_highlights") or {}
    glossary = session.get("analysis_glossary") or []
    commentary = session.get("academic_commentary") or []
    student_rows = list(session.get("student_results") or session.get("student_preview") or [])

    sections: list[dict[str, Any]] = [
        build_section(
            "Genel Ozet",
            ["Alan", "Deger"],
            [
                ["Sistem sinav kodu", exam.get("exam_code", "")],
                ["Sinav basligi", exam.get("title", "")],
                ["Sinav yili", exam.get("exam_year", "")],
                ["Donem", exam.get("exam_term", "")],
                ["Sinav turu", exam.get("exam_type", "")],
                ["Olusturma", format_export_datetime(session.get("created_at", ""))],
                ["Import formati", session.get("import_format", "")],
                ["Net kurali", net_policy.get("label") or summary.get("net_policy_label") or "Belirtilmedi"],
                ["Ogrenci sayisi", summary.get("student_count", "")],
                ["Toplam soru", summary.get("total_questions", "")],
                ["Ortalama puan", summary.get("average_score", "")],
                ["Ortalama dogru", summary.get("average_correct_count", "")],
                ["Ortalama yanlis", summary.get("average_wrong_count", "")],
                ["Ortalama bos", summary.get("average_blank_count", "")],
                ["Ortalama net", summary.get("average_net_count", "")],
                ["Ortalama yuzde", summary.get("average_percent", "")],
                ["Tamamlama orani", summary.get("completion_rate", "")],
                ["Guvenirlik alpha", summary.get("reliability_alpha", "")],
                ["Standart sapma", summary.get("score_std_dev", "")],
                ["Atlanan satir", summary.get("skipped_rows", "")],
            ],
        ),
        build_section(
            "Sinava Ozel Akademik Yorum",
            ["Baslik", "Yorum"],
            [[item.get("title", ""), item.get("text", "")] for item in commentary],
        ),
        build_section(
            "Rapor Metodolojisi ve Terim Aciklamalari",
            ["Tur", "Gosterge", "Uretim ozeti", "Kullanim ve yorum"],
            build_methodology_rows(glossary, commentary),
        ),
        build_section(
            "Olcme Degerlendirme Uyarilari",
            ["Baslik", "Icerik"],
            [
                [
                    "En zor sorular",
                    " | ".join(
                        f"S{item.get('canonical_no')} (%{stringify(item.get('correct_rate'))})"
                        for item in highlights.get("hardest_questions", [])
                    ),
                ],
                [
                    "En kolay sorular",
                    " | ".join(
                        f"S{item.get('canonical_no')} (%{stringify(item.get('correct_rate'))})"
                        for item in highlights.get("easiest_questions", [])
                    ),
                ],
                [
                    "En cok bos birakilan sorular",
                    " | ".join(
                        f"S{item.get('canonical_no')} (%{stringify(item.get('blank_rate'))})"
                        for item in highlights.get("most_blank_questions", [])
                    ),
                ],
                [
                    "Ayirt ediciligi zayif sorular",
                    " | ".join(
                        f"S{item.get('canonical_no')} ({stringify(item.get('discrimination_index'))})"
                        for item in highlights.get("weak_discrimination_questions", [])
                    ),
                ],
                [
                    "En yuksek performans",
                    " | ".join(
                        f"#{item.get('exam_rank')} {stringify(item.get('student_id'))} {stringify(item.get('student_full_name'))}"
                        for item in highlights.get("top_students", [])
                    ),
                ],
                [
                    "En dusuk performans",
                    " | ".join(
                        f"#{item.get('exam_rank')} {stringify(item.get('student_id'))} {stringify(item.get('student_full_name'))}"
                        for item in highlights.get("lowest_students", [])
                    ),
                ],
            ],
        ),
        build_section(
            "Kitapcik Ozeti",
            [
                "Kitapcik",
                "Ogrenci",
                "Toplam puan",
                "Toplam D",
                "Toplam Y",
                "Toplam B",
                "Toplam net",
                "Ort. puan",
                "Maks.",
                "Ort. D",
                "Ort. Y",
                "Ort. B",
                "Ort. net",
                "Ort. dogruluk",
            ],
            [
                [
                    row.get("booklet_code", ""),
                    row.get("student_count", ""),
                    row.get("total_score", ""),
                    row.get("total_correct_count", ""),
                    row.get("total_wrong_count", ""),
                    row.get("total_blank_count", ""),
                    row.get("total_net_count", ""),
                    row.get("average_score", ""),
                    row.get("max_score", ""),
                    row.get("average_correct_count", ""),
                    row.get("average_wrong_count", ""),
                    row.get("average_blank_count", ""),
                    row.get("average_net_count", ""),
                    row.get("average_accuracy_percent", ""),
                ]
                for row in (session.get("booklet_summary") or [])
            ],
        ),
        build_section(
            "Grup Ozeti",
            [
                "Grup",
                "Ogrenci",
                "Soru",
                "Toplam puan",
                "Toplam D",
                "Toplam Y",
                "Toplam B",
                "Toplam net",
                "Maks.",
                "Ort. puan",
                "Ort. D",
                "Ort. Y",
                "Ort. B",
                "Ort. net",
                "Ort. dogruluk",
            ],
            [
                [
                    row.get("group_label", ""),
                    row.get("student_count", ""),
                    row.get("question_count", ""),
                    row.get("total_score", ""),
                    row.get("total_correct_count", ""),
                    row.get("total_wrong_count", ""),
                    row.get("total_blank_count", ""),
                    row.get("total_net_count", ""),
                    row.get("max_score", ""),
                    row.get("average_score", ""),
                    row.get("average_correct_count", ""),
                    row.get("average_wrong_count", ""),
                    row.get("average_blank_count", ""),
                    row.get("average_net_count", ""),
                    row.get("average_accuracy_percent", ""),
                ]
                for row in (session.get("group_summary") or [])
            ],
        ),
        build_section(
            "Soru Bazli Dagilim",
            [
                "Soru",
                "Grup",
                "Agirlik",
                "Dogru %",
                "Yanlis %",
                "Bos %",
                "Gucluk indeksi",
                "Madde varyansi",
                "Madde std sapmasi",
                "Nokta-cift serili r",
                "r yorumu",
                "Ust grup %",
                "Alt grup %",
                "Ayirt indeksi",
                "Gucluk",
                "Ayirt edicilik",
                "Kitapcik pozisyonlari",
                "Kitapcik cevap anahtari",
            ],
            [
                [
                    f"S{row.get('canonical_no')}",
                    row.get("group_label", ""),
                    row.get("weight", ""),
                    row.get("correct_rate", ""),
                    row.get("wrong_rate", ""),
                    row.get("blank_rate", ""),
                    row.get("difficulty_index", ""),
                    row.get("item_variance", ""),
                    row.get("item_std_dev", ""),
                    row.get("point_biserial", ""),
                    row.get("point_biserial_label", ""),
                    row.get("upper_group_correct_rate", ""),
                    row.get("lower_group_correct_rate", ""),
                    row.get("discrimination_index", ""),
                    row.get("difficulty_label", ""),
                    row.get("discrimination_label", ""),
                    row.get("booklet_positions", {}),
                    row.get("booklet_answer_key", {}),
                ]
                for row in (session.get("question_summary") or [])
            ],
        ),
        build_section(
            "Sorulara Siklara Gore Verilen Cevaplarin Dagilimi",
            [
                "Soru",
                "Grup",
                "Agirlik",
                "Ogrenci",
                "A",
                "B",
                "C",
                "D",
                "E",
                "Bos",
                "Dogru %",
                "Yanlis %",
                "Gucluk indeksi",
                "Madde varyansi",
                "Madde std sapmasi",
                "Nokta-cift serili r",
                "r yorumu",
                "Ust grup %",
                "Alt grup %",
                "Ayirt indeksi",
                "Gucluk",
                "Ayirt edicilik",
                "Kitapcik pozisyonlari",
                "Kitapcik cevap anahtari",
            ],
            [
                [
                    f"S{row.get('canonical_no')}",
                    row.get("group_label", ""),
                    row.get("weight", ""),
                    row.get("student_count", ""),
                    format_choice_distribution_cell(row, "A"),
                    format_choice_distribution_cell(row, "B"),
                    format_choice_distribution_cell(row, "C"),
                    format_choice_distribution_cell(row, "D"),
                    format_choice_distribution_cell(row, "E"),
                    f"{stringify((row.get('blank_distribution') or {}).get('count'))} / %{stringify((row.get('blank_distribution') or {}).get('rate'))}",
                    row.get("correct_rate", ""),
                    row.get("wrong_rate", ""),
                    row.get("difficulty_index", ""),
                    row.get("item_variance", ""),
                    row.get("item_std_dev", ""),
                    row.get("point_biserial", ""),
                    row.get("point_biserial_label", ""),
                    row.get("upper_group_correct_rate", ""),
                    row.get("lower_group_correct_rate", ""),
                    row.get("discrimination_index", ""),
                    row.get("difficulty_label", ""),
                    row.get("discrimination_label", ""),
                    row.get("booklet_positions", {}),
                    row.get("booklet_answer_key", {}),
                ]
                for row in (session.get("question_summary") or [])
            ],
        ),
        build_section(
            "Ogrenci Onizlemi",
            [
                "Ogrenci no",
                "Ad",
                "Soyad",
                "Ad Soyad",
                "Sinif",
                "Kitapcik",
                "Form kodu",
                "Form tarihi",
                "D",
                "Y",
                "B",
                "Net",
                "Toplam",
                "Genel sira",
                "Sinif sira",
                "Puan",
                "Yuzde",
            ],
            [
                [
                    row.get("student_id", ""),
                    row.get("student_name", ""),
                    row.get("student_surname", ""),
                    row.get("student_full_name", ""),
                    row.get("classroom", ""),
                    row.get("booklet_code", ""),
                    row.get("scanned_exam_code", ""),
                    row.get("scanned_exam_date", ""),
                    row.get("correct_count", ""),
                    row.get("wrong_count", ""),
                    row.get("blank_count", ""),
                    row.get("net_count", ""),
                    row.get("total_questions", ""),
                    row.get("exam_rank", ""),
                    row.get("class_rank", ""),
                    row.get("score", ""),
                    row.get("weighted_percent", ""),
                ]
                for row in student_rows
            ],
        ),
    ]

    question_numbers = question_numbers_from_session(session)
    if not question_numbers:
        return sections

    chunk_size = response_chunk_size or len(question_numbers)
    for start_index in range(0, len(question_numbers), chunk_size):
        question_chunk = question_numbers[start_index:start_index + chunk_size]
        columns = ["Genel sira", "Ogrenci no", "Ad Soyad", "Sinif", "Kitapcik"] + [f"S{number}" for number in question_chunk]
        rows: list[list[Any]] = []
        for student_row in student_rows:
            responses = response_lookup(student_row)
            rows.append(
                [
                    student_row.get("exam_rank", ""),
                    student_row.get("student_id", ""),
                    student_row.get("student_full_name", ""),
                    student_row.get("classroom", ""),
                    student_row.get("booklet_code", ""),
                    *[responses.get(number, "-(B)") for number in question_chunk],
                ]
            )
        sections.append(
            build_section(
                f"Ogrenci Cevap Matrisi S{question_chunk[0]}-S{question_chunk[-1]}",
                columns,
                rows,
            )
        )

    return sections


def section_to_dicts(section: dict[str, Any]) -> list[dict[str, Any]]:
    columns = section["columns"]
    return [{column: row[index] if index < len(row) else "" for index, column in enumerate(columns)} for row in section["rows"]]


def build_csv_bytes(exam: dict[str, Any], session: dict[str, Any]) -> bytes:
    sections = build_report_sections(exam, session, response_chunk_size=30)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for section in sections:
        writer.writerow(["Rapor Bolumu", section["title"]])
        writer.writerow(section["columns"])
        for row in section["rows"]:
            writer.writerow([stringify_export_value(section, row, index) for index in range(len(section["columns"]))])
        writer.writerow([])
    return buffer.getvalue().encode("utf-8-sig")


def build_json_bytes(exam: dict[str, Any], session: dict[str, Any]) -> bytes:
    sections = build_report_sections(exam, session, response_chunk_size=None)
    payload = {
        "exam": {
            "exam_code": exam.get("exam_code"),
            "title": exam.get("title"),
            "exam_year": exam.get("exam_year", ""),
            "exam_term": exam.get("exam_term", ""),
            "exam_type": exam.get("exam_type", ""),
            "booklet_codes": exam.get("booklet_codes", []),
            "question_count": len(exam.get("questions", [])),
        },
        "session": session,
        "report_blocks": [
            {
                "title": section["title"],
                "columns": section["columns"],
                "rows": section_to_dicts(section),
            }
            for section in sections
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def render_text_table(section: dict[str, Any]) -> str:
    rows = [
        [stringify_export_value(section, row, index) for index in range(len(section["columns"]))]
        for row in section["rows"]
    ]
    headers = [stringify(value) for value in section["columns"]]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def render_row(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    separator = "-+-".join("-" * width for width in widths)
    lines = [section["title"], separator, render_row(headers), separator]
    for row in rows:
        lines.append(render_row(row))
    lines.append(separator)
    return "\n".join(lines)


def build_txt_bytes(exam: dict[str, Any], session: dict[str, Any]) -> bytes:
    sections = build_report_sections(exam, session, response_chunk_size=20)
    content = "\n\n".join(render_text_table(section) for section in sections)
    return content.encode("utf-8")


def autosize_sheet(sheet) -> None:
    for column_cells in sheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            max_length = max(max_length, len(stringify(cell.value)))
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 42)


def write_section_to_sheet(sheet, section: dict[str, Any]) -> None:
    sheet.append([section["title"]])
    sheet[1][0].font = Font(bold=True, size=12)
    sheet[1][0].fill = SECTION_FILL
    sheet.append(section["columns"])
    for cell in sheet[2]:
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL
    for row in section["rows"]:
        sheet.append([stringify_export_value(section, row, index) for index in range(len(section["columns"]))])
    sheet.freeze_panes = "A3"
    autosize_sheet(sheet)


def build_xlsx_bytes(exam: dict[str, Any], session: dict[str, Any]) -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)
    sections = build_report_sections(exam, session, response_chunk_size=None)

    for section in sections:
        title = section["title"][:31] or "Rapor"
        sheet = workbook.create_sheet(title)
        write_section_to_sheet(sheet, section)

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def register_pdf_font() -> str:
    try:
        pdfmetrics.getFont("SessionExportFont")
        return "SessionExportFont"
    except KeyError:
        pass

    for font_path in WINDOWS_FONT_CANDIDATES:
        if font_path.exists():
            pdfmetrics.registerFont(TTFont("SessionExportFont", str(font_path)))
            return "SessionExportFont"
    return "Helvetica"


def build_pdf_paragraph(value: Any, style: ParagraphStyle) -> Paragraph:
    text = stringify(value).replace(" | ", "<br/>")
    safe_text = html.escape(text).replace("\n", "<br/>").replace("&lt;br/&gt;", "<br/>") or "-"
    return Paragraph(safe_text, style)


def compute_pdf_column_widths(section: dict[str, Any], available_width: float) -> list[float]:
    text_rows = [section["columns"], *[[stringify(value) for value in row] for row in section["rows"]]]
    estimated = []
    for index in range(len(section["columns"])):
        max_length = max(len(row[index]) if index < len(row) else 0 for row in text_rows)
        estimated.append(min(max(max_length, 8), 24))
    total = sum(estimated) or 1
    return [available_width * (value / total) for value in estimated]


def make_pdf_table(section: dict[str, Any], font_name: str, available_width: float) -> Table:
    column_count = max(len(section["columns"]), 1)
    if column_count <= 6:
        header_font_size = 8
        body_font_size = 7
    elif column_count <= 12:
        header_font_size = 7
        body_font_size = 6.5
    elif column_count <= 18:
        header_font_size = 6.5
        body_font_size = 6
    else:
        header_font_size = 6
        body_font_size = 5.4

    header_style = ParagraphStyle(
        "SessionExportHeader",
        fontName=font_name,
        fontSize=header_font_size,
        leading=header_font_size + 1,
        textColor=colors.HexColor("#1F2937"),
        wordWrap="CJK",
    )
    body_style = ParagraphStyle(
        "SessionExportBody",
        fontName=font_name,
        fontSize=body_font_size,
        leading=body_font_size + 1.5,
        wordWrap="CJK",
    )

    data = [
        [build_pdf_paragraph(value, header_style) for value in section["columns"]],
        *[
            [build_pdf_paragraph(stringify_export_value(section, row, index), body_style) for index in range(len(section["columns"]))]
            for row in section["rows"]
        ],
    ]
    table = Table(data, repeatRows=1, colWidths=compute_pdf_column_widths(section, available_width), splitByRow=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E8FF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#A3B1C6")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return table


def build_pdf_bytes(exam: dict[str, Any], session: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    font_name = register_pdf_font()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A3), leftMargin=18, rightMargin=18, topMargin=18, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles["Heading1"].fontName = font_name
    styles["Heading2"].fontName = font_name
    styles["Normal"].fontName = font_name

    story = [
        Paragraph(f"{stringify(exam.get('exam_code'))} - {stringify(exam.get('title'))}", styles["Heading1"]),
        Spacer(1, 12),
    ]

    for section in build_report_sections(exam, session, response_chunk_size=18):
        story.append(Paragraph(section["title"], styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(make_pdf_table(section, font_name, doc.width))
        story.append(Spacer(1, 12))

    doc.build(story)
    return buffer.getvalue()


def build_session_export(exam: dict[str, Any], session: dict[str, Any], export_format: str) -> tuple[bytes, str, str]:
    format_name = export_format.strip().lower()
    base_name = f"{exam.get('exam_code', 'sinav')}_{session.get('session_id', 'oturum')}"
    if format_name == "csv":
        return build_csv_bytes(exam, session), "text/csv; charset=utf-8", f"{base_name}.csv"
    if format_name == "txt":
        return build_txt_bytes(exam, session), "text/plain; charset=utf-8", f"{base_name}.txt"
    if format_name == "xlsx":
        return build_xlsx_bytes(exam, session), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"{base_name}.xlsx"
    if format_name == "pdf":
        return build_pdf_bytes(exam, session), "application/pdf", f"{base_name}.pdf"
    if format_name == "json":
        return build_json_bytes(exam, session), "application/json; charset=utf-8", f"{base_name}.json"
    raise ValueError("Desteklenmeyen export formati. Beklenen: csv, txt, xlsx, pdf, json.")