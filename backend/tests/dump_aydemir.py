"""Dump AYDEMIR exam decoded sheets."""
import json, pathlib

data = json.loads(pathlib.Path("backend/data/app_state.json").read_text("utf-8"))
exam = data["exams"]["AYDEMIR"]
q_count = len(exam.get("questions", []))
booklets = exam.get("booklet_codes", [])
print(f"Exam: AYDEMIR, questions={q_count}, booklets={booklets}")
for q in exam.get("questions", []):
    print(f"  Q{q['canonical_no']}: bk_mappings={q.get('booklet_mappings', {})}")

for s in exam.get("sessions", []):
    sid = s.get("session_id", "?")
    sheets = s.get("decoded_sheets", [])
    print(f"\nSession: {sid}, sheets={len(sheets)}")
    for ds in sheets:
        sno = ds.get("sheet_no")
        ans = ds.get("answers", {})
        orient = ds.get("matrix_orientation", "?")
        corrected = ds.get("matrix_orientation_corrected", False)
        thresh = ds.get("analysis_threshold_used", "?")
        fields = ds.get("decoded_fields", {})
        sorted_ans = dict(sorted(ans.items(), key=lambda x: int(x[0])))
        print(f"  Sheet {sno}: orient={orient}, corrected={corrected}, threshold={thresh}")
        print(f"    answers={sorted_ans}")
        print(f"    fields={fields}")
        warns = ds.get("warnings", [])
        if warns:
            print(f"    warnings={warns}")
