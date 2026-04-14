"""Quick dump of decoded sheets from debug state."""
import json, pathlib

for fname in ("_tmp_debug_state.json", "_tmp_state2.json"):
    fpath = pathlib.Path("backend/data") / fname
    if not fpath.exists():
        continue
    data = json.loads(fpath.read_text("utf-8"))
    print(f"\n=== {fname} ===")
    for code, exam in data.get("exams", {}).items():
        print(f"Exam: {code}, template={exam.get('form_template_id')}")
        print(f"  Questions: {len(exam.get('questions', []))}")
        print(f"  Booklets: {exam.get('booklet_codes', [])}")
        for s in exam.get("sessions", []):
            sid = s.get("session_id", "?")
            print(f"  Session: {sid}")
            for ds in s.get("decoded_sheets", []):
                sno = ds.get("sheet_no")
                ans = ds.get("answers", {})
                fields = ds.get("decoded_fields", {})
                orient = ds.get("matrix_orientation", "?")
                thresh = ds.get("analysis_threshold_used", "?")
                corrected = ds.get("matrix_orientation_corrected", "?")
                warnings = ds.get("warnings", [])
                # Sort answers by position
                sorted_ans = dict(sorted(ans.items(), key=lambda x: int(x[0])))
                print(f"    Sheet {sno}: orient={orient}, corrected={corrected}, threshold={thresh}")
                print(f"      answers={sorted_ans}")
                print(f"      fields={fields}")
                if warnings:
                    print(f"      warnings={warnings}")
