"""Sinav kodu ve tarih alanlarini ham matristen detayli izle."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.device_service import parse_mark_output_detailed
from backend.app.optical_form_service import (
    decode_sheet,
    decode_auxiliary_fields,
    get_named_field_regions,
    parse_form_template,
    EXPLICIT_TEMPLATE_COORDINATE_SOURCES,
)

raw_path = ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"
raw = raw_path.read_text(encoding="utf-8")
sheets = parse_mark_output_detailed(raw)
if not sheets:
    print("HATA: Sheet bulunamadi!")
    sys.exit(1)

original_matrix = sheets[0]["front_matrix"]
flipped = list(reversed(original_matrix))

template = parse_form_template(ROOT, "varsayilan")
named_regions = get_named_field_regions(template)

THR = 12

print(f"Matris: {len(original_matrix)}x{len(original_matrix[0])}")
print(f"Template regions: {sorted(named_regions.keys())}")
print()

# Flipped matristeki TUM sifir-olmayan hucrelerin tam haritasi
print("=== FLIP_VERTICAL: Tum esik-ustu hucreler ===")
for r, row in enumerate(flipped):
    for c, val in enumerate(row):
        if val >= THR:
            print(f"  R{r+1:02d}C{c+1:02d} = {val}")

print()

# Ilgili alan bolgeleri
fields_of_interest = [
    "exam_code_prefix", "exam_code_number",
    "exam_date_day", "exam_date_month", "exam_date_year",
    "class_number", "class_section",
    "student_number",
]

for fname in fields_of_interest:
    reg = named_regions.get(fname)
    if not reg:
        print(f"{fname}: BOLGE YOK!")
        continue
    sr = reg["start_row"]
    er = reg["end_row"]
    sc = reg["start_column"]
    ec = reg["end_column"]
    rev = reg.get("reverse_columns", False)
    print(f"--- {fname} (R{sr}-{er}, C{sc}-{ec}, reverse={rev}) ---")

    # Her sutun icin flipped matristeki degerler
    for col in range(sc, ec + 1):
        vals = []
        for row in range(sr, er + 1):
            v = flipped[row - 1][col - 1] if row - 1 < len(flipped) and col - 1 < len(flipped[0]) else -1
            vals.append(v)
        above = [(i, v) for i, v in enumerate(vals) if v >= THR]
        if above:
            print(f"  C{col}: vals={vals} -> esik-ustu={above}")
        else:
            maxv = max(vals) if vals else 0
            print(f"  C{col}: TUM SIFIR (max={maxv})")

    print()

# Simdi decode_auxiliary_fields ile ne cikiyor bakalim
print("=== decode_auxiliary_fields SONUCLARI ===")
decoded_fields, warnings = decode_auxiliary_fields(flipped, template, THR)
for k, v in sorted(decoded_fields.items()):
    print(f"  {k}: [{v}]")
if warnings:
    print(f"  UYARILAR: {warnings}")

# Full decode
print("\n=== decode_sheet SONUCLARI ===")
plain_exam = {"booklet_codes": [], "questions": []}
decoded = decode_sheet(sheets[0], template, plain_exam, threshold=THR)
df = decoded.get("decoded_fields", {})
for k, v in sorted(df.items()):
    print(f"  {k}: [{v}]")
print(f"  orientation: [{decoded.get('matrix_orientation')}]")
print(f"  answers(1-5): {[decoded.get('answers',{}).get(str(i),'(bos)') for i in range(1,6)]}")
