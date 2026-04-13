from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .device_service import build_device_payload_from_raw_text, parse_mark_output_detailed, read_mark_sheet
from .exam_service import build_answer_key_profile, build_exam_detail, compute_import_session, normalize_exam_payload, normalize_token, summarize_exam
from .export_service import build_session_export, resolve_session
from .form_template_service import list_form_templates, resolve_form_template, slugify_form_template_name
from .import_service import parse_answer_key_upload, parse_upload_file
from .optical_form_service import apply_optical_answer_keys, decode_exam_sheets, decode_sheet, parse_form_template
from .schemas import DeviceAnswerKeyReadRequest, DeviceImportRequest, DeviceReadRequest, ExamUpsertRequest
from .storage import JsonStateStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEFAULT_DATA_FILE = PROJECT_ROOT / "backend" / "data" / "app_state.json"


def form_template_catalog() -> list[dict[str, Any]]:
    return list_form_templates(PROJECT_ROOT)


def get_exam_or_404(store: JsonStateStore, exam_code: str) -> dict[str, Any]:
    exam = store.get_exam(exam_code.upper())
    if not exam:
        raise HTTPException(status_code=404, detail="Sinav bulunamadi.")
    return exam


def ensure_answer_key_ready(exam: dict[str, Any]) -> None:
    if not exam.get("questions"):
        raise HTTPException(status_code=400, detail="Cevap anahtari yuklenmeden ogrenci cevaplari puanlanamaz.")


def apply_form_template_override(exam: dict[str, Any], template_id: str | None) -> dict[str, Any]:
    if not template_id:
        return deepcopy(exam)

    catalog = form_template_catalog()
    normalized_template_id = slugify_form_template_name(template_id)
    selected_template = resolve_form_template(template_id, catalog)
    if selected_template["id"] != normalized_template_id:
        raise HTTPException(status_code=400, detail="Secilen optik kagit formati bulunamadi.")

    updated_exam = deepcopy(exam)
    updated_exam["form_template_id"] = selected_template["id"]
    updated_exam["form_template_name"] = selected_template["name"]
    return updated_exam


def normalize_vendor_fixed_rows(exam: dict[str, Any], parsed_rows: list[dict[str, Any]], import_format: str) -> list[dict[str, Any]]:
    if import_format != "vendor-fixed":
        return parsed_rows

    booklet_codes = exam.get("booklet_codes", [])
    if len(booklet_codes) != 1:
        raise HTTPException(
            status_code=400,
            detail="Header'siz sabit-genislik vendor TXT cok kitapcikli sinavlarda bilincli olarak reddedilir.",
        )

    normalized_booklet = str(booklet_codes[0]).strip().upper()
    rows: list[dict[str, Any]] = []
    for row in parsed_rows:
        copied = dict(row)
        copied["booklet_code"] = normalized_booklet
        rows.append(copied)
    return rows


def resolve_device_answer_key_settings(
    exam: dict[str, Any],
    payload: DeviceAnswerKeyReadRequest,
) -> dict[str, Any]:
    settings = payload.settings.model_dump()
    if int(settings.get("max_sheets") or 0) > 0:
        return settings

    requested_booklets: list[str] = []
    requested_items = payload.booklet_codes or ([payload.booklet_code] if payload.booklet_code else [])
    for item in requested_items:
        token = normalize_token(item)
        if token and token not in requested_booklets:
            requested_booklets.append(token)
    if requested_booklets:
        settings["max_sheets"] = len(requested_booklets)
        return settings

    exam_booklets: list[str] = []
    for item in exam.get("booklet_codes", []):
        token = normalize_token(item)
        if token and token not in exam_booklets:
            exam_booklets.append(token)
    if not exam_booklets:
        return settings

    known_booklets = {
        normalize_token(item)
        for item in (exam.get("optical_answer_key_booklets") or {}).keys()
        if normalize_token(item)
    }
    pending_booklets = [item for item in exam_booklets if item not in known_booklets]
    settings["max_sheets"] = len(pending_booklets) if pending_booklets else len(exam_booklets)
    return settings


def decode_device_sheets(
    exam: dict[str, Any],
    raw_text: str,
    threshold: int,
    *,
    fallback_booklet: str | None = None,
    filter_booklets: list[str] | None = None,
) -> list[dict[str, Any]]:
    sheets = parse_mark_output_detailed(raw_text)
    template = parse_form_template(PROJECT_ROOT, exam.get("form_template_id"))
    normalized_filters = {item.strip().upper() for item in (filter_booklets or []) if str(item).strip()}

    decoded_sheets: list[dict[str, Any]] = []
    for sheet in sheets:
        decoded = decode_sheet(sheet, template, exam, threshold, fallback_booklet=fallback_booklet)
        if normalized_filters and decoded.get("booklet_code") and decoded["booklet_code"] not in normalized_filters:
            raise HTTPException(status_code=400, detail="Optik cevap anahtari secili filtre disinda kalan kitapcik verdi.")
        decoded_sheets.append(decoded)
    return decoded_sheets


def create_app(state_file: Path | None = None) -> FastAPI:
    store = JsonStateStore(state_file or DEFAULT_DATA_FILE)

    app = FastAPI(
        title="Sinav Okuma Platformu",
        version="0.1.0",
        summary="Teacher-prep ve operator-run odakli lokal sinav okuma MVP",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/form-templates")
    def get_form_templates() -> dict[str, object]:
        return {"items": form_template_catalog()}

    @app.get("/api/exams")
    def list_exams() -> dict[str, object]:
        return {"items": [summarize_exam(item) for item in store.list_exams()]}

    @app.get("/api/exams/{exam_code}")
    def get_exam(exam_code: str) -> dict[str, object]:
        return build_exam_detail(get_exam_or_404(store, exam_code))

    @app.delete("/api/exams/{exam_code}")
    def delete_exam(exam_code: str) -> dict[str, object]:
        deleted = store.delete_exam(exam_code.upper())
        if not deleted:
            raise HTTPException(status_code=404, detail="Sinav bulunamadi.")
        return {"deleted": True, "exam_code": exam_code.upper()}

    @app.post("/api/exams")
    def save_exam(payload: ExamUpsertRequest) -> dict[str, object]:
        existing = store.get_exam(payload.exam_code.upper())
        try:
            exam = normalize_exam_payload(
                payload.model_dump(),
                existing_exam=existing,
                form_template_catalog=form_template_catalog(),
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if existing and "optical_answer_key_booklets" in existing:
            exam["optical_answer_key_booklets"] = deepcopy(existing.get("optical_answer_key_booklets") or {})

        saved = store.upsert_exam(exam)
        return build_exam_detail(saved)

    @app.post("/api/exams/{exam_code}/answer-key")
    async def upload_answer_key(exam_code: str, file: UploadFile = File(...)) -> dict[str, object]:
        exam = get_exam_or_404(store, exam_code)
        try:
            questions, import_format, booklet_strategy = await parse_answer_key_upload(file, exam.get("booklet_codes", []))
            answer_key_profile = build_answer_key_profile(
                source_type="file-upload",
                source_label="Cevap anahtari dosyasi",
                question_count=len(questions),
                import_format=import_format,
                booklet_strategy=booklet_strategy,
                source_file=file.filename or "answer-key",
            )
            updated_exam = normalize_exam_payload(
                {
                    "exam_code": exam["exam_code"],
                    "title": exam["title"],
                    "description": exam.get("description", ""),
                    "exam_year": exam.get("exam_year", ""),
                    "exam_term": exam.get("exam_term", ""),
                    "exam_type": exam.get("exam_type", ""),
                    "form_template_id": exam.get("form_template_id", "varsayilan"),
                    "booklet_codes": exam.get("booklet_codes", []),
                    "questions": questions,
                },
                existing_exam=exam,
                form_template_catalog=form_template_catalog(),
                answer_key_profile=answer_key_profile,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        updated_exam["optical_answer_key_booklets"] = {}
        saved = store.upsert_exam(updated_exam)
        return build_exam_detail(saved)

    @app.post("/api/exams/{exam_code}/imports")
    async def import_exam_responses(
        exam_code: str,
        file: UploadFile = File(...),
        net_rule_code: str | None = Form(default=None),
    ) -> dict[str, object]:
        exam = get_exam_or_404(store, exam_code)
        ensure_answer_key_ready(exam)

        try:
            parsed_rows, import_format = await parse_upload_file(file)
            parsed_rows = normalize_vendor_fixed_rows(exam, parsed_rows, import_format)
            session = compute_import_session(
                exam,
                parsed_rows,
                file.filename or "import",
                import_format,
                net_rule_code=net_rule_code,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        updated_exam = store.append_session(exam["exam_code"], session)
        return {
            "exam": summarize_exam(updated_exam),
            "session": session,
            "recent_sessions": updated_exam.get("sessions", []),
        }

    @app.post("/api/device/mark-read")
    def device_mark_read(payload: DeviceReadRequest) -> dict[str, object]:
        try:
            return read_mark_sheet(PROJECT_ROOT, DEFAULT_DATA_FILE.parent, settings=payload.settings.model_dump())
        except RuntimeError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/api/exams/{exam_code}/device-answer-key")
    def device_answer_key(exam_code: str, payload: DeviceAnswerKeyReadRequest) -> dict[str, object]:
        exam = apply_form_template_override(get_exam_or_404(store, exam_code), payload.form_template_id)
        booklet_filters = payload.booklet_codes or ([payload.booklet_code] if payload.booklet_code else [])
        fallback_booklet = booklet_filters[0] if len(booklet_filters) == 1 else None
        device_settings = resolve_device_answer_key_settings(exam, payload)

        try:
            device_payload = read_mark_sheet(PROJECT_ROOT, DEFAULT_DATA_FILE.parent, settings=device_settings)
            decoded_sheets = decode_device_sheets(
                exam,
                device_payload["raw_text"],
                int(device_settings["analysis_threshold"]),
                fallback_booklet=fallback_booklet,
                filter_booklets=booklet_filters,
            )
            updated_exam, processed_booklets, answer_key_messages = apply_optical_answer_keys(
                exam,
                decoded_sheets,
                device_payload.get("metadata", {}).get("output_file") or "sr3500-live.txt",
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        saved = store.upsert_exam(updated_exam)
        return {
            "exam": build_exam_detail(saved),
            "decoded_sheets": decoded_sheets,
            "decoded_sheet": decoded_sheets[0] if len(decoded_sheets) == 1 else None,
            "processed_booklets": processed_booklets,
            "answer_key_messages": answer_key_messages + list(device_payload.get("partial_warnings") or []),
            "device": device_payload,
        }

    @app.post("/api/exams/{exam_code}/device-import")
    def device_import(exam_code: str, payload: DeviceImportRequest) -> dict[str, object]:
        exam = get_exam_or_404(store, exam_code)
        ensure_answer_key_ready(exam)
        decode_exam = apply_form_template_override(exam, payload.form_template_id)

        try:
            device_payload = (
                build_device_payload_from_raw_text(payload.raw_text, payload.settings.model_dump())
                if payload.raw_text
                else read_mark_sheet(PROJECT_ROOT, DEFAULT_DATA_FILE.parent, settings=payload.settings.model_dump())
            )
            decoded_rows, decode_warnings = decode_exam_sheets(
                PROJECT_ROOT,
                decode_exam,
                parse_mark_output_detailed(device_payload["raw_text"]),
                int(payload.settings.analysis_threshold),
            )
            session = compute_import_session(
                exam,
                decoded_rows,
                "sr3500-live.txt",
                "device-matrix",
                net_rule_code=payload.net_rule_code,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        session["warnings"] = list(session.get("warnings") or []) + decode_warnings + list(device_payload.get("partial_warnings") or [])
        updated_exam = store.append_session(exam["exam_code"], session)
        return {
            "exam": summarize_exam(updated_exam),
            "session": session,
            "recent_sessions": updated_exam.get("sessions", []),
            "device": device_payload,
        }

    @app.get("/api/exams/{exam_code}/exports/{export_format}")
    def export_session(exam_code: str, export_format: str, session_id: str = "latest") -> Response:
        exam = get_exam_or_404(store, exam_code)
        try:
            session = resolve_session(exam, session_id)
            payload, media_type, filename = build_session_export(exam, session, export_format)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return Response(content=payload, media_type=media_type, headers=headers)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    return app


app = create_app()
