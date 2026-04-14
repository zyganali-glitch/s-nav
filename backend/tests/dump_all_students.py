"""Tum runtime ogrencileri listele."""
import json
from pathlib import Path

state_path = Path(__file__).resolve().parent.parent / "data" / "app_state.runtime.json"
with open(state_path, encoding="utf-8") as f:
    state = json.load(f)

for ek, ev in state.get("exams", {}).items():
    print(f"\n=== SINAV: {ek} ({ev.get('title', '')}) ===")
    for si, sess in enumerate(ev.get("reading_sessions", [])):
        print(f"  Oturum {si}: sab={sess.get('template_name')}")
        for j, st in enumerate(sess.get("students", [])):
            df = st.get("decoded_fields", {})
            print(f"    [{j}] name={df.get('name','?')} surname={df.get('surname','?')} "
                  f"no={df.get('student_number','?')} class={df.get('class_code','?')} "
                  f"bk={st.get('booklet_code','?')} orient={st.get('matrix_orientation','?')}")
