"""Diagnostic script: parse last-mark-read.txt and decode using current template coordinates."""

import re, sys, pathlib

# Add parent to path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from backend.app.optical_form_service import (
    parse_form_template,
    get_answer_regions,
    get_booklet_region,
    get_named_field_regions,
    decode_horizontal_pattern,
    decode_vertical_region_once,
    decode_answers_from_sheet,
    detect_booklet_code,
    decode_auxiliary_fields,
)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DEVICE_FILE = PROJECT_ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"


def parse_sheets_from_file(path: pathlib.Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    sheets = []
    for match in re.finditer(
        r"\[sheet_(\d+)\].*?front_rows=(\d+).*?front_columns=(\d+).*?front_marks=\s*(.*?)\s*\[/sheet_\1\]",
        text,
        re.DOTALL,
    ):
        sheet_no = int(match.group(1))
        rows_expected = int(match.group(2))
        cols_expected = int(match.group(3))
        raw_lines = [l.strip() for l in match.group(4).strip().splitlines() if l.strip()]
        matrix = []
        for line in raw_lines:
            matrix.append([int(c) for c in line.split(",")])
        sheets.append({
            "sheet_no": sheet_no,
            "rows_expected": rows_expected,
            "cols_expected": cols_expected,
            "front_matrix": matrix,
        })
    return sheets


def dump_answer_region_raw(matrix, region, label, threshold=12):
    """Print raw cell values for each question row in an answer region."""
    print(f"\n  --- {label}: rows {region['start_row']}-{region['end_row']}, cols {region['start_column']}-{region['end_column']}, pattern={region['pattern']} ---")
    start_col = region["start_column"] - 1
    end_col = region["end_column"]
    pattern = region["pattern"]
    
    q_num = 1
    for row_offset in range(region["row_count"]):
        row_idx = region["start_row"] - 1 + row_offset
        if row_idx >= len(matrix):
            print(f"  Q{q_num}: ROW {row_idx} BEYOND MATRIX (len={len(matrix)})")
            q_num += 1
            continue
        row = matrix[row_idx]
        segment = row[start_col:end_col]
        # Show raw values aligned with pattern chars
        cell_labels = []
        for i, val in enumerate(segment):
            ch = pattern[i] if i < len(pattern) else "?"
            cell_labels.append(f"{ch}={val:2d}")
        answer, status = decode_horizontal_pattern(segment, pattern, threshold)
        print(f"  Q{q_num:3d} (row {row_idx:2d}): [{', '.join(cell_labels)}] -> answer={answer or '?':1s} status={status}")
        q_num += 1


def dump_vertical_region_raw(matrix, region, label, threshold=12):
    """Print raw cell values for each column in a vertical (D-axis) region."""
    print(f"\n  --- {label}: rows {region['start_row']}-{region['end_row']}, cols {region['start_column']}-{region['end_column']}, choices={region.get('choices',[])} ---")
    rev = region.get("reverse_columns", False)
    col_offsets = list(range(region["column_count"]))
    if rev:
        col_offsets.reverse()
    for col_offset_idx, col_offset in enumerate(col_offsets):
        col_idx = region["start_column"] - 1 + col_offset
        vals = []
        for row_offset in range(region["row_count"]):
            row_idx = region["start_row"] - 1 + row_offset
            if row_idx < len(matrix) and col_idx < len(matrix[row_idx]):
                vals.append(matrix[row_idx][col_idx])
            else:
                vals.append(-1)
        marked = [(i, v) for i, v in enumerate(vals) if v > 0]
        print(f"  col_offset={col_offset:2d} (matrix_col={col_idx:2d}, output_pos={col_offset_idx}): marked={marked}")


def main():
    if not DEVICE_FILE.exists():
        print(f"Device file not found: {DEVICE_FILE}")
        return

    sheets = parse_sheets_from_file(DEVICE_FILE)
    print(f"Parsed {len(sheets)} sheets from {DEVICE_FILE.name}")

    template = parse_form_template(PROJECT_ROOT, "varsayilan")
    print(f"Template: {template['template']['id']}, rows={template['rows']}, cols={template['columns']}")
    
    answer_regions = get_answer_regions(template)
    print(f"Answer regions: {len(answer_regions)}")
    for i, r in enumerate(answer_regions):
        print(f"  [{i}] rows {r['start_row']}-{r['end_row']}, cols {r['start_column']}-{r['end_column']}, pattern={r['pattern']}")
    
    booklet_region = get_booklet_region(template, ["A", "B", "C", "D"])
    if booklet_region:
        print(f"Booklet region: row {booklet_region['start_row']}-{booklet_region['end_row']}, cols {booklet_region['start_column']}-{booklet_region['end_column']}, pattern={booklet_region['pattern']}")
    
    named_regions = get_named_field_regions(template)
    print(f"Named field regions: {list(named_regions.keys())}")
    
    threshold = 12
    exam_stub = {"booklet_codes": ["A", "B", "C", "D"]}

    for sheet in sheets:
        matrix = sheet["front_matrix"]
        print(f"\n{'='*80}")
        print(f"SHEET {sheet['sheet_no']}: {len(matrix)} rows x {len(matrix[0]) if matrix else 0} cols")
        print(f"{'='*80}")
        
        # Timing column (last column) - verify form alignment
        timing_vals = [row[-1] if row else 0 for row in matrix]
        print(f"  Timing column (col {len(matrix[0]) if matrix else '?'}): first 10 = {timing_vals[:10]}, last 5 = {timing_vals[-5:]}")
        
        # Row 0/col 0 check (often timing)
        col0_vals = [row[0] if row else 0 for row in matrix]
        col0_nonzero = [(i, v) for i, v in enumerate(col0_vals) if v > 0]
        print(f"  Column 0 nonzero: {col0_nonzero}")
        
        # Booklet decode
        if booklet_region:
            br_row = booklet_region["start_row"] - 1
            br_start = booklet_region["start_column"] - 1
            br_end = booklet_region["end_column"]
            if br_row < len(matrix):
                br_segment = matrix[br_row][br_start:br_end]
                br_pattern = booklet_region["pattern"]
                br_labels = [f"{br_pattern[i] if i < len(br_pattern) else '?'}={v:2d}" for i, v in enumerate(br_segment)]
                booklet_answer, booklet_status = decode_horizontal_pattern(br_segment, br_pattern, threshold)
                print(f"  Booklet (row {br_row}): [{', '.join(br_labels)}] -> {booklet_answer or '?'} ({booklet_status})")
        
        # Named fields
        for field_name, region in named_regions.items():
            if field_name in ("student_name", "student_surname"):
                dump_vertical_region_raw(matrix, region, field_name, threshold)
            elif field_name == "student_number":
                dump_vertical_region_raw(matrix, region, field_name, threshold)
        
        # Answers
        q_global = 1
        for i, region in enumerate(answer_regions):
            dump_answer_region_raw(matrix, region, f"answer_block_{i+1}", threshold)
        
        # Summary from actual decode functions
        answers, warnings = decode_answers_from_sheet(matrix, template, threshold)
        print(f"\n  DECODED ANSWERS: {dict(sorted(answers.items(), key=lambda x: int(x[0])))}")
        if warnings:
            print(f"  WARNINGS: {warnings}")
        
        # Also decode auxiliary fields
        fields, field_warnings = decode_auxiliary_fields(matrix, template, threshold)
        print(f"  DECODED FIELDS: {fields}")
        if field_warnings:
            print(f"  FIELD WARNINGS: {field_warnings}")
        
        # Now try with flipped matrix
        flipped = list(reversed(matrix))
        answers_flipped, warnings_flipped = decode_answers_from_sheet(flipped, template, threshold)
        fields_flipped, _ = decode_auxiliary_fields(flipped, template, threshold)
        print(f"\n  FLIPPED ANSWERS: {dict(sorted(answers_flipped.items(), key=lambda x: int(x[0])))}")
        print(f"  FLIPPED FIELDS: {fields_flipped}")


if __name__ == "__main__":
    main()
