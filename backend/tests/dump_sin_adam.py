"""SIN ADAM ogrencisinin mevcut decode durumunu yazdir."""
import json
from pathlib import Path

state_path = Path(__file__).resolve().parent.parent / "data" / "app_state.runtime.json"
with open(state_path, encoding="utf-8") as f:
    state = json.load(f)

for ek, ev in state.get("exams", {}).items():
    for sess in ev.get("reading_sessions", []):
        for st in sess.get("students", []):
            nm = str(st.get("decoded_fields", {}).get("name", "")).upper()
            sn = str(st.get("decoded_fields", {}).get("surname", "")).upper()
            if "SIN" in nm or "ADAM" in sn:
                df = st.get("decoded_fields", {})
                print(f"SINAV: {ek}")
                print("decoded_fields:")
                for k, v in df.items():
                    print(f"  {k}: [{v}]")
                print(f"booklet_code: {st.get('booklet_code')}")
                print(f"orientation: {st.get('matrix_orientation')}")
                ans = st.get("answers", {})
                for i in range(1, 6):
                    print(f"  Q{i}: {ans.get(str(i), '(yok)')}")
                qrs = st.get("question_responses", [])[:5]
                print("question_responses (ilk 5):")
                for qr in qrs:
                    cn = qr.get("canonical_no")
                    mk = qr.get("marked_answer")
                    bp = qr.get("booklet_position")
                    dv = qr.get("display_value")
                    print(f"  canon={cn} pos={bp} marked={mk} display={dv}")
