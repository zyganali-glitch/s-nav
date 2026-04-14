"""Dump runtime state sessions."""
import json, pathlib

data = json.loads(pathlib.Path("backend/data/app_state.runtime.json").read_text("utf-8"))
for code, exam in data.get("exams", {}).items():
    sessions = exam.get("sessions", [])
    if not sessions:
        continue
    print(f"Exam: {code}")
    for s in sessions:
        sheets = s.get("decoded_sheets", [])
        sid = s.get("session_id", "?")
        print(f"  Session {sid}: {len(sheets)} sheets")
        for ds in sheets:
            sno = ds.get("sheet_no")
            orient = ds.get("matrix_orientation", "?")
            corrected = ds.get("matrix_orientation_corrected", False)
            thresh = ds.get("analysis_threshold_used", "?")
            ans = ds.get("answers", {})
            fields = ds.get("decoded_fields", {})
            sorted_ans = dict(sorted(ans.items(), key=lambda x: int(x[0])))
            print(f"    Sheet {sno}: orient={orient}, corrected={corrected}, threshold={thresh}")
            print(f"      answers={sorted_ans}")
            print(f"      fields={fields}")
            warns = ds.get("warnings", [])
            if warns:
                print(f"      warnings={warns}")
