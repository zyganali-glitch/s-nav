"""Full end-to-end decode_sheet verification using raw device matrix."""
import json, re, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from backend.app.optical_form_service import (
    parse_form_template,
    decode_sheet,
    score_decoded_sheet_candidate,
    build_decoded_sheet_payload,
    build_orientation_candidates,
)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DEVICE_FILE = PROJECT_ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"


def parse_sheets_from_file(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    sheets = []
    for match in re.finditer(
        r"\[sheet_(\d+)\].*?front_rows=(\d+).*?front_columns=(\d+).*?front_marks=\s*(.*?)\s*\[/sheet_\1\]",
        text, re.DOTALL,
    ):
        raw_lines = [l.strip() for l in match.group(4).strip().splitlines() if l.strip()]
        matrix = [[int(c) for c in line.split(",")] for line in raw_lines]
        sheets.append({"sheet_no": int(match.group(1)), "front_matrix": matrix})
    return sheets


def main():
    sheets = parse_sheets_from_file(DEVICE_FILE)
    template = parse_form_template(PROJECT_ROOT, "varsayilan")
    
    # Use the AYDEMIR exam config from app_state.json
    app_state = json.loads((PROJECT_ROOT / "backend" / "data" / "app_state.json").read_text("utf-8"))
    exam = app_state["exams"]["AYDEMIR"]
    
    print(f"Exam: AYDEMIR, questions={len(exam.get('questions', []))}, booklets={exam.get('booklet_codes', [])}")
    print(f"Template: {template['template']['id']}")
    
    threshold = 12
    
    for sheet in sheets:
        matrix = sheet["front_matrix"]
        
        # Run decode_sheet (the actual full pipeline)
        decoded = decode_sheet(sheet, template, exam, threshold)
        
        # Also compute individual orientation scores
        for orient, cand_matrix in build_orientation_candidates(matrix):
            payload = build_decoded_sheet_payload(sheet, cand_matrix, template, exam, threshold, None, orient)
            score = score_decoded_sheet_candidate(payload, exam)
            ans = dict(sorted(payload["answers"].items(), key=lambda x: int(x[0])))
            fields = payload.get("decoded_fields", {})
            print(f"\n  [{orient}] score={score}")
            print(f"    answers={ans}")
            print(f"    booklet={payload.get('booklet_code','?')}, fields={fields}")
        
        # Show what decode_sheet actually picked
        final_ans = dict(sorted(decoded["answers"].items(), key=lambda x: int(x[0])))
        final_fields = decoded.get("decoded_fields", {})
        print(f"\n  === WINNER: orient={decoded['matrix_orientation']}, corrected={decoded['matrix_orientation_corrected']} ===")
        print(f"    answers={final_ans}")
        print(f"    booklet={decoded.get('booklet_code','?')}")
        print(f"    fields={final_fields}")
        print(f"    warnings={decoded.get('warnings', [])}")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
