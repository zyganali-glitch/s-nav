from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from backend.app.main import create_app


def build_exam_payload() -> dict[str, object]:
    return {
        "exam_code": "deneme01",
        "title": "Nisan Denemesi",
        "description": "Iki kitapcikli agirlikli deneme",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A", "B"],
        "questions": [
            {
                "canonical_no": 1,
                "group_label": "Matematik",
                "weight": 10,
                "booklet_mappings": {
                    "A": {"position": 1, "correct_answer": "A"},
                    "B": {"position": 2, "correct_answer": "A"},
                },
            },
            {
                "canonical_no": 2,
                "group_label": "Fen",
                "weight": 5,
                "booklet_mappings": {
                    "A": {"position": 2, "correct_answer": "D"},
                    "B": {"position": 1, "correct_answer": "D"},
                },
            },
        ],
    }


def build_single_booklet_exam_payload() -> dict[str, object]:
    answer_key = "AABBDAADEC"
    return {
        "exam_code": "tekkitapcik",
        "title": "Tek Kitapcik Deneme",
        "description": "Sabit genislik TXT import testi",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A"],
        "questions": [
            {
                "canonical_no": index,
                "group_label": "Genel",
                "weight": 1,
                "booklet_mappings": {
                    "A": {"position": index, "correct_answer": answer},
                },
            }
            for index, answer in enumerate(answer_key, start=1)
        ],
    }


def build_draft_exam_payload() -> dict[str, object]:
    return {
        "exam_code": "taslak01",
        "title": "Taslak Sinav",
        "description": "Cevap anahtari sonradan yüklenecek",
        "form_template_id": "varsayilan",
        "booklet_codes": ["A", "B"],
        "questions": [],
    }


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "app_state.json")
    return TestClient(app)


def test_exam_save_and_csv_import_scoring(client: TestClient) -> None:
    save_response = client.post("/api/exams", json=build_exam_payload())
    assert save_response.status_code == 200
    assert save_response.json()["summary"]["question_count"] == 2
    assert save_response.json()["summary"]["form_template_id"] == "varsayilan"

    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n1002,B,D,A\n1003,B,D,C\n"
    import_response = client.post(
        "/api/exams/DENEME01/imports",
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )
    assert import_response.status_code == 200
    session = import_response.json()["session"]

    assert session["summary"]["student_count"] == 3
    assert session["summary"]["average_score"] == 11.67
    assert [item["booklet_code"] for item in session["booklet_summary"]] == ["A", "B"]
    assert session["booklet_summary"][1]["total_correct_count"] == 3
    assert session["booklet_summary"][1]["total_wrong_count"] == 1
    assert session["group_summary"][0]["total_correct_count"] >= 1
    assert session["question_summary"][0]["correct_rate"] == 66.67
    assert session["question_summary"][0]["booklet_positions"] == {"A": 1, "B": 2}
    assert session["question_summary"][0]["booklet_answer_key"] == {"A": "A", "B": "A"}
    assert session["question_summary"][0]["choice_distribution"]["A"]["count"] == 2
    assert session["question_summary"][0]["blank_distribution"]["count"] == 0
    assert "analysis_glossary" in session
    assert "academic_commentary" in session
    assert any("agirlik" in item["text"].lower() for item in session["academic_commentary"])
    assert session["student_results"][0]["exam_rank"] == 1
    assert session["student_results"][0]["question_responses"][0]["display_value"] == "A(D)"


def test_exam_save_accepts_single_character_code_and_title(client: TestClient) -> None:
    payload = build_draft_exam_payload()
    payload["exam_code"] = "s"
    payload["title"] = "A"

    response = client.post("/api/exams", json=payload)

    assert response.status_code == 200
    detail = response.json()
    assert detail["exam_code"] == "S"
    assert detail["title"] == "A"


