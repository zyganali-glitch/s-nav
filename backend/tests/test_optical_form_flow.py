from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.optical_form_service import (
    decode_sheet,
    get_answer_regions,
    get_named_field_regions,
    parse_form_template,
    relaxed_candidate_is_safe,
)


ANSWER_BLOCKS = [
    (36, 65, 26, "EDCBA"),
    (36, 65, 20, "EDCBA"),
    (36, 65, 14, "EDCBA"),
    (36, 45, 8, "EDCBA"),
]
TIP_ANSWER_BLOCKS = [
    (34, 63, 38, "EDCBA"),
    (34, 63, 32, "EDCBA"),
    (34, 63, 26, "EDCBA"),
    (34, 63, 20, "EDCBA"),
    (34, 63, 14, "EDCBA"),
    (34, 63, 8, "EDCBA"),
    (34, 63, 2, "EDCBA"),
]
BOOKLET_REGION = (37, 36, "D C B A")
STUDENT_NUMBER_REGION = (23, 32, 35, "0123456789")


def build_single_booklet_exam_payload() -> dict[str, object]:
    return {
        "exam_code": "optik01",
        "title": "Optik Cihaz Testi",
        "description": "Operator optik cevap anahtari akisi",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A"],
        "questions": [],
    }


def build_multi_booklet_exam_payload() -> dict[str, object]:
    return {
        "exam_code": "optik02",
        "title": "Cok Kitapcikli Optik",
        "description": "A ve B kitapcikli optik akisi",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A", "B"],
        "questions": [],
    }


def build_four_booklet_exam_payload() -> dict[str, object]:
    return {
        "exam_code": "optik04",
        "title": "Dort Kitapcikli Optik",
        "description": "A, B, C, D kitapcikli optik akis",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A", "B", "C", "D"],
        "questions": [],
    }


def build_matrix(answer_key: str, booklet_code: str = "A", marked_value: int = 16) -> list[list[int]]:
    matrix = [[0 for _ in range(48)] for _ in range(65)]

    booklet_row, booklet_start_column, booklet_pattern = BOOKLET_REGION
    booklet_index = booklet_pattern.index(booklet_code)
    matrix[booklet_row - 1][booklet_start_column - 1 + booklet_index] = marked_value

    for position, answer in enumerate(answer_key, start=1):
        remaining = position
        for start_row, end_row, start_column, pattern in ANSWER_BLOCKS:
            block_size = end_row - start_row + 1
            if remaining > block_size:
                remaining -= block_size
                continue
            column_offset = pattern.index(answer)
            matrix[start_row - 1 + remaining - 1][start_column - 1 + column_offset] = marked_value
            break

    return matrix


def build_matrix_with_positions(
    row_count: int,
    answer_blocks: list[tuple[int, int, int, str]],
    marked_positions: list[tuple[int, str]],
    marked_value: int = 16,
) -> list[list[int]]:
    matrix = [[0 for _ in range(48)] for _ in range(row_count)]

    for position, answer in marked_positions:
        remaining = position
        for start_row, end_row, start_column, pattern in answer_blocks:
            block_size = end_row - start_row + 1
            if remaining > block_size:
                remaining -= block_size
                continue
            column_offset = pattern.index(answer)
            matrix[start_row - 1 + remaining - 1][start_column - 1 + column_offset] = marked_value
            break

    return matrix


def mark_student_number(matrix: list[list[int]], student_number: str, marked_value: int = 16) -> list[list[int]]:
    start_row, end_row, start_column, pattern = STUDENT_NUMBER_REGION
    assert end_row - start_row + 1 == len(pattern)

    for offset, digit in enumerate(student_number[:11]):
        row_offset = pattern.index(digit)
        reverse_offset = 10 - offset
        matrix[start_row - 1 + row_offset][start_column - 1 + reverse_offset] = marked_value
    return matrix


def mark_vertical_field(
    matrix: list[list[int]],
    *,
    start_row: int,
    start_column: int,
    value: str,
    pattern: str,
    reverse_columns: bool = False,
    marked_value: int = 16,
) -> list[list[int]]:
    text = value[: len(value)]
    for offset, token in enumerate(text):
        if token not in pattern:
            continue
        row_offset = pattern.index(token)
        column_offset = len(text) - 1 - offset if reverse_columns else offset
        matrix[start_row - 1 + row_offset][start_column - 1 + column_offset] = marked_value
    return matrix


def flip_matrix_vertical(matrix: list[list[int]]) -> list[list[int]]:
    return list(reversed(matrix))


def build_raw_text(matrices: list[list[list[int]]]) -> str:
    sections = []
    for sheet_no, matrix in enumerate(matrices, start=1):
        rows = [",".join(str(cell) for cell in row) for row in matrix]
        sections.append(
            "\n".join(
                [
                    f"[sheet_{sheet_no}]",
                    "front_rows=65",
                    "front_columns=48",
                    "front_type=0",
                    "front_marks=",
                    *rows,
                    f"[/sheet_{sheet_no}]",
                ]
            )
        )
    return "\n".join(sections)


def build_device_payload(raw_text: str, sheet_count: int) -> dict[str, object]:
    return {
        "raw_text": raw_text,
        "analysis_text": f"Toplam form: {sheet_count}",
        "metadata": {
            "sheet_count": sheet_count,
            "sheets": [{"sheet_no": index + 1} for index in range(sheet_count)],
            "settings": {"analysis_threshold": 12},
        },
        "helper_output": "ok",
    }


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "app_state.json")
    return TestClient(app)


def test_decode_sheet_reads_answers_from_varsayilan_template() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("ABCDE", booklet_code="A")
    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["booklet_code"] == "A"
    assert decoded["answers"]["1"] == "A"
    assert decoded["answers"]["2"] == "B"
    assert decoded["answers"]["5"] == "E"


def test_decode_sheet_auto_corrects_vertical_flip_when_it_restores_q1_alignment() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = flip_matrix_vertical(build_matrix("ABCDE", booklet_code="B"))
    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A", "B", "C", "D"]},
        threshold=12,
    )

    assert decoded["matrix_orientation"] == "flip_vertical"
    assert decoded["matrix_orientation_corrected"] is True
    assert decoded["booklet_code"] == "B"
    assert decoded["answers"]["1"] == "A"
    assert decoded["answers"]["5"] == "E"


def test_decode_sheet_relaxes_threshold_when_it_recovers_booklet_without_more_answers() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("ABCDE", booklet_code="B")
    booklet_row, booklet_start_column, booklet_pattern = BOOKLET_REGION
    booklet_index = booklet_pattern.index("B")
    matrix[booklet_row - 1][booklet_start_column - 1 + booklet_index] = 11

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A", "B", "C", "D"]},
        threshold=12,
    )

    assert decoded["booklet_code"] == "B"
    assert decoded["decoded_question_count"] == 5
    assert decoded["analysis_threshold_used"] == 11
    assert any("Analiz esigi 11'e dusurulerek zayif isaretler geri kazanildi." in warning for warning in decoded["warnings"])


def test_decode_sheet_accepts_single_faint_answer_mark() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("ABCDE", booklet_code="A")

    start_row, _, start_column, pattern = ANSWER_BLOCKS[0]
    matrix[start_row - 1 + 2][start_column - 1 + pattern.index("C")] = 11

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["answers"]["3"] == "C"


def test_decode_sheet_blanks_adjacent_near_tie_instead_of_silent_wrong_answer() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("AACDE", booklet_code="A")

    start_row, _, start_column, pattern = ANSWER_BLOCKS[0]
    question_row = start_row - 1 + 2
    matrix[question_row][start_column - 1 + pattern.index("C")] = 11
    matrix[question_row][start_column - 1 + pattern.index("B")] = 12

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert "3" not in decoded["answers"]
    assert any("komsu siklar" in warning for warning in decoded["warnings"])


def test_relaxed_candidate_cannot_override_existing_answer_or_booklet() -> None:
    base_candidate = {"booklet_code": "C", "answers": {"3": "C", "4": "D"}}
    conflicting_relaxed = {"booklet_code": "B", "answers": {"3": "B", "4": "D", "5": "A"}}
    additive_relaxed = {"booklet_code": "C", "answers": {"3": "C", "4": "D", "5": "A"}}

    assert relaxed_candidate_is_safe(base_candidate, conflicting_relaxed) is False
    assert relaxed_candidate_is_safe(base_candidate, additive_relaxed) is True


def test_decode_sheet_extracts_student_number_from_vertical_digit_block() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("ABCDE", booklet_code="A")
    mark_student_number(matrix, "12345678901")
    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["student_id"] == "12345678901"
    assert decoded["decoded_fields"]["student_number"] == "12345678901"


def test_decode_sheet_extracts_auxiliary_identity_fields_from_named_regions() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")
    mark_student_number(matrix, "12345678901")
    mark_vertical_field(
        matrix,
        start_row=named_regions["student_name"]["start_row"],
        start_column=named_regions["student_name"]["start_column"],
        value="ALI",
        pattern="".join(named_regions["student_name"]["choices"]),
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["student_surname"]["start_row"],
        start_column=named_regions["student_surname"]["start_column"],
        value="VELI",
        pattern="".join(named_regions["student_surname"]["choices"]),
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["class_number"]["start_row"],
        start_column=named_regions["class_number"]["start_column"],
        value="0012",
        pattern="".join(named_regions["class_number"]["choices"]),
        reverse_columns=True,
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["decoded_fields"]["student_name"] == "ALI"
    assert decoded["decoded_fields"]["student_surname"] == "VELI"
    assert decoded["decoded_fields"]["student_full_name"] == "ALI VELI"
    assert named_regions["class_number"]["end_column"] == 34
    assert decoded["decoded_fields"]["class_number"] == "0012"
    assert "class_section" not in decoded["decoded_fields"]
    assert decoded["decoded_fields"]["classroom"] == "0012"


def test_decode_sheet_extracts_exam_code_and_exam_date_from_auxiliary_blocks() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")

    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_code_prefix"]["start_row"],
        start_column=named_regions["exam_code_prefix"]["start_column"],
        value="A",
        pattern="".join(named_regions["exam_code_prefix"]["choices"]),
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_code_number"]["start_row"],
        start_column=named_regions["exam_code_number"]["start_column"],
        value="601",
        pattern="".join(named_regions["exam_code_number"]["choices"]),
        reverse_columns=True,
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_day"]["start_row"],
        start_column=named_regions["exam_date_day"]["start_column"],
        value="09",
        pattern="".join(named_regions["exam_date_day"]["choices"]),
        reverse_columns=True,
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_month"]["start_row"],
        start_column=named_regions["exam_date_month"]["start_column"],
        value="04",
        pattern="".join(named_regions["exam_date_month"]["choices"]),
        reverse_columns=True,
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_year"]["start_row"],
        start_column=named_regions["exam_date_year"]["start_column"],
        value="2026",
        pattern="".join(named_regions["exam_date_year"]["choices"]),
        reverse_columns=True,
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert named_regions["exam_code_prefix"]["start_column"] == 45
    assert named_regions["exam_code_number"]["start_column"] == 42
    assert named_regions["exam_date_year"]["start_column"] == 33
    assert named_regions["exam_date_day"]["start_column"] == 39
    assert decoded["decoded_fields"]["exam_code_prefix"] == "A"
    assert decoded["decoded_fields"]["exam_code_number"] == "601"
    assert decoded["decoded_fields"]["exam_code"] == "A601"
    assert decoded["decoded_fields"]["exam_date_day"] == "09"
    assert decoded["decoded_fields"]["exam_date_month"] == "04"
    assert decoded["decoded_fields"]["exam_date_year"] == "2026"
    assert decoded["decoded_fields"]["exam_date"] == "09.04.2026"


def test_decode_sheet_recovers_exam_date_when_single_year_digit_is_faint() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")

    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_day"]["start_row"],
        start_column=named_regions["exam_date_day"]["start_column"],
        value="11",
        pattern="".join(named_regions["exam_date_day"]["choices"]),
        reverse_columns=True,
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_month"]["start_row"],
        start_column=named_regions["exam_date_month"]["start_column"],
        value="01",
        pattern="".join(named_regions["exam_date_month"]["choices"]),
        reverse_columns=True,
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["exam_date_year"]["start_row"],
        start_column=named_regions["exam_date_year"]["start_column"],
        value="1990",
        pattern="".join(named_regions["exam_date_year"]["choices"]),
        reverse_columns=True,
    )

    faint_year_row = named_regions["exam_date_year"]["end_row"]
    faint_year_column = named_regions["exam_date_year"]["start_column"] + 2
    matrix[faint_year_row - 1][faint_year_column - 1] = 11

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["decoded_fields"]["exam_date_year"] == "1990"
    assert decoded["decoded_fields"]["exam_date"] == "11.01.1990"


def test_decode_sheet_does_not_soft_guess_classroom_from_weak_marks() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    matrix = build_matrix("ABCDE", booklet_code="A")

    named_regions = get_named_field_regions(template)
    mark_vertical_field(
        matrix,
        start_row=named_regions["class_number"]["start_row"],
        start_column=named_regions["class_number"]["start_column"],
        value="0012",
        pattern="".join(named_regions["class_number"]["choices"]),
        reverse_columns=True,
        marked_value=11,
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert "class_number" not in decoded["decoded_fields"]
    assert "classroom" not in decoded["decoded_fields"]


def test_default_template_maps_surname_block_before_name_block() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")

    named_regions = get_named_field_regions(template)

    assert named_regions["student_surname"]["start_column"] == 6
    assert named_regions["student_name"]["start_column"] == 19


def test_decode_sheet_preserves_turkish_characters_in_named_regions() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")
    mark_student_number(matrix, "12345678901")
    mark_vertical_field(
        matrix,
        start_row=named_regions["student_name"]["start_row"],
        start_column=named_regions["student_name"]["start_column"],
        value="ÇAĞLA",
        pattern="".join(named_regions["student_name"]["choices"]),
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["student_surname"]["start_row"],
        start_column=named_regions["student_surname"]["start_column"],
        value="ŞİMŞEK",
        pattern="".join(named_regions["student_surname"]["choices"]),
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["decoded_fields"]["student_name"] == "ÇAĞLA"
    assert decoded["decoded_fields"]["student_surname"] == "ŞİMŞEK"
    assert decoded["decoded_fields"]["student_full_name"] == "ÇAĞLA ŞİMŞEK"


def test_decode_sheet_can_read_name_blocks_coded_right_to_left() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")
    mark_student_number(matrix, "12345678901")
    name_pattern = "".join(named_regions["student_name"]["choices"])
    surname_pattern = "".join(named_regions["student_surname"]["choices"])
    for offset, token in enumerate("ALI"):
        row_offset = name_pattern.index(token)
        column_offset = named_regions["student_name"]["column_count"] - 1 - offset
        matrix[named_regions["student_name"]["start_row"] - 1 + row_offset][named_regions["student_name"]["start_column"] - 1 + column_offset] = 16
    for offset, token in enumerate("VELI"):
        row_offset = surname_pattern.index(token)
        column_offset = named_regions["student_surname"]["column_count"] - 1 - offset
        matrix[named_regions["student_surname"]["start_row"] - 1 + row_offset][named_regions["student_surname"]["start_column"] - 1 + column_offset] = 16

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["decoded_fields"]["student_name"] == "ALI"
    assert decoded["decoded_fields"]["student_surname"] == "VELI"
    assert any("sagdan-sola kolon cozumlemesi" in warning for warning in decoded["warnings"])


def test_decode_sheet_tolerates_one_row_shift_in_name_blocks_when_upper_band_is_noisy() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "varsayilan")
    named_regions = get_named_field_regions(template)
    matrix = build_matrix("ABCDE", booklet_code="A")
    mark_student_number(matrix, "12345678901")

    for column_offset in range(3):
        matrix[named_regions["student_name"]["start_row"] - 1][named_regions["student_name"]["start_column"] - 1 + column_offset] = 16

    mark_vertical_field(
        matrix,
        start_row=named_regions["student_name"]["start_row"] + 1,
        start_column=named_regions["student_name"]["start_column"],
        value="ALI",
        pattern="".join(named_regions["student_name"]["choices"]),
    )
    mark_vertical_field(
        matrix,
        start_row=named_regions["student_surname"]["start_row"] + 1,
        start_column=named_regions["student_surname"]["start_column"],
        value="VELI",
        pattern="".join(named_regions["student_surname"]["choices"]),
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["decoded_fields"]["student_name"] == "ALI"
    assert decoded["decoded_fields"]["student_surname"] == "VELI"
    assert any("satir ofseti +1" in warning for warning in decoded["warnings"])


def test_decode_sheet_does_not_promote_unknown_numeric_region_to_student_number() -> None:
    matrix = [[0 for _ in range(48)] for _ in range(65)]
    for offset, digit in enumerate("12345678"):
        matrix[int(digit) - 1 if digit != "0" else 9][offset] = 16

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        {
            "regions": [
                {
                    "index": 1,
                    "start_row": 1,
                    "end_row": 10,
                    "start_column": 1,
                    "end_column": 8,
                    "row_count": 10,
                    "column_count": 8,
                    "axis": "D",
                    "pattern": "0123456789",
                    "region_type": "T",
                    "choices": list("0123456789"),
                }
            ],
            "template": {"id": "synthetic-unknown"},
        },
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    assert decoded["student_id"] == "FORM-001"
    assert decoded["decoded_fields"] == {}


def test_explicit_coordinate_source_covers_left_bottom_answer_blocks_for_tip_template() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = parse_form_template(project_root, "katipcel-tip")
    matrix = build_matrix_with_positions(
        63,
        TIP_ANSWER_BLOCKS,
        [(1, "A"), (31, "B"), (61, "C"), (91, "D"), (121, "E"), (151, "A"), (181, "B")],
    )

    decoded = decode_sheet(
        {"sheet_no": 1, "front_matrix": matrix},
        template,
        {"booklet_codes": ["A"]},
        threshold=12,
    )

    named_blocks = [region["semantic_name"] for region in get_answer_regions(template)]
    assert named_blocks == [
        "answer_block_1",
        "answer_block_2",
        "answer_block_3",
        "answer_block_4",
        "answer_block_5",
        "answer_block_6",
        "answer_block_7",
    ]
    assert decoded["answers"]["1"] == "A"
    assert decoded["answers"]["31"] == "B"
    assert decoded["answers"]["61"] == "C"
    assert decoded["answers"]["91"] == "D"
    assert decoded["answers"]["121"] == "E"
    assert decoded["answers"]["151"] == "A"
    assert decoded["answers"]["181"] == "B"


def test_device_answer_key_endpoint_materializes_single_booklet_answer_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    save_response = client.post("/api/exams", json=build_single_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([build_matrix("ABCDE")])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK01/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 200

    exam = response.json()["exam"]
    assert exam["summary"]["question_count"] == 5
    assert exam["answer_key_profile"]["source_type"] == "optical-read"
    assert exam["questions"][0]["booklet_mappings"]["A"]["correct_answer"] == "A"


def test_device_import_endpoint_scores_using_optically_scanned_answer_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    save_response = client.post("/api/exams", json=build_single_booklet_exam_payload())
    assert save_response.status_code == 200

    answer_key_raw = build_raw_text([build_matrix("ABCDE")])
    student_raw = build_raw_text([build_matrix("ABCED")])
    payloads = [build_device_payload(answer_key_raw, 1), build_device_payload(student_raw, 1)]

    def fake_read_mark_sheet(*args, **kwargs):
        return payloads.pop(0)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    key_response = client.post("/api/exams/OPTIK01/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert key_response.status_code == 200

    import_response = client.post("/api/exams/OPTIK01/device-import", json={"settings": {"analysis_threshold": 12}})
    assert import_response.status_code == 200

    session = import_response.json()["session"]
    assert session["import_format"] == "device-matrix"
    assert session["summary"]["student_count"] == 1
    assert session["student_results"][0]["correct_count"] == 3
    assert session["student_results"][0]["wrong_count"] == 2
    assert session["student_results"][0]["net_count"] == 2.5
    assert session["student_results"][0]["score"] == 3.0


def test_device_import_endpoint_accepts_previously_captured_raw_matrix_without_rereading_device(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_single_booklet_exam_payload())
    assert save_response.status_code == 200

    answer_key_raw = build_raw_text([build_matrix("ABCDE")])
    student_raw = build_raw_text([build_matrix("ABCED")])
    payloads = [build_device_payload(answer_key_raw, 1)]

    def fake_read_mark_sheet(*args, **kwargs):
        if payloads:
            return payloads.pop(0)
        raise AssertionError("read_mark_sheet should not be called when raw_text is provided")

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    key_response = client.post("/api/exams/OPTIK01/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert key_response.status_code == 200

    import_response = client.post(
        "/api/exams/OPTIK01/device-import",
        json={"settings": {"analysis_threshold": 12}, "raw_text": student_raw},
    )
    assert import_response.status_code == 200

    session = import_response.json()["session"]
    assert session["import_format"] == "device-matrix"
    assert session["summary"]["student_count"] == 1
    assert session["student_preview"][0]["score"] == 3.0


def test_device_endpoints_accept_form_template_override_and_keep_decoded_student_number(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_single_booklet_exam_payload())
    assert save_response.status_code == 200

    answer_key_raw = build_raw_text([build_matrix("ABCDE")])
    student_matrix = build_matrix("ABCDE")
    mark_student_number(student_matrix, "12345678901")
    student_raw = build_raw_text([student_matrix])
    payloads = [build_device_payload(answer_key_raw, 1), build_device_payload(student_raw, 1)]

    def fake_read_mark_sheet(*args, **kwargs):
        return payloads.pop(0)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    key_response = client.post(
        "/api/exams/OPTIK01/device-answer-key",
        json={"settings": {"analysis_threshold": 12}, "form_template_id": "katipcelebi"},
    )
    assert key_response.status_code == 200
    assert key_response.json()["exam"]["summary"]["form_template_id"] == "katipcelebi"

    import_response = client.post(
        "/api/exams/OPTIK01/device-import",
        json={"settings": {"analysis_threshold": 12}, "form_template_id": "katipcelebi"},
    )
    assert import_response.status_code == 200

    session = import_response.json()["session"]
    assert session["student_results"][0]["student_id"] == "12345678901"


def test_multi_booklet_optical_answer_key_can_be_stored_partially_until_all_booklets_arrive(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([build_matrix("ABCDE", booklet_code="A")])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 200

    exam = response.json()["exam"]
    assert exam["summary"]["question_count"] == 0
    assert exam["summary"]["optical_answer_key_ready_count"] == 1
    assert exam["answer_key_profile"]["pending_booklets"] == ["B"]


def test_device_answer_key_endpoint_materializes_last_pending_booklet_when_only_one_unassigned_sheet_remains(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_four_booklet_exam_payload())
    assert save_response.status_code == 200

    partial_raw = build_raw_text([
        build_matrix("ABCDE", booklet_code="A"),
        build_matrix("BCDEA", booklet_code="B"),
        build_matrix("CDEAB", booklet_code="C"),
    ])
    last_matrix = build_matrix("DEABC", booklet_code="D")
    booklet_row, booklet_start_column, booklet_pattern = BOOKLET_REGION
    for index in range(len(booklet_pattern.replace(" ", ""))):
        last_matrix[booklet_row - 1][booklet_start_column - 1 + index] = 0
    last_raw = build_raw_text([last_matrix])
    payloads = [build_device_payload(partial_raw, 3), build_device_payload(last_raw, 1)]

    def fake_read_mark_sheet(*args, **kwargs):
        return payloads.pop(0)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    partial_response = client.post(
        "/api/exams/OPTIK04/device-answer-key",
        json={"settings": {"analysis_threshold": 12, "max_sheets": 0}},
    )
    assert partial_response.status_code == 200
    assert partial_response.json()["exam"]["answer_key_profile"]["pending_booklets"] == ["D"]

    final_response = client.post("/api/exams/OPTIK04/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert final_response.status_code == 200

    payload = final_response.json()
    assert payload["processed_booklets"] == ["D"]
    assert payload["exam"]["summary"]["question_count"] == 5
    assert payload["exam"]["answer_key_profile"]["pending_booklets"] == []
    assert payload["exam"]["questions"][0]["booklet_mappings"]["D"]["correct_answer"] == "D"
    assert any("kalan tek eksik kitapçık D" in message for message in payload["answer_key_messages"])


def test_device_answer_key_endpoint_accepts_vertically_reversed_sheet_by_auto_orientation(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([flip_matrix_vertical(build_matrix("ABCDE", booklet_code="B"))])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 200

    payload = response.json()
    assert payload["processed_booklets"] == ["B"]
    assert payload["decoded_sheets"][0]["matrix_orientation"] == "flip_vertical"
    assert payload["decoded_sheets"][0]["warnings"][-1] == "Form matrisi dikey terslik algilanarak cozuldu."


def test_device_answer_key_endpoint_reads_multiple_booklets_in_single_pass(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([
        build_matrix("ABCDE", booklet_code="A"),
        build_matrix("BCDEA", booklet_code="B"),
    ])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 2)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12, "max_sheets": 0}})
    assert response.status_code == 200

    payload = response.json()
    exam = payload["exam"]
    assert payload["processed_booklets"] == ["A", "B"]
    assert exam["summary"]["question_count"] == 5
    assert exam["summary"]["optical_answer_key_ready_count"] == 2
    assert exam["questions"][0]["booklet_mappings"]["A"]["correct_answer"] == "A"
    assert exam["questions"][0]["booklet_mappings"]["B"]["correct_answer"] == "B"


def test_device_answer_key_endpoint_defaults_max_sheets_to_total_booklet_count_when_unset(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_four_booklet_exam_payload())
    assert save_response.status_code == 200

    captured_settings: list[dict[str, object]] = []
    raw_text = build_raw_text([build_matrix("ABCDE", booklet_code="A")])

    def fake_read_mark_sheet(*args, **kwargs):
        captured_settings.append(dict(kwargs.get("settings") or {}))
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK04/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 200
    assert captured_settings[0]["max_sheets"] == 4


def test_device_answer_key_endpoint_defaults_max_sheets_to_remaining_pending_booklets(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    captured_settings: list[dict[str, object]] = []
    payloads = [
        build_device_payload(build_raw_text([build_matrix("ABCDE", booklet_code="A")]), 1),
        build_device_payload(build_raw_text([build_matrix("BCDEA", booklet_code="B")]), 1),
    ]

    def fake_read_mark_sheet(*args, **kwargs):
        captured_settings.append(dict(kwargs.get("settings") or {}))
        return payloads.pop(0)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    first_response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert first_response.status_code == 200
    assert captured_settings[0]["max_sheets"] == 2
    assert first_response.json()["exam"]["answer_key_profile"]["pending_booklets"] == ["B"]

    second_response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert second_response.status_code == 200
    assert captured_settings[1]["max_sheets"] == 1


def test_device_answer_key_endpoint_accepts_multi_select_booklet_filter_subset(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([build_matrix("BCDEA", booklet_code="B")])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post(
        "/api/exams/OPTIK02/device-answer-key",
        json={"settings": {"analysis_threshold": 12}, "booklet_codes": ["B"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_booklets"] == ["B"]


def test_device_answer_key_endpoint_rejects_booklet_outside_selected_filter(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    raw_text = build_raw_text([build_matrix("ABCDE", booklet_code="A")])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post(
        "/api/exams/OPTIK02/device-answer-key",
        json={"settings": {"analysis_threshold": 12}, "booklet_codes": ["B"]},
    )
    assert response.status_code == 400
    assert "secili filtre disinda" in response.json()["detail"]


def test_device_answer_key_endpoint_relaxes_threshold_for_weak_mark_d_booklet(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post(
        "/api/exams",
        json={
            **build_four_booklet_exam_payload(),
            "title": "Zayif D Kitapcigi",
            "description": "Threshold fallback testi",
        },
    )
    assert save_response.status_code == 200

    weak_d_matrix = build_matrix("EDDEC", booklet_code="D", marked_value=11)
    booklet_row, booklet_start_column, booklet_pattern = BOOKLET_REGION
    booklet_index = booklet_pattern.index("D")
    weak_d_matrix[booklet_row - 1][booklet_start_column - 1 + booklet_index] = 16
    raw_text = build_raw_text([weak_d_matrix])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK04/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 200

    payload = response.json()
    assert payload["processed_booklets"] == ["D"]
    assert payload["decoded_sheets"][0]["analysis_threshold_used"] == 12
    assert payload["decoded_sheets"][0]["answers"] == {
        "1": "E",
        "2": "D",
        "3": "D",
        "4": "E",
        "5": "C",
    }
    assert not any("zayif isaretler geri kazanildi" in warning for warning in payload["decoded_sheets"][0]["warnings"])


def test_device_import_endpoint_scores_mixed_booklets_in_single_pass(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_multi_booklet_exam_payload())
    assert save_response.status_code == 200

    answer_key_raw = build_raw_text([
        build_matrix("ABCDE", booklet_code="A"),
        build_matrix("BCDEA", booklet_code="B"),
    ])
    student_raw = build_raw_text([
        build_matrix("ABCDE", booklet_code="A"),
        build_matrix("BCDEA", booklet_code="B"),
    ])
    payloads = [build_device_payload(answer_key_raw, 2), build_device_payload(student_raw, 2)]

    def fake_read_mark_sheet(*args, **kwargs):
        return payloads.pop(0)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    key_response = client.post("/api/exams/OPTIK02/device-answer-key", json={"settings": {"analysis_threshold": 12, "max_sheets": 0}})
    assert key_response.status_code == 200

    import_response = client.post("/api/exams/OPTIK02/device-import", json={"settings": {"analysis_threshold": 12, "max_sheets": 0}})
    assert import_response.status_code == 200

    session = import_response.json()["session"]
    assert session["summary"]["student_count"] == 2
    assert [item["booklet_code"] for item in session["booklet_summary"]] == ["A", "B"]
    assert session["student_preview"][0]["booklet_code"] == "A"
    assert session["student_preview"][1]["booklet_code"] == "B"
    assert session["student_preview"][0]["score"] == 5.0
    assert session["student_preview"][1]["score"] == 5.0


def test_device_answer_key_endpoint_rejects_sparse_non_contiguous_decode_with_diagnostic(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_response = client.post("/api/exams", json=build_single_booklet_exam_payload())
    assert save_response.status_code == 200

    sparse_matrix = build_matrix_with_positions(65, ANSWER_BLOCKS, [(28, "C"), (88, "D")])
    raw_text = build_raw_text([sparse_matrix])

    def fake_read_mark_sheet(*args, **kwargs):
        return build_device_payload(raw_text, 1)

    monkeypatch.setattr("backend.app.main.read_mark_sheet", fake_read_mark_sheet)

    response = client.post("/api/exams/OPTIK01/device-answer-key", json={"settings": {"analysis_threshold": 12}})
    assert response.status_code == 400
    assert "Cihaz verisi geldi ancak cevap anahtari Q1'den baslamiyor" in response.json()["detail"]


def test_decode_sheet_correctly_decodes_device_flipped_matrix() -> None:
    """SR3500 sends matrix bottom-first; decode_sheet must flip and decode correctly."""
    template = parse_form_template(Path(__file__).resolve().parent.parent.parent, "varsayilan")
    exam = {"booklet_codes": ["A", "B", "C", "D"], "questions": []}

    # Build a correct-orientation matrix with known answers and booklet
    answer_key = "ABCDE"
    booklet_code = "C"
    correct_matrix = build_matrix(answer_key, booklet_code=booklet_code)
    mark_student_number(correct_matrix, "05367246543")

    # Simulate device output: flip the matrix vertically (device sends bottom-first)
    device_matrix = list(reversed(correct_matrix))

    sheet = {"sheet_no": 1, "front_matrix": device_matrix}
    decoded = decode_sheet(sheet, template, exam, threshold=12)

    # Must pick flip_vertical
    assert decoded["matrix_orientation"] == "flip_vertical"
    assert decoded["matrix_orientation_corrected"] is True

    # Answers must be correct
    answers = decoded["answers"]
    for pos, expected in enumerate(answer_key, start=1):
        assert answers.get(str(pos)) == expected, f"Q{pos}: expected {expected}, got {answers.get(str(pos))}"

    # Booklet must be detected
    assert decoded["booklet_code"] == booklet_code

    # Student number must be decoded
    assert decoded["decoded_fields"].get("student_number") == "05367246543"


def test_decode_sheet_prefers_flip_vertical_in_tie() -> None:
    """When both orientations score equally, flip_vertical should win."""
    template = parse_form_template(Path(__file__).resolve().parent.parent.parent, "varsayilan")
    exam = {"booklet_codes": [], "questions": []}

    # Empty matrix - both orientations produce the same (blank) result
    empty_matrix = [[0 for _ in range(48)] for _ in range(65)]
    sheet = {"sheet_no": 1, "front_matrix": empty_matrix}
    decoded = decode_sheet(sheet, template, exam, threshold=12)

    # Flip should be preferred when tied
    assert decoded["matrix_orientation"] == "flip_vertical"