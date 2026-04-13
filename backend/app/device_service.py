from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


CSC_X86_PATH = Path(r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe")
DEFAULT_SDK_BIN = Path(r"C:\SecureExam\vendor-media\English\English\API Library\Bin")
DEVICE_STATUS_FAMILY_MASK = 0xFFFFFF80

HELPER_STATUS_LABELS = {
    "0x00000000": "OK",
    "0x20312105": "Operating unit mesgul",
    "0x20028880": "Form tepsisi bos veya kagit algilanmadi",
    "hopper_empty": "Form tepsisi bos",
}

HELPER_ERROR_MESSAGES = {
    "sdk_bin_missing": "SR-3500 SDK klasoru bulunamadi. Vendor API klasor yolunu kontrol edin.",
    "driver_dll_missing": "SR-3500 surucu DLL'i bulunamadi. Vendor API kurulumunu dogrulayin.",
    "bad_image_format": "SR-3500 helper ile vendor DLL mimarisi uyusmuyor. x86/x64 kurulumunu kontrol edin.",
    "dll_not_found": "SR-3500 vendor DLL yuklenemedi. API Library/Bin altindaki dosyalari kontrol edin.",
    "entry_point_not_found": "SR-3500 vendor DLL beklenen API girislerini sunmuyor. SDK surumu uyumsuz olabilir.",
    "unexpected": "SR-3500 helper beklenmeyen bir hata ile sonlandi.",
}

# R4 ve akraba kodlar icin normalized aile kodu (maskelenmiş hex)
_R4_FAMILY = "0x20029200"   # Timing Mark Error
_Q2_FAMILY = "0x20028900"   # Double Feed Error
_Q3_FAMILY = "0x20028980"   # Left End Skew Error
_Q4_FAMILY = "0x20028A00"   # Mark Skew Error

HELPER_STATUS_MESSAGES = {
    ("req_init_status", "0x20312105"): (
        "SR-3500 hazirlama komutunu kabul etmedi. Cihaz panelinde aktif bir islem/menü olabilir "
        "veya baska bir yazilim cihazi kullaniyor olabilir. Paneli hazir ekrana getirip tekrar deneyin."
    ),
    ("feed_mark_sheet_status", "0x20028880"): (
        "Cihaz formu besleyemedi. Tepside kagit oldugunu, kagidin duz yerlestigini ve besleme yolunun hazir oldugunu kontrol edin."
    ),
    ("feed_mark_sheet_status", _R4_FAMILY): (
        "Cihaz formu beslerken zamanlama isareti okuyamadi (R4 Timing Mark Error). "
        "Form bozuk veya yanlis boyutta olabilir ya da besleme yolunda hizalama sorunu var. "
        "Formu cihazdan cikarin, duzeltip yeniden yerlestirip tekrar deneyin."
    ),
    ("feed_mark_sheet_status", _Q2_FAMILY): (
        "Cihaz cift besleme algiladi (Q2 Double Feed Error). "
        "Birden fazla form yapismis olabilir. Formlari ayirip yeniden yerlestirin."
    ),
    ("feed_mark_sheet_status", _Q3_FAMILY): (
        "Form egik beslendi (Q3 Left End Skew Error). "
        "Formu duzgun hizalayarak tekrar yerlestirin."
    ),
    ("feed_mark_sheet_status", _Q4_FAMILY): (
        "Form isaret egikliginden dolayi okunamadi (Q4 Mark Skew Error). "
        "Formu duzgun hizalayarak tekrar yerlestirin."
    ),
    ("device_status", "0x20028880"): (
        "Cihaz form bekliyor veya tepside okunacak kagit algilamadi. Formu tekrar yerlestirip yeniden deneyin."
    ),
    ("device_status", "hopper_empty"): (
        "Tepside okunacak form kalmadi. Yeni form koyup yeniden deneyin."
    ),
}

HELPER_STATUS_GENERIC_MESSAGES = {
    "open_single_status": "SR-3500 ile ilk baglanti kurulurken cihaz cevap vermedi.",
    "open_with_omrapi_status": "SR-3500 yedek baglanti yontemi de basarisiz oldu.",
    "sensor_status": "SR-3500 sensor durumu okunamadi.",
    "get_mark_conf_status": "SR-3500 mevcut okuma ayarlari okunamadi.",
    "set_mark_conf_status": "SR-3500 okuma ayarlari cihaza uygulanamadi.",
    "feed_mark_sheet_status": "SR-3500 formu beslerken hata verdi.",
    "get_front_marks_status": "SR-3500 isaret matrisini cihazin on yuzunden alamadi.",
    "close_status": "SR-3500 baglantisi temiz kapatilamadi.",
}


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def parse_matrix_rows(lines: list[str]) -> list[list[int]]:
    matrix: list[list[int]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "<empty>":
            continue
        matrix.append([parse_int(cell, 0) for cell in stripped.split(",")])
    return matrix


def summarize_sheet(sheet: dict[str, Any], threshold: int) -> dict[str, Any]:
    matrix = sheet.get("front_matrix", [])
    nonzero_count = 0
    candidate_marks: list[str] = []
    darkest_value = 0
    row_hits = 0

    for row_index, row in enumerate(matrix, start=1):
        hits: list[str] = []
        for column_index, value in enumerate(row, start=1):
            if value > 0:
                nonzero_count += 1
                darkest_value = max(darkest_value, value)
            if value >= threshold:
                hits.append(f"K{column_index}={value}")
        if hits:
            row_hits += 1
            if len(candidate_marks) < 12:
                candidate_marks.append(f"S{row_index}: {' / '.join(hits[:4])}")

    return {
        "sheet_no": sheet.get("sheet_no", 0),
        "rows": sheet.get("front_rows", 0),
        "columns": sheet.get("front_columns", 0),
        "type": sheet.get("front_type", 0),
        "nonzero_cell_count": nonzero_count,
        "candidate_mark_count": sum(1 for row in matrix for value in row if value >= threshold),
        "candidate_row_count": row_hits,
        "darkest_value": darkest_value,
        "preview": candidate_marks,
    }


def build_analysis_text(sheets: list[dict[str, Any]], settings: dict[str, Any], threshold: int) -> str:
    lines = [
        f"Toplam form: {len(sheets)}",
        f"Kolon ayarı: {settings.get('columns', 48)}",
        f"Okuma yöntemi: {settings.get('reading_method', 3)}",
        f"Kağıt kalınlığı: {settings.get('thickness_type', 0)}",
        f"Arka yüz okuma: {'Açık' if settings.get('backside_reading') else 'Kapalı'}",
        f"Analiz eşiği: {threshold}",
        "",
    ]

    for sheet in sheets:
        lines.append(
            f"Form {sheet['sheet_no']}: {sheet['rows']}x{sheet['columns']} | aday işaret={sheet['candidate_mark_count']} | karanlık hücre={sheet['nonzero_cell_count']} | max={sheet['darkest_value']}"
        )
        if sheet["preview"]:
            lines.extend(sheet["preview"])
        else:
            lines.append("Belirgin işaret bulunamadı.")
        lines.append("")

    return "\n".join(lines).strip()


def parse_mark_output_detailed(raw_text: str) -> list[dict[str, Any]]:
    sheets: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    matrix_lines: list[str] = []
    reading_matrix = False

    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("[sheet_") and stripped.endswith("]") and not stripped.startswith("[/"):
            current = {"sheet_no": parse_int(stripped.removeprefix("[sheet_").removesuffix("]"), len(sheets) + 1)}
            matrix_lines = []
            reading_matrix = False
            continue

        if stripped.startswith("[/sheet_"):
            if current is not None:
                current["front_matrix"] = parse_matrix_rows(matrix_lines)
                sheets.append(current)
            current = None
            matrix_lines = []
            reading_matrix = False
            continue

        if current is None:
            continue

        if stripped == "front_marks=":
            reading_matrix = True
            matrix_lines = []
            continue

        if reading_matrix:
            matrix_lines.append(stripped)
            continue

        if "=" in stripped:
            key, value = stripped.split("=", 1)
            current[key] = parse_int(value, 0)

    return sheets


def parse_mark_output(raw_text: str, threshold: int = 12) -> dict[str, Any]:
    sheets = parse_mark_output_detailed(raw_text)

    sheet_summaries = [summarize_sheet(sheet, threshold) for sheet in sheets]
    return {
        "sheet_count": len(sheets),
        "sheets": sheet_summaries,
    }


def parse_helper_status_lines(raw_text: str) -> dict[str, str]:
    status_lines: dict[str, str] = {}
    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        status_lines[key.strip()] = value.strip()
    return status_lines


def normalize_helper_status_value(value: str) -> str:
    text = str(value or "").strip()
    if not text.startswith("0x"):
        return text
    try:
        parsed = int(text, 16)
    except ValueError:
        return text
    return f"0x{(parsed & DEVICE_STATUS_FAMILY_MASK):08X}"


def format_helper_status(key: str, value: str) -> str:
    normalized_value = normalize_helper_status_value(value)
    label = HELPER_STATUS_LABELS.get(value) or HELPER_STATUS_LABELS.get(normalized_value)
    if label:
        return f"{key}={value} ({label})"
    return f"{key}={value}"


def build_helper_failure_message(helper_output: str, returncode: int) -> str:
    if not helper_output.strip():
        return f"SR-3500 yardimci sureci {returncode} cikis koduyla sonlandi."

    status_lines = parse_helper_status_lines(helper_output)
    error_key = status_lines.get("error")
    if error_key:
        error_message = HELPER_ERROR_MESSAGES.get(error_key, "SR-3500 helper teknik bir hata ile sonlandi.")
        detail = status_lines.get("message")
        if detail:
            return f"{error_message} Detay: {detail}"
        return f"{error_message} Teknik kod: error={error_key}."

    prioritized_keys = [
        "req_init_status",
        "feed_mark_sheet_status",
        "device_status",
        "get_front_marks_status",
        "set_mark_conf_status",
        "get_mark_conf_status",
        "sensor_status",
        "open_single_status",
        "open_with_omrapi_status",
        "close_status",
    ]

    for key in prioritized_keys:
        value = status_lines.get(key)
        if not value or value == "0x00000000":
            continue
        normalized_value = normalize_helper_status_value(value)
        friendly_message = HELPER_STATUS_MESSAGES.get((key, value)) or HELPER_STATUS_MESSAGES.get((key, normalized_value))
        if friendly_message:
            return f"{friendly_message} Teknik kod: {format_helper_status(key, value)}."
        generic_message = HELPER_STATUS_GENERIC_MESSAGES.get(key)
        if generic_message:
            return f"{generic_message} Teknik kod: {format_helper_status(key, value)}."
        return f"SR-3500 islemi cihaz tarafinda reddedildi. Teknik kod: {format_helper_status(key, value)}."

    compact_lines = [line.strip() for line in helper_output.splitlines() if line.strip()]
    if compact_lines:
        return f"SR-3500 yardimci sureci basarisiz oldu. Detay: {compact_lines[-1]}"
    return f"SR-3500 yardimci sureci {returncode} cikis koduyla sonlandi."


def build_vendor_probe(project_root: Path, work_dir: Path) -> Path:
    source_path = project_root / "ops" / "sr3500_vendor_probe_x86.cs"
    if not source_path.exists():
        raise RuntimeError(f"SR-3500 probe source not found: {source_path}")
    if not CSC_X86_PATH.exists():
        raise RuntimeError(f"x86 C# compiler not found: {CSC_X86_PATH}")

    work_dir.mkdir(parents=True, exist_ok=True)
    exe_path = work_dir / "sr3500_vendor_probe_x86.exe"
    if exe_path.exists() and exe_path.stat().st_mtime >= source_path.stat().st_mtime:
        return exe_path

    result = subprocess.run(
        [
            str(CSC_X86_PATH),
            "/nologo",
            "/target:exe",
            "/platform:x86",
            f"/out:{exe_path}",
            str(source_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(project_root),
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stdout + "\n" + result.stderr).strip() or "SR-3500 probe compilation failed.")
    return exe_path


def read_mark_sheet(
    project_root: Path,
    state_dir: Path,
    sdk_bin: Path | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sdk_root = sdk_bin or DEFAULT_SDK_BIN
    if not sdk_root.exists():
        raise RuntimeError(f"SR-3500 SDK klasoru bulunamadi: {sdk_root}")

    read_settings = {
        "max_sheets": 0,
        "columns": 48,
        "reading_method": 3,
        "thickness_type": 0,
        "backside_reading": False,
        "analysis_threshold": 12,
    }
    if settings:
        read_settings.update(settings)

    work_dir = state_dir / "device-runtime"
    output_path = work_dir / "last-mark-read.txt"
    exe_path = build_vendor_probe(project_root, work_dir)

    result = subprocess.run(
        [
            str(exe_path),
            str(sdk_root),
            "mark-batch",
            str(output_path),
            str(read_settings["max_sheets"]),
            str(read_settings["columns"]),
            str(read_settings["reading_method"]),
            str(read_settings["thickness_type"]),
            "1" if read_settings["backside_reading"] else "0",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(work_dir),
        timeout=180,
        check=False,
    )

    helper_output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise RuntimeError(build_helper_failure_message(helper_output, result.returncode))
    if not output_path.exists():
        raise RuntimeError("SR-3500 helper completed but mark output file was not produced.")

    raw_text = output_path.read_text(encoding="utf-8", errors="replace")
    metadata = parse_mark_output(raw_text, threshold=int(read_settings["analysis_threshold"]))
    metadata["output_file"] = str(output_path)
    metadata["settings"] = read_settings

    # Partial-read recovery: C# probe breaks gracefully on mid-batch feed errors
    # (e.g. R4 Timing Mark Error) and emits feed_partial_end= to stdout.
    # Surface this as a device warning so the UI can inform the operator.
    helper_status_lines = parse_helper_status_lines(helper_output)
    partial_end_raw = helper_status_lines.get("feed_partial_end")
    partial_warnings: list[str] = []
    if partial_end_raw:
        normalized_partial = normalize_helper_status_value(partial_end_raw)
        friendly = (
            HELPER_STATUS_MESSAGES.get(("feed_mark_sheet_status", partial_end_raw))
            or HELPER_STATUS_MESSAGES.get(("feed_mark_sheet_status", normalized_partial))
        )
        partial_warnings.append(
            f"{friendly or 'Cihaz besleme durdu.'} "
            f"Bu turda {metadata['sheet_count']} form okundu; "
            f"kalan formlar bir sonraki okumada beslenebilir. Teknik: feed_partial_end={partial_end_raw}."
        )
        metadata["feed_partial_end_status"] = partial_end_raw

    return {
        "raw_text": raw_text,
        "analysis_text": build_analysis_text(metadata["sheets"], read_settings, int(read_settings["analysis_threshold"])),
        "metadata": metadata,
        "helper_output": helper_output,
        "partial_warnings": partial_warnings,
    }


def build_device_payload_from_raw_text(raw_text: str, settings: dict[str, Any] | None = None) -> dict[str, Any]:
    read_settings = {
        "max_sheets": 0,
        "columns": 48,
        "reading_method": 3,
        "thickness_type": 0,
        "backside_reading": False,
        "analysis_threshold": 12,
    }
    if settings:
        read_settings.update(settings)

    metadata = parse_mark_output(raw_text, threshold=int(read_settings["analysis_threshold"]))
    metadata["output_file"] = "raw-device-text"
    metadata["settings"] = read_settings
    return {
        "raw_text": raw_text,
        "analysis_text": build_analysis_text(metadata["sheets"], read_settings, int(read_settings["analysis_threshold"])),
        "metadata": metadata,
        "helper_output": "raw-device-text",
    }