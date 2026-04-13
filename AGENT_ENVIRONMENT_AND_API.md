# Agent Environment And API

- Kullanici ortami: Windows.
- Donor governance paketi: `Universal-Agent-OS/`.
- Hedef deploy modeli Phase-0 sonunda genisletildi: ayni frontend/API kaynagindan hem lokal browser uzerinde calisan desktop-web hem Windows masaustu launcher/installer dagitimi.
- Scanner driver entegrasyonu MVP disi; import tabanli akis once gelir.
- Lokal runtime komutu: `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8140`.
- Ana URL: `http://127.0.0.1:8140`
- Lokal state dosyasi: `backend/data/app_state.json`
- Hedef operator runtime yolu: `launcher -> localhost health-check -> varsayilan browser -> ayni UI`; kalici veri bundle klasoru yerine yazilabilir dis klasore yonlendirilmelidir.
- Cihaz direct-read baseline kaniti: SR-3500 donor makinede vendor x86 SDK uzerinden alindi; SR-6000 ve ayni driver ailesi icin destek yalniz gercek probe + packaged runtime smoke sonrasinda acilacak.
- Ana API yuzeyleri: `/api/health`, `/api/exams`, `/api/exams/{exam_code}`, `/api/exams/{exam_code}/imports`

