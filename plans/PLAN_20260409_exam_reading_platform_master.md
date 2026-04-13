# Exam Reading Platform Master Plan

Bu plan self-contained'dir.
Bu plan, QR'siz sinav okuma platformunun governance bootstrap'ini, Phase-0 mutabakatini ve sonraki MVP implementasyon fazlarini yonetir.

---

## 0) Belge Kimligi

- Plan dosya adi: `PLAN_20260409_exam_reading_platform_master.md`
- Aktif plan yolu: `plans/PLAN_20260409_exam_reading_platform_master.md`
- Tamamlanan plan yolu: `plans/completed/PLAN_20260409_exam_reading_platform_master.md`
- Plan ID: `ERP-20260409-ROOT`
- Hedef platform: `DESKTOP-WEB`
- Son guncelleme: `2026-04-13 15:33 TRT`
- Plan sahibi: `GitHub Copilot`
- Aktif durum: `IN_PROGRESS`

### 0.1) Integrity Lock

- IL-01: Gorev takip cizelgesi resmi kaynaktir.
- IL-02: Header + faz + backlog + task table + gate + risk + handoff ayni editte guncellenir.
- IL-03: Alt kalemler acikken ust kalem kapanmaz.
- IL-04: Gelecek tarihli tamamlanma yazilmaz.
- IL-05: Zorunlu gate PASS olmadan closure verilmez.
- IL-06: Yeni kesfedilen is `[DISCOVERED]` satiri olarak eklenir.
- IL-07: Mikro-adim baslamadan `DEVAM`, bitince kanit yazilir.

---

## 1) Phase-0 Kararlari

- Iletisim tonu: `Pragmatik mentor`
- Platform: `Desktop-web, ayni cihazdan kullanilan lokal MVP`
- Dagitim modeli: `Ayni bilgisayarda calisan lokal web uygulamasi`
- Veri saklama modeli: `Ilk fazda hafif lokal veritabani + import dosyalari`
- Auth/Billing kapsami: `Tek operator uygulamasi; login yok, billing yok`
- Dil modeli: `TR-only`

Kilidi acilan Phase-0 kararlari:
- Ogretmen ve operator ilk MVP'de ayni cihazdan calisacak.
- Ilk faz import tipi `CSV/Excel` ve `vendor export TXT/CSV` birlikte destekleyecek.
- Rol bazli giris olmayacak; tek uygulamada teacher-prep ve operator-run ekranlari olacak.
- Arayuz ilk teslimde yalniz Turkce olacak.

---

## 2) Scope Lock

- Kapsam ici: `Teacher-prep sinav tanimi, operator-run sinav kodu ile oturum baslatma, agirlikli soru puanlama, kitapcik esleme, soru/grup bazli temel analiz, QR'siz akis, vendor export veya manuel veri importu, lokal web uygulamasi governance ve MVP implementasyonu.`
- Kapsam disi: `QR, dogrudan scanner driver/TWAIN entegrasyonu, mobil native uygulama, bulut SaaS billing, canli deploy.`
- En kucuk sonraki adim: `Gercek vendor export dosyasi ile import toleranslarini saha formatina gore sertlestirmek.`

---

## 3) Allowlist

- `AGENTS.md`
- `GLOBAL_PLAN_TASK_TRACKING_TEMPLATE.md`
- `README.md`
- `AGENT_MEMORY_AND_LESSONS.md`
- `AGENT_ARCHITECTURE_AND_PATTERNS.md`
- `AGENT_ENVIRONMENT_AND_API.md`
- `AGENT_USER_PREFERENCES.md`
- `plans/PLAN_20260409_exam_reading_platform_master.md`
- `backend/**`
- `frontend/**`
- `tests/**`
- `docs/**`

---

## 4) Faz Plani

| Faz | Aciklama | Durum |
|---|---|---|
| F1 | Governance bootstrap ve Phase-0 mutabakati | TAMAMLANDI |
| F2 | Domain modeli ve backend iskeleti | TAMAMLANDI |
| F3 | Ogretmen ve operator arayuzu | TAMAMLANDI |
| F4 | Test, smoke ve yerel calistirma | DEVAM |

