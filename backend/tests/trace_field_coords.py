"""
Ham matristeki sinif, sinav kodu ve tarih alanlarindaki hucre degerlerini
dogrudan oku ve decode zincirini adim adim izle.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.device_service import parse_mark_output_detailed
from backend.app.optical_form_service import (
    decode_sheet,
    parse_form_template,
    EXPLICIT_TEMPLATE_COORDINATE_SOURCES,
)

# ---------- matris oku ----------
raw_path = ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"
raw = raw_path.read_text(encoding="utf-8")
sheets = parse_mark_output_detailed(raw)
if not sheets:
    print("HATA: Hic sheet bulunamadi!")
    sys.exit(1)

original_matrix = sheets[0]["front_matrix"]
# flip_vertical uygula (decode'da kazanan oryantasyon)
flipped_matrix = list(reversed(original_matrix))

print(f"Matris boyutu: {len(original_matrix)} satir x {len(original_matrix[0])} sutun")
print()

# ---------- alan koordinatlari ----------
varsayilan = EXPLICIT_TEMPLATE_COORDINATE_SOURCES["varsayilan"]

fields_to_check = {
    "class_number": {"start_row": 23, "end_row": 32, "start_column": 31, "end_column": 33, "choices": "0123456789"},
    "class_section": {"start_row": 23, "end_row": 32, "start_column": 34, "end_column": 34, "choices": "ABCDEFGHIJ"},
    "exam_code_prefix": {"start_row": 46, "end_row": 55, "start_column": 45, "end_column": 45, "choices": "ABCDEFGHIJ"},
    "exam_code_number": {"start_row": 46, "end_row": 55, "start_column": 42, "end_column": 44, "choices": "0123456789"},
    "exam_date_day": {"start_row": 46, "end_row": 55, "start_column": 38, "end_column": 39, "choices": "0123456789"},
    "exam_date_month": {"start_row": 46, "end_row": 55, "start_column": 36, "end_column": 37, "choices": "0123456789"},
    "exam_date_year": {"start_row": 46, "end_row": 55, "start_column": 32, "end_column": 35, "choices": "0123456789"},
    "booklet_code": {"start_row": 37, "end_row": 37, "start_column": 36, "end_column": 42, "choices": "DCBA"},
    "student_number": {"start_row": 23, "end_row": 32, "start_column": 35, "end_column": 45, "choices": "0123456789"},
}

THRESHOLD = 12

for label in ["FLIP_VERTICAL (cihaz duzeltilmis)", "AS_IS (cihazdan gelen ham)"]:
    matrix = flipped_matrix if "FLIP" in label else original_matrix
    print(f"======== {label} ========")

    for field_name, coords in fields_to_check.items():
        sr = coords["start_row"] - 1  # 0-based
        er = coords["end_row"] - 1
        sc = coords["start_column"] - 1
        ec = coords["end_column"] - 1
        choices = coords["choices"]

        print(f"\n--- {field_name} (satir {coords['start_row']}-{coords['end_row']}, sutun {coords['start_column']}-{coords['end_column']}) ---")

        # Her sutun icin dikey decode yap (D ekseni)
        if field_name == "booklet_code":
            # Y ekseni: yatay okuma, tek satir
            row = matrix[sr]
            vals = [row[c] for c in range(sc, ec + 1)]
            print(f"  Satir {coords['start_row']} degerler: {vals}")
            decoded_idx = None
            for ci, v in enumerate(vals):
                if v >= THRESHOLD:
                    decoded_idx = ci
                    break
            if decoded_idx is not None:
                print(f"  Kazanan index={decoded_idx} -> '{choices[decoded_idx]}' (deger={vals[decoded_idx]})")
            else:
                print(f"  ESIK USTU DEGER YOK! Max={max(vals)}")
        else:
            num_cols = ec - sc + 1
            result_chars = []
            for col_offset in range(num_cols):
                col = sc + col_offset
                col_vals = [matrix[r][col] for r in range(sr, er + 1)]
                above_threshold = [(i, v) for i, v in enumerate(col_vals) if v >= THRESHOLD]
                print(f"  Sutun {col+1}: vals={col_vals} above_thr={above_threshold}")

                if len(above_threshold) == 1:
                    idx = above_threshold[0][0]
                    result_chars.append(choices[idx])
                elif len(above_threshold) == 0:
                    result_chars.append("_")
                else:
                    result_chars.append(f"?({','.join(choices[a[0]] for a in above_threshold)})")

            decoded_value = "".join(result_chars)
            print(f"  => DECODE: [{decoded_value}]")

    print()