def test_vendor_style_semicolon_import_is_accepted(client: TestClient) -> None:
    client.post("/api/exams", json=build_exam_payload())
    txt_payload = "ogrenci_no;kitapcik;S1;S2\n2001;A;A;D\n2002;B;D;A\n"
    response = client.post(
        "/api/exams/DENEME01/imports",
        files={"file": ("vendor_export.txt", txt_payload.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    session = response.json()["session"]
    assert session["summary"]["student_count"] >= 2
    assert session["summary"]["max_score"] == 15.0


def test_fixed_width_vendor_txt_is_accepted_for_single_booklet_exam(client: TestClient) -> None:
    client.post("/api/exams", json=build_single_booklet_exam_payload())
    txt_payload = (
        "     50001210601081                  ALI VELI          AABBDAADEC\n"
        "3    50002240601049                  AYSE FATMA        AABBDAA EC\n"
    )
    response = client.post(
        "/api/exams/TEKKITAPCIK/imports",
        files={"file": ("vendor_export.txt", txt_payload.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    session = response.json()["session"]
    assert session["import_format"] == "vendor-fixed"
    assert session["summary"]["student_count"] == 2
    assert session["summary"]["average_score"] == 9.5
    assert session["student_preview"][1]["blank_count"] == 1


def test_import_can_disable_net_count_with_explicit_none_rule(client: TestClient) -> None:
    client.post("/api/exams", json=build_exam_payload())
    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n1002,B,D,A\n"

    response = client.post(
        "/api/exams/DENEME01/imports",
        data={"net_rule_code": "none"},
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )

    assert response.status_code == 200
    session = response.json()["session"]
    assert session["net_policy"]["code"] == "none"
    assert session["summary"]["average_net_count"] is None
    assert session["student_results"][0]["net_count"] is None


def test_summary_xlsx_is_rejected_with_clear_message(client: TestClient) -> None:
    client.post("/api/exams", json=build_single_booklet_exam_payload())

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["SIRA", "OGRENCI.NO", "SINIF", "ADI SOYADI", "DOGRU", "YANLIS", "NETI", "PUANI"])
    sheet.append([1, "241401005", "12A", "ALI VELI", 22, 3, 22.0, 88])

    buffer = io.BytesIO()
    workbook.save(buffer)
    response = client.post(
        "/api/exams/TEKKITAPCIK/imports",
        files={
            "file": (
                "summary.xlsx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 400
    assert "ozet rapor" in response.json()["detail"].lower()


def test_form_templates_are_listed_and_exam_can_select_one(client: TestClient) -> None:
    template_response = client.get("/api/form-templates")
    assert template_response.status_code == 200

    templates = template_response.json()["items"]
    assert templates[0]["id"] == "varsayilan"
    assert any(item["id"] == "katipcelebi" for item in templates)

    payload = build_exam_payload()
    payload["form_template_id"] = "katipcelebi"
    save_response = client.post("/api/exams", json=payload)
    assert save_response.status_code == 200

    detail = save_response.json()
    assert detail["form_template_id"] == "katipcelebi"
    assert detail["active_form_template"]["name"] == "KATİPÇELEBİ"


def test_exam_can_be_saved_without_questions_and_answer_key_uploaded_from_mapping_csv(client: TestClient) -> None:
    save_response = client.post("/api/exams", json=build_draft_exam_payload())
    assert save_response.status_code == 200
    assert save_response.json()["summary"]["question_count"] == 0
    assert save_response.json()["summary"]["has_answer_key"] is False

    answer_key_csv = (
        "canonical_no,group_label,weight,A_position,A_answer,B_position,B_answer\n"
        "1,Matematik,10,1,A,2,A\n"
        "2,Fen,5,2,D,1,D\n"
    )
    upload_response = client.post(
        "/api/exams/TASLAK01/answer-key",
        files={"file": ("answer_key.csv", answer_key_csv, "text/csv")},
    )

    assert upload_response.status_code == 200
    detail = upload_response.json()
    assert detail["summary"]["question_count"] == 2
    assert detail["summary"]["has_answer_key"] is True
    assert detail["answer_key_profile"]["import_format"] == "answer-key-mapping"
    assert detail["questions"][0]["booklet_mappings"]["B"]["position"] == 2


def test_single_booklet_fixed_width_answer_key_upload_is_accepted(client: TestClient) -> None:
    payload = build_single_booklet_exam_payload()
    payload["questions"] = []
    save_response = client.post("/api/exams", json=payload)
    assert save_response.status_code == 200

    txt_payload = "     50001210601081                  CEVAP ANAHTARI    AABBDAADEC\n"
    upload_response = client.post(
        "/api/exams/TEKKITAPCIK/answer-key",
        files={"file": ("answer_key.txt", txt_payload.encode("utf-8"), "text/plain")},
    )

    assert upload_response.status_code == 200
    detail = upload_response.json()
    assert detail["summary"]["question_count"] == 10
    assert detail["answer_key_profile"]["import_format"] == "answer-key-vendor-fixed"
    assert detail["questions"][9]["booklet_mappings"]["A"]["correct_answer"] == "C"


def test_student_import_is_blocked_until_answer_key_exists(client: TestClient) -> None:
    save_response = client.post("/api/exams", json=build_draft_exam_payload())
    assert save_response.status_code == 200

    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n"
    import_response = client.post(
        "/api/exams/TASLAK01/imports",
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )

    assert import_response.status_code == 400
    assert "cevap anahtari" in import_response.json()["detail"].lower()


def test_exam_can_be_deleted_from_library(client: TestClient) -> None:
    save_response = client.post("/api/exams", json=build_exam_payload())
    assert save_response.status_code == 200

    delete_response = client.delete("/api/exams/DENEME01")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    get_response = client.get("/api/exams/DENEME01")
    assert get_response.status_code == 404


@pytest.mark.parametrize(
    ("export_format", "expected_media_type", "expected_prefix"),
    [
        ("csv", "text/csv; charset=utf-8", "\ufeffRapor Bolumu,Genel Ozet"),
        ("txt", "text/plain; charset=utf-8", "Genel Ozet"),
        ("json", "application/json; charset=utf-8", '{\n  "exam"'),
    ],
)
def test_session_exports_return_downloadable_payloads(
    client: TestClient,
    export_format: str,
    expected_media_type: str,
    expected_prefix: str,
) -> None:
    client.post("/api/exams", json=build_exam_payload())
    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n1002,B,D,A\n"
    import_response = client.post(
        "/api/exams/DENEME01/imports",
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )
    assert import_response.status_code == 200

    response = client.get(f"/api/exams/DENEME01/exports/{export_format}?session_id=latest")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(expected_media_type)
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert response.text.startswith(expected_prefix)
    if export_format in {"csv", "txt"}:
        assert "Kitapcik Ozeti" in response.text
        assert "Ogrenci Cevap Matrisi" in response.text
        assert "Rapor Metodolojisi ve Terim Aciklamalari" in response.text
        assert "Sinava Ozel Akademik Yorum" in response.text
        assert "Sorulara Siklara Gore Verilen Cevaplarin Dagilimi" in response.text
        assert "Bu yorum oturum verisinden deterministic olarak uretilir." not in response.text


def test_legacy_session_is_hydrated_for_detail_and_export(tmp_path: Path) -> None:
    app = create_app(tmp_path / "app_state.json")
    client = TestClient(app)

    client.post("/api/exams", json=build_exam_payload())
    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n1002,B,D,A\n"
    import_response = client.post(
        "/api/exams/DENEME01/imports",
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )
    assert import_response.status_code == 200

    state_path = tmp_path / "app_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    session = state["exams"]["DENEME01"]["sessions"][0]
    session.pop("analysis_glossary", None)
    session.pop("academic_commentary", None)
    for row in session.get("booklet_summary", []):
        row.pop("total_score", None)
        row.pop("total_correct_count", None)
        row.pop("total_wrong_count", None)
        row.pop("total_blank_count", None)
        row.pop("total_net_count", None)
    for row in session.get("group_summary", []):
        row.pop("student_count", None)
        row.pop("total_score", None)
        row.pop("total_correct_count", None)
        row.pop("total_wrong_count", None)
        row.pop("total_blank_count", None)
        row.pop("total_net_count", None)
    for row in session.get("question_summary", []):
        row.pop("difficulty_index", None)
        row.pop("item_variance", None)
        row.pop("item_std_dev", None)
        row.pop("point_biserial", None)
        row.pop("point_biserial_label", None)
        row.pop("upper_group_correct_rate", None)
        row.pop("lower_group_correct_rate", None)

    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    detail_response = client.get("/api/exams/DENEME01")
    assert detail_response.status_code == 200
    hydrated_session = detail_response.json()["recent_sessions"][0]
    assert hydrated_session["analysis_glossary"]
    assert hydrated_session["academic_commentary"]
    assert hydrated_session["booklet_summary"][0]["total_score"] == 15.0
    assert hydrated_session["group_summary"][0]["student_count"] == 2
    assert "point_biserial" in hydrated_session["question_summary"][0]

    export_response = client.get("/api/exams/DENEME01/exports/csv?session_id=latest")
    assert export_response.status_code == 200
    assert "Sinava Ozel Akademik Yorum" in export_response.text
    assert ",15,2,0,0,2," in export_response.text or ",15.0,2,0,0,2.0," in export_response.text


@pytest.mark.parametrize(
    ("export_format", "content_type_prefix", "signature"),
    [
        (
            "xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            b"PK",
        ),
        ("pdf", "application/pdf", b"%PDF"),
    ],
)
def test_binary_session_exports_return_expected_file_signatures(
    client: TestClient,
    export_format: str,
    content_type_prefix: str,
    signature: bytes,
) -> None:
    client.post("/api/exams", json=build_exam_payload())
    csv_payload = "student_id,booklet_code,Q1,Q2\n1001,A,A,D\n"
    import_response = client.post(
        "/api/exams/DENEME01/imports",
        files={"file": ("answers.csv", csv_payload, "text/csv")},
    )
    assert import_response.status_code == 200

    response = client.get(f"/api/exams/DENEME01/exports/{export_format}?session_id=latest")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type_prefix)
    assert response.content.startswith(signature)