---

## 5) Mikro-Faz Backlogu

| ID | Baslik | Durum |
|---|---|---|
| MF-01 | Dogru kokte governance yuzeylerini olustur | TAMAMLANDI |
| MF-02 | Phase-0 kararlarini kullaniciyla kilitle | TAMAMLANDI |
| MF-03 | Backend domain ve import/puanlama iskeletini kur | TAMAMLANDI |
| MF-04 | Frontend teacher/operator akisini kur | TAMAMLANDI |
| MF-05 | Test, smoke ve uygulama baslatma | DEVAM |
| MF-06 | README canli dokumantasyonunu guncelle ve GitHub snapshot yedegi al | DEVAM |

---

## 6) Talep Derleme Tablosu

| REQ-ID | Talep | Kapsam | Durum |
|---|---|---|---|
| REQ-01 | Hoca sinav katmanlarini onceden girsin | MVP | DEVAM |
| REQ-02 | Operator sinav ID ile okutma baslatsin | MVP | DEVAM |
| REQ-03 | Agirlikli puan ve kitapcik/grup bazli analizler olsun | MVP | DEVAM |
| REQ-04 | QR olmasin | MVP | TAMAMLANDI |
| REQ-05 | Yanlis repoda baslayan is bu koke tasinsin | Governance | TAMAMLANDI |
| REQ-06 | Guncel README hazirlansin ve repo GitHub'a yedeklensin | Governance | DEVAM |

---

## 7) Gorev Takip Cizelgesi

| Faz | Adim | Aciklama | Durum | Ust ID | Ajan | Baslangic | Tamamlanma | Parity | Notlar |
|---|---|---|---|---|---|---|---|---|---|
| F1 | F1.1 | Donor kurallari oku ve dogru proje kokunu belirle | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | `Universal-Agent-OS/tr/AGENT_OS_RULES.md` ve donor sablon okundu |
| F1 | F1.2 | Proje kokunde governance dosyalari ve aktif master plani olustur | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | README, AGENTS, memory surfaces ve master plan acildi |
| F1 | F1.3 | [DISCOVERED] Yanlis repodaki task-ozel dosyalari temizle | TAMAMLANDI | REQ-05 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | OPRADOX tarafinda exam-platform'a ait task-ozel kod bulunmadi; unrelated degisikliklere dokunulmadi |
| F1 | F1.4 | Kullanicidan kalan Phase-0 kararlarini topla ve kilitle | TAMAMLANDI | MF-02 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | Ayni cihaz, CSV/Excel + vendor export, login'siz tek uygulama, TR-only karar kilidi alindi |
| F2 | F2.1 | Backend domain ve proje iskeletini kur | TAMAMLANDI | MF-03 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | FastAPI API, lokal JSON persist, import parser ve puanlama servisi kuruldu |
| F3 | F3.1 | Ogretmen ve operator arayuzunu ayni sayfada ac | TAMAMLANDI | MF-04 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | TR-only vanilla JS arayuzu teacher-prep, import ve analiz panelleriyle kuruldu |
| F4 | F4.1 | Test, smoke ve restore parity kosularini yap | DEVAM | MF-05 | GitHub Copilot | 2026-04-09 | - | OK | Paketlenmis son frontend source'a geri tasindi; `pytest backend/tests/test_exam_flow.py backend/tests/test_device_service.py backend/tests/test_optical_form_flow.py -q` -> `27 passed`; `/api/health` ve root smoke 2026-04-13'te tekrar dogrulandi |
| F4 | F4.2 | [DISCOVERED] Cok kitapcikli optik cevap anahtari okuma sayisini kitapcik/pending adetle sinirla | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.main` icinde device-answer-key path'i explicit limit yoksa toplam/pending kitapcik adedi kadar `max_sheets` uygular; `pytest backend/tests/test_optical_form_flow.py -k "defaults_max_sheets or mixed_booklets_in_single_pass or reads_multiple_booklets_in_single_pass" -q` -> `4 passed`; `pytest backend/tests/test_optical_form_flow.py -q` -> `20 passed` |
| F4 | F4.3 | [DISCOVERED] Canli operator kabul bosluklarini kapat: canli import, silme, export, decode alanlari ve detayli analiz | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | TODO | Kullanici canli testte `Okunanlari ice aktar` pasifligi, sinav silme eksigi, ogrenci no yon problemi, sinif/ad-soyad decode eksigi, sinav kodu/tarih gorunurlugu ve analiz yetersizligini raporladi |
| F4 | F4.4 | [DISCOVERED] Ciktilari tam bloklu rapora cevir: kitapcik/grup/soru/ogrenci bloklari, soru-yanit matrisi, sinav geneli sirasi ve secilebilir net kurali | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | Session modeli agirlik-duyarli deterministic akademik yorum, birlestirilmis metodoloji tablosu ve soru bazli dagilimin altinda ayrica sik-cevap dagilim tablosu ile genisletildi; legacy session hydration artik bu yeni yorum/tablo alanlarini da geriye donuk dolduruyor; PDF export hucreleri sarilabilir paragraf + sayfaya olceklenen kolon genisligi ile yeniden kuruldu; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `42 passed, 1 deselected`; localhost `http://127.0.0.1:8141` uzerinde ayakta |
| F4 | F4.5 | [DISCOVERED] README'yi canli durumla hizala ve GitHub snapshot yedegini al | DEVAM | MF-06 | GitHub Copilot | 2026-04-13 | - | TODO | Mevcut kok README ilk MVP asamasinda kalmis durumda; guncel optik/raporlama/yedekleme akislarini anlatan README yazilip hedef GitHub reposuna push alinacak |

