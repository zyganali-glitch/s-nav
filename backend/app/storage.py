from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonStateStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _default_state(self) -> dict[str, Any]:
        return {"exams": {}}

    def read_state(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return self._default_state()
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def write_state(self, state: dict[str, Any]) -> None:
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=self.file_path.parent) as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            temp_path = Path(handle.name)
        temp_path.replace(self.file_path)

    def list_exams(self) -> list[dict[str, Any]]:
        state = self.read_state()
        exams = list(state.get("exams", {}).values())
        exams.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        return [deepcopy(item) for item in exams]

    def get_exam(self, exam_code: str) -> dict[str, Any] | None:
        state = self.read_state()
        exam = state.get("exams", {}).get(exam_code)
        return deepcopy(exam) if exam else None

    def upsert_exam(self, exam: dict[str, Any]) -> dict[str, Any]:
        state = self.read_state()
        exams = state.setdefault("exams", {})
        existing = exams.get(exam["exam_code"], {})
        merged = deepcopy(exam)
        merged["created_at"] = existing.get("created_at", utc_now_iso())
        merged["updated_at"] = utc_now_iso()
        merged["sessions"] = existing.get("sessions", [])
        exams[exam["exam_code"]] = merged
        self.write_state(state)
        return deepcopy(merged)

    def append_session(self, exam_code: str, session: dict[str, Any]) -> dict[str, Any]:
        state = self.read_state()
        exams = state.setdefault("exams", {})
        exam = exams.get(exam_code)
        if not exam:
            raise KeyError(exam_code)
        sessions = list(exam.get("sessions", []))
        sessions.insert(0, deepcopy(session))
        exam["sessions"] = sessions[:10]
        exam["updated_at"] = utc_now_iso()
        self.write_state(state)
        return deepcopy(exam)

    def delete_exam(self, exam_code: str) -> bool:
        state = self.read_state()
        exams = state.setdefault("exams", {})
        if exam_code not in exams:
            return False
        del exams[exam_code]
        self.write_state(state)
        return True
