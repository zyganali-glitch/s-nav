# Agent Environment And API

- Kullanici ortami: Windows.
- Donor governance paketi: `Universal-Agent-OS/`.
- Hedef deploy modeli Phase-0 sonunda netlesti: ayni cihazda calisan lokal web uygulamasi.
- Scanner driver entegrasyonu MVP disi; import tabanli akis once gelir.
- Lokal runtime komutu: `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8140`.
- Ana URL: `http://127.0.0.1:8140`
- Lokal state dosyasi: `backend/data/app_state.json`
- Ana API yuzeyleri: `/api/health`, `/api/exams`, `/api/exams/{exam_code}`, `/api/exams/{exam_code}/imports`