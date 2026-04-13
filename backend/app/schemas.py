from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BookletMappingInput(BaseModel):
    position: int = Field(ge=1)
    correct_answer: str = Field(min_length=1)


class QuestionInput(BaseModel):
    canonical_no: int = Field(ge=1)
    group_label: str = "Genel"
    weight: float = Field(gt=0)
    booklet_mappings: dict[str, BookletMappingInput]


class ExamUpsertRequest(BaseModel):
    exam_code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""
    exam_year: str = ""
    exam_term: str = ""
    exam_type: str = ""
    form_template_id: str = Field(default="varsayilan", min_length=1)
    booklet_codes: list[str] = Field(min_length=1)
    questions: list[QuestionInput] = Field(default_factory=list)


class ParsedImportRow(BaseModel):
    student_id: str
    booklet_code: str
    answers: dict[str, str]
    source_row: int


class DeviceReadSettings(BaseModel):
    max_sheets: int = Field(default=0, ge=0, le=500)
    columns: int = Field(default=48, ge=1, le=48)
    reading_method: int = Field(default=3, ge=1, le=6)
    thickness_type: int = Field(default=0, ge=0, le=5)
    backside_reading: bool = False
    analysis_threshold: int = Field(default=12, ge=1, le=16)


class DeviceReadRequest(BaseModel):
    settings: DeviceReadSettings = Field(default_factory=DeviceReadSettings)


class DeviceAnswerKeyReadRequest(BaseModel):
    settings: DeviceReadSettings = Field(default_factory=DeviceReadSettings)
    booklet_code: str | None = None
    booklet_codes: list[str] | None = None
    form_template_id: str | None = None


class DeviceImportRequest(BaseModel):
    settings: DeviceReadSettings = Field(default_factory=DeviceReadSettings)
    form_template_id: str | None = None
    raw_text: str | None = None
    net_rule_code: str | None = None


class ApiMessage(BaseModel):
    message: str
    payload: dict[str, Any] | None = None
