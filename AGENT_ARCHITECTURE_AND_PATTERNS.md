# Agent Architecture And Patterns

- Hedef ilk mimari: lokal web tabanli teacher/operator arayuzu + backend API.
- Additive ve moduler dosya yapisi zorunlu.
- Shared governance dosyalari tek yazarla ilerletilir.
- UI sade, hizli ve operator odakli olacak; gorev akisi fazladan tiklama uretmeyecek.
- Secilen ilk stack: `FastAPI + vanilla JS + lokal JSON state`.
- Sinav modeli `kanonik soru` + `kitapcik bazli sira/dogru cevap eslemesi` uzerinden yurur.
- Backend servis katmani `exam_service.py`, `import_service.py`, `storage.py` olarak ayristirilir.
- Frontend tek sayfada teacher-prep, operator import ve analiz ozetlerini birlikte sunar.
- Rollout mimarisi ogretmen-prep ekranini ileride acilabilir tutsa da ilk yayginlasmada operator-first calisir; ayni kullanici ayni cihazda hem prep hem okutma adimlarini ardisk sekilde yurutur.
- Akademik analiz katmani kanonik soru agirligi ve kitapcik permutasyonu gibi alanlarda sessiz fallback'e dayanmaz; explicit kaynak yoksa durumu `provizyonel`/`eksik metadata` olarak isaretleyecek akislara oncelik verilir.