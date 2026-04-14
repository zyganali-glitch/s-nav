"""
SIN ADAM formunu ham cihaz verisinden decode edip tum alanlari goster.
last-mark-read.txt dosyasindaki tek sheet.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.device_service import parse_mark_output_detailed
from backend.app.optical_form_service import (
    decode_sheet,
    parse_form_template,
)

# ---------- ham veriyi oku ----------
raw_path = ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"
raw = raw_path.read_text(encoding="utf-8")
sheets = parse_mark_output_detailed(raw)
print(f"Toplam yaprak: {len(sheets)}")
for i, s in enumerate(sheets):
    m = s.get("front_matrix", [])
    print(f"  Sheet {s.get('sheet_no')}: {len(m)} satir x {len(m[0]) if m else 0} sutun")

# ---------- template ----------
template = parse_form_template(ROOT, "varsayilan")

# Kitapciksiz basit exam (saf pozisyon decode)
plain_exam = {"booklet_codes": [], "questions": []}

for sidx, sheet_data in enumerate(sheets):
    decoded = decode_sheet(sheet_data, template, plain_exam, threshold=12)
    df = decoded.get("decoded_fields", {})
    print(f"\n===== SHEET {sheet_data.get('sheet_no')} DECODE =====")
    print(f"Ad (name):       [{df.get('name', '(bos)')}]")
    print(f"Soyad (surname): [{df.get('surname', '(bos)')}]")
    print(f"Ogrenci No:      [{df.get('student_number', '(bos)')}]")
    print(f"Sinif (class):   [{df.get('class_code', '(bos)')}]")
    print(f"Sinav Kodu:      [{df.get('exam_code', '(bos)')}]")
    print(f"Sinav Tarihi:    [{df.get('exam_date', '(bos)')}]")
    print(f"Kitapcik:        [{decoded.get('booklet_code', '(bos)')}]")
    print(f"Oryantasyon:     [{decoded.get('matrix_orientation', '(bos)')}]")

    answers = decoded.get("answers", {})
    print("Cevaplar (ilk 10):")
    for i in range(1, 11):
        v = answers.get(str(i), "(bos)")
        print(f"  Q{i}: {v}")

    # decoded_fields icindeki TUM alanlari goster
    print("TUM decoded_fields:")
    for k, v in sorted(df.items()):
        print(f"  {k}: [{v}]")