---

## 8) Gate Plani

| Gate | Durum | Kanit |
|---|---|---|
| Smoke Gate | PASS | `uvicorn backend.app.main:app --host 127.0.0.1 --port 8140` sonrasi `/api/health` `{"status":"ok"}` ve root HTML cevabi alindi |
| Binding Gate | PASS | `backend/tests/test_exam_flow.py` exam save + CSV import + vendor-style TXT import akisini dogruladi |
| Related-Tests Gate | PASS | `pytest backend/tests/test_exam_flow.py -q` -> `2 passed` |
| Parity Gate | PASS | Backend API, static frontend ve lokal state ayni repo kokunden servis ediliyor; source ayrismasi yok |
| No-UI-Regression Gate | DEVAM | Agirlik-duyarli yorum, birlestirilmis metodoloji tablosu, yeni sik-dagilim tablosu ve PDF satir sarma/kolon olcekleme kod/test tarafinda eklendi; cache-bust varligi `20260413c` ile yukseltildi; guncel localhost instance `http://127.0.0.1:8141` uzerinde hazir, gercek operator kabul turu bekleniyor |
| I18N-Completeness Gate | PASS | Phase-0 TR-only kilidi dogrultusunda arayuz Turkceye cekildi; karisik dil etiketleri temizlendi |
| Integrity-Lock Gate | PASS | Header, faz, backlog, task, gate, risk ve handoff ayni editte implementasyon ve test kanitiyle guncellendi |
| Repo-Snapshot Gate | DEVAM | Workspace halen git ile baslatilmamis durumda; README guncellemesinden sonra hedef `https://github.com/zyganali-glitch/s-nav` reposuna snapshot push denenecek |
| Release/NFR Gate | DEVAM | Gercek saha dosyasi kabul turu bekleniyor |

---

## 9) Risk Kaydi

| Risk ID | Risk | Durum | Azaltma |
|---|---|---|---|
| R-01 | Hedef platform karari netlesmeden yanlis stack secilebilir | MITIGATED | Phase-0 kilidi ayni cihazda calisan desktop-web MVP olarak alindi |
| R-02 | Yanlis repoda kalan task dosyalari karisiklik yaratir | MITIGATED | OPRADOX tarafinda task-ozel exam-platform kodu olmadigi dogrulandi; unrelated degisiklikler korunuyor |
| R-03 | QR/dis driver entegrasyonu beklentiye karisabilir | ACK | README ve plan scope lock'ta acikca disarda tut |
| R-04 | Bos scaffold nedeniyle ilk implementasyonda stack secimi gereksiz buyuyebilir | MITIGATED | Minimal FastAPI + vanilla frontend iskeleti ile additive MVP acildi |
| R-05 | Gercek vendor export dosyalari saha varyasyonu nedeniyle parser disinda kolon isimleri kullanabilir | OPEN | Ilk saha kabul turunda gercek export dosyasi ile parser esikleri sertlestirilecek |
| R-06 | Cevap anahtari okut akisinda `max_sheets=0` varsayimi butun tepsiyi tuketip operator sirasini bozabilir | MITIGATED | Device answer-key path'te explicit limit yoksa kitapcik/pending adedi kadar otomatik limit uygulanip optik regresyon testleriyle kilitlendi |
| R-07 | Ham cihaz matrisinde bubble olmayan serbest-yazi alanlari (or. tarih/anket kodu) OCR olmadan geri kazanilamayabilir | OPEN | Bubble kodlu alanlari decode et; bubble olmayan alanlarda session/exam metadata ile gorunurluk sagla ve fiziksel format kaniti gelirse OCR/ek helper yolunu ayir |
| R-08 | Cikti formatlarinda ayni session verisinin farkli tablolarda farkli net/rank hesaplariyla bozulmasi operator guvenini dusurur | OPEN | Net kurali session aninda kilitlenip backend tek kaynaktan rank/net/cevap matrisi uretecek; tum export/UI katmanlari ayni payload'a baglanacak |
| R-09 | Ad/soyad gibi dikey alanlarda kodlama satirinin ustundeki el yazisi veya bir satir asagidan baslayan kodlama named-field decode'unu bozabilir | OPEN | Named-field decode'a kontrollu satir-ofset toleransi ve testli secici skor ekle; cevap bloklarina dokunma |
| R-10 | GitHub hedef reposu bos degilse veya kimlik dogrulamasi yoksa snapshot push bloke olabilir | OPEN | README guncellemesinden sonra remote refs ve push sonucu dogrulanacak; gerekiyorsa kullanicidan sadece auth/overwrite karari istenecek |

---

## 10) Handoff

- Son tamamlanan mikro-adim: `MF-05 agirlik-duyarli deterministic yorum, soru-sik dagilim tablosu ve PDF hucre sarma/kolon olcekleme eklendi; legacy session hydration bu yeni alanlari da dolduruyor; asset cache-bust 20260413c; localhost 8141'de ayakta`
- Sonraki mikro-adim: `Kok README'yi guncel urun durumu, calistirma, persist, export ve optik yeteneklerle yenile; sonra yerel snapshot'i hedef GitHub reposuna push ederek harici yedek al`
- Acik risk/bloke: `Workspace henuz git ile baslatilmamis; hedef repo doluysa veya auth eksikse push akisi bloke olabilir. Bunun disinda legacy sabit-genislik vendor TXT ortalama puan beklentisi (5.5/9.5 farki) halen bilincli olarak kapsam disi; optik sinav kodu/tarih decode'u ve PDF satir sarma davranisinin gercek saha raporlarinda son kabul kaniti henuz alinmadi.`
- Degisen dosyalar: `README.md`, `plans/PLAN_20260409_exam_reading_platform_master.md`
- Gate durumu: `Smoke PASS, Binding PASS, Related-Tests PASS, Parity PASS, I18N PASS, Restore-Regression PASS, No-UI-Regression DEVAM, Repo-Snapshot DEVAM, Release/NFR DEVAM.`
- Checkpoint: `Uygulama tarafi stabil; bu mikro-fazda dokumantasyon vitrini guncellenip harici GitHub snapshot'i alinacak. Sonrasinda tekrar saha kabul turune donulecek.`
