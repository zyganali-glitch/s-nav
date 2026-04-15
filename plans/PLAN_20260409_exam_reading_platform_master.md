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
- Son guncelleme: `2026-04-15 15:25 TRT`
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
- Platform: `Desktop-web cekirdegi korunarak ayni kod tabanindan lokal browser + Windows masaustu kabugu`
- Dagitim modeli: `Ayni bilgisayarda calisan lokal web uygulamasi + masaustu kisayollu Windows paket/installer`
- Veri saklama modeli: `Ilk fazda hafif lokal veritabani + import dosyalari`
- Auth/Billing kapsami: `Tek operator uygulamasi; login yok, billing yok`
- Dil modeli: `TR-only`

Kilidi acilan Phase-0 kararlari:
- Ogretmen ve operator ilk MVP'de ayni cihazdan calisacak.
- Baslangic ve yayginlasma fazinda ogretmen erisimi acilmayacak; sinava ait genel bilgiler ile kanonik hazirlik verilerini ayni cihazda operator girecek.
- Teacher-prep ve operator arayuzu browser-temelli ayni frontend olarak korunacak; masaustu uygulamasi bu arayuzu localhost uzerinden acan Windows kabugu olacak.
- Kisa vadeli operator dagitimi icin masaustu ikonu, kisayol ve installer desteklenecek; orta vadeli webe tasima olasiligi icin ayni frontend/API kaynagi korunacak.
- Ilk faz import tipi `CSV/Excel` ve `vendor export TXT/CSV` birlikte destekleyecek.
- Rol bazli giris olmayacak; tek uygulamada teacher-prep ve operator-run ekranlari olacak.
- Arayuz ilk teslimde yalniz Turkce olacak.
- Scanner direct-read tarafinda mevcut donor/kanit zinciri SR-3500 ile olustu; SR-6000 ve ayni driver ailesi icin destek iddiasi yalniz gercek cihaz probe + packaged runtime smoke sonrasinda acilacak.
- Akademik analiz butunlugunde `kanonik soru agirligi` ve `kitapcik bazli soru sirasi` sessiz varsayimla uydurulmayacak; bu alanlar operator tarafinda explicit toplanacak veya analiz/provizyonel durum acik warning ile bloke/etiketlenecek.

---

## 2) Scope Lock

- Kapsam ici: `Teacher-prep sinav tanimi, operator-run sinav kodu ile oturum baslatma, operator-first staged exam prep (ogretmen acilana kadar operatorun genel sinav bilgileri + kanonik soru metadata girmesi), agirlikli soru puanlama, kitapcik esleme, soru/grup bazli temel analiz, QR'siz akis, vendor export veya manuel veri importu, lokal web uygulamasi governance ve MVP implementasyonu, Windows masaustu launcher/installer/kisayol akisi, tek-PC operator kurulum ergonomisi, SR-6000 ve ayni driver ailesi icin uyumluluk matrisi/probe karari, form-tipinden bagimsiz fiziksel optik form <-> ham cihaz matrisi <-> yazilim alan aynalama modeli ve global kurallara bagli teknik-detaysiz yeni form tipi tanimlama.`
- Kapsam disi: `QR, dogrudan scanner driver/TWAIN entegrasyonu disindaki rastgele cihaz aileleri, mobil native uygulama, bulut SaaS billing, canli deploy.`
- En kucuk sonraki adim: `F7 icin aktif form tiplerinin fiziksel bloklari, ham cihaz matrisi ve yazilim alanlari arasinda kanonik aynalama sozlugunu cikarip ilk evidence paketlerini olusturmak.`

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
- `SinavOkumaPlatformu.spec`
- `backend/**`
- `frontend/**`
- `tests/**`
- `docs/**`
- `ops/**`

---

## 4) Faz Plani

| Faz | Aciklama | Durum |
|---|---|---|
| F1 | Governance bootstrap ve Phase-0 mutabakati | TAMAMLANDI |
| F2 | Domain modeli ve backend iskeleti | TAMAMLANDI |
| F3 | Ogretmen ve operator arayuzu | TAMAMLANDI |
| F4 | Test, smoke ve yerel calistirma | DEVAM |
| F5 | Windows masaustu paketleme ve operator kurulum ergonomisi | DEVAM |
| F6 | SR cihaz ailesi uyumluluk matrisi ve secure-PC dogrulamasi | DEVAM |
| F7 | Form-tipinden bagimsiz optik aynalama ve operator-dostu yeni form tipi tanimlama | DEVAM |

---

## 5) Mikro-Faz Backlogu

| ID | Baslik | Durum |
|---|---|---|
| MF-01 | Dogru kokte governance yuzeylerini olustur | TAMAMLANDI |
| MF-02 | Phase-0 kararlarini kullaniciyla kilitle | TAMAMLANDI |
| MF-03 | Backend domain ve import/puanlama iskeletini kur | TAMAMLANDI |
| MF-04 | Frontend teacher/operator akisini kur | TAMAMLANDI |
| MF-05 | Test, smoke ve uygulama baslatma | DEVAM |
| MF-06 | README canli dokumantasyonunu guncelle ve GitHub snapshot yedegi al | TAMAMLANDI |
| MF-07 | Browser cekirdegi korunurken Windows masaustu launcher/installer hattini ekle | DEVAM |
| MF-08 | SR-6000 ve ayni driver ailesi icin destek kararini probe ile kilitle | DEVAM |
| MF-09 | [DISCOVERED] Operator-first kanonik hazirlik akisini minimum tikla ve sessiz varsayimsiz kilitle | DEVAM |
| MF-10 | [DISCOVERED] Gercek SR matrisinde sinif blogu semantigi ve zayif tarih hanesi kabulunu duzelt | TAMAMLANDI |
| MF-11 | [DISCOVERED] Kurumsal rapor basligi, matrix export iyilestirmesi ve toplu ZIP cikti paketi ekle | TAMAMLANDI |
| MF-12 | [DISCOVERED] Hazirlik butunlugu uyarilarini raporda kurumsal Turkce ve kirmizi vurgu ile gorunur kil | TAMAMLANDI |
| MF-13 | [DISCOVERED] Kitapcik sirasi ve blok agirlik hizli-yapistir akisini operator-dostu etkinlestir | TAMAMLANDI |
| MF-14 | [DISCOVERED] `paste-ranges` metadata'sinin optik cevap anahtari sonrasi explicit korunmasini kilitle | TAMAMLANDI |
| MF-15 | [DISCOVERED] Dusuk guvenli cihaz matrisi cozumlerini sahte ogrenci/materializasyon yerine acik bloke et | TAMAMLANDI |
| MF-16 | [DISCOVERED] BSR formunda beklenen soru araligi disindaki hayalet cevaplari orientation skorundan dus ve template-ozel kimlik/date koordinatlarini ayir | DEVAM |
| MF-17 | [DISCOVERED] Her form tipi icin fiziksel form, ham cihaz matrisi ve yazilim alanlari arasinda kanonik aynalama modeli cikar | DEVAM |
| MF-18 | [DISCOVERED] Global kurallarla teknik-detaysiz, blok-bilgisi tabanli yeni form tipi tanimlama akisini kur | NOT_STARTED |

---

## 6) Talep Derleme Tablosu

| REQ-ID | Talep | Kapsam | Durum |
|---|---|---|---|
| REQ-01 | Hoca sinav katmanlarini onceden girsin | MVP | DEVAM |
| REQ-02 | Operator sinav ID ile okutma baslatsin | MVP | DEVAM |
| REQ-03 | Agirlikli puan ve kitapcik/grup bazli analizler olsun | MVP | DEVAM |
| REQ-04 | QR olmasin | MVP | TAMAMLANDI |
| REQ-05 | Yanlis repoda baslayan is bu koke tasinsin | Governance | TAMAMLANDI |
| REQ-06 | Guncel README hazirlansin ve repo GitHub'a yedeklensin | Governance | TAMAMLANDI |
| REQ-07 | Ayni arayuz masaustu ikonlu Windows uygulamasi olarak da acilsin | Distribution | DEVAM |
| REQ-08 | Masaustu dagitimi olurken gelecekte ogretmen-prep icin webe tasinabilir ayni UI/API kaynagi korunsun | Architecture | DEVAM |
| REQ-09 | SR-3500 donor kaniti SR-6000 ve ayni driver ailesi icin destek matrisine donusturulsun | Device | DEVAM |
| REQ-10 | Baslangic/yayginlasma fazinda sinava ait genel bilgiler ve kanonik soru metadata'si ogretmen yerine operator tarafinda minimum tikli guvenli akisla toplanabilsin | Operations | DEVAM |
| REQ-11 | Operator, birbirini bozmayan alternatif sinav hazirlama yontemleri arasindan ihtiyaca gore secim yapabilsin; sonraki adimlar secilen yonteme gore acilsin | Operations | DEVAM |
| REQ-12 | Akademisyenlere dagitilabilecek 500 satirlik Excel sinav tanim sablonu uretilsin; sistem yalniz dolu satir kadar soru kabul etsin | Operations | DEVAM |
| REQ-13 | Eksik kanonik metadata nedeniyle etkilenebilecek analiz kolonlari UI'da kirmizi baslik ve acik uyari notuyla isaretlensin | UX/Assessment | DEVAM |
| REQ-14 | Tam Excel tanimi sablonu ve sonuc ciktilari kurumsal gorunsun; rapor basligi universite kimligiyle baslasin | UX/Branding | TAMAMLANDI |
| REQ-15 | Ogrenci cevap matrisi exportta kanonik ve form pozisyonu gorunumleri alt alta verilsin, tum metin ciktilari ZIP olarak toplu indirilebilsin | Export | TAMAMLANDI |
| REQ-16 | Hazirlik butunlugu uyarilari raporda dogru Turkce, kurumsal warning alani ve UI ile tutarli kirmizi baslik vurgusuyla gosterilsin | UX/Assessment | TAMAMLANDI |
| REQ-17 | Kitapcik sirasi ve blok agirlik hazirlama yolunda toplu-yapistir butonlari aninda aktif olsun; agirlik formati operator dostu ve virgullu kusurat kabul eder hale gelsin | UX/Operations | TAMAMLANDI |
| REQ-18 | `Kitapcik sirasi + blok agirlik` yolunda manuel girilen sira/agırlik metadata'si optik cevap anahtari ve ogrenci okuma sonrasinda da kesin kabul edilip `inferred/defaulted` warning'lerine dusmesin | UX/Operations | TAMAMLANDI |
| REQ-19 | Ham cihaz matrisi beklenen cevap/kimlik bloklariyla guvenilir eslesmiyorsa sistem uydurma ogrenci/cevap uretmek yerine acik bloke ve operator mesaji vermeli | Optical Reliability | TAMAMLANDI |
| REQ-20 | BSR-KATIPCELEBI-SNF formunda orientation secimi, sinavdaki beklenen soru araligi ve forma-ozel kimlik/date koordinatlariyla puanlanmali; Q25/Q89 gibi alakasiz hayalet cevaplar gercek AYDEMIR sheet'ini bastirmamali | Optical Reliability | DEVAM |
| REQ-21 | Makine ham verisi, yazilim ve fiziki optik form aynalamasi her form tipi icin kanonik evidence modeliyle kurulmalı; tek forma ozel hotfix closure sayilmamali | Optical Reliability | DEVAM |
| REQ-22 | Makine dili cozuldukten sonra global kurallara bagli yeni form tipi tanimlama ozelligi gelistirilmeli; operator yalniz blok bilgileri girmeli, teknik koordinat/esik/orientasyon ayrintilari UI'ya sizmamalidir | UX/Operations | NOT_STARTED |

---

## 7) Gorev Takip Cizelgesi

| Faz | Adim | Aciklama | Durum | Ust ID | Ajan | Baslangic | Tamamlanma | Parity | Notlar |
|---|---|---|---|---|---|---|---|---|---|
| F1 | F1.1 | Donor kurallari oku ve dogru proje kokunu belirle | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | `Universal-Agent-OS/tr/AGENT_OS_RULES.md` ve donor sablon okundu |
| F1 | F1.2 | Proje kokunde governance dosyalari ve aktif master plani olustur | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | README, AGENTS, memory surfaces ve master plan acildi |
| F1 | F1.3 | [DISCOVERED] Yanlis repodaki task-ozel dosyalari temizle | TAMAMLANDI | REQ-05 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | OPRADOX tarafinda exam-platform'a ait task-ozel kod bulunmadi; unrelated degisikliklere dokunulmadi |
| F1 | F1.4 | Kullanicidan kalan Phase-0 kararlarini topla ve kilitle | TAMAMLANDI | MF-02 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | Ayni cihaz, CSV/Excel + vendor export, login'siz tek uygulama, TR-only karar kilidi alindi |
| F1 | F1.5 | [DISCOVERED] Desktop-web cekirdegi korunurken Windows masaustu dagitimi ve SR ailesi karar kapilarini plana kilitle | TAMAMLANDI | MF-02 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | Kullanici talebi dogrultusunda browser cekirdegi korunup operator icin Windows desktop shell/installer hattinin ayni planda yurumesi ve SR-6000 destek iddiasinin probe-gated olmasi yazili kilide alindi |
| F1 | F1.6 | [DISCOVERED] Startup rollout modelini operator-first prep ve no-silent-default analiz kuralıyla yazili kilitle | TAMAMLANDI | MF-09 | GitHub Copilot | 2026-04-14 | 2026-04-14 | OK | Baslangic/yayginlasma fazinda ogretmen erisimi acilmayacagi, genel sinav bilgileri ile kanonik metadata'nin operatorce girilecegi ve agirlik/sira alanlarinin sessiz varsayimla tamamlanamayacagi governance yuzeylerine islendi |
| F2 | F2.1 | Backend domain ve proje iskeletini kur | TAMAMLANDI | MF-03 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | FastAPI API, lokal JSON persist, import parser ve puanlama servisi kuruldu |
| F3 | F3.1 | Ogretmen ve operator arayuzunu ayni sayfada ac | TAMAMLANDI | MF-04 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | TR-only vanilla JS arayuzu teacher-prep, import ve analiz panelleriyle kuruldu |
| F4 | F4.1 | Test, smoke ve restore parity kosularini yap | DEVAM | MF-05 | GitHub Copilot | 2026-04-09 | - | OK | Paketlenmis son frontend source'a geri tasindi; `pytest backend/tests/test_exam_flow.py backend/tests/test_device_service.py backend/tests/test_optical_form_flow.py -q` -> `27 passed`; `/api/health` ve root smoke 2026-04-13'te tekrar dogrulandi |
| F4 | F4.2 | [DISCOVERED] Cok kitapcikli optik cevap anahtari okuma sayisini kitapcik/pending adetle sinirla | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.main` icinde device-answer-key path'i explicit limit yoksa toplam/pending kitapcik adedi kadar `max_sheets` uygular; `pytest backend/tests/test_optical_form_flow.py -k "defaults_max_sheets or mixed_booklets_in_single_pass or reads_multiple_booklets_in_single_pass" -q` -> `4 passed`; `pytest backend/tests/test_optical_form_flow.py -q` -> `20 passed` |
| F4 | F4.3 | [DISCOVERED] Canli operator kabul bosluklarini kapat: canli import, silme, export, decode alanlari ve detayli analiz | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | TODO | Kullanici canli testte `Okunanlari ice aktar` pasifligi, sinav silme eksigi, ogrenci no yon problemi, sinif/ad-soyad decode eksigi, sinav kodu/tarih gorunurlugu, lokal ayaga kaldirma ihtiyaci ve export RTL gorunumu raporladi |
| F4 | F4.6 | [DISCOVERED] Varsayilan optik kimlik alanlarini saha semantigi ve export bidi yonuyle hizala | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.optical_form_service` icinde varsayilan/katipcelebi/katipcelebi63 ad-soyad semantigi saha gozlemine gore swap edildi; sinif numarasi default yonu soldan-saga alindi; `backend.app.export_service` karma alanlara LTR mark ekledi; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `44 passed, 1 deselected`; lokal sunucu `http://127.0.0.1:8141` uzerinde `/api/health` -> `{"status":"ok"}` |
| F4 | F4.7 | [DISCOVERED] Export raporunu sadeleştir, sınav metadata alanlarını ekle ve sınıf yönünü UI/export katmanında kilitle | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.schemas` ve `backend.app.exam_service` sinav yili/donem/tur alanlariyla genisletildi; `frontend/index.html` + `frontend/js/app.js` teacher-prep metadata girdileri ve library/preview gosterimleriyle guncellendi; `backend.app.export_service` genel ozetten oturum/raw created_at satirlarini ve ogrenci onizleminden `Cevap ozeti` sutununu cikardi; UI ve export sinif/form kodu/form tarihi alanlari LTR mark ile kilitlendi; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `45 passed, 1 deselected`; lokal sunucu `.venv` uzerinden `http://127.0.0.1:8141` adresinde yeniden baslatildi ve `/api/health` -> `{"status":"ok"}` |
| F4 | F4.8 | [DISCOVERED] Optik sinav/anket kodu ve sinav tarihi alanlari icin fiziksel matris koordinatlarini teyit et | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | `.fmt` icinde tanimli bolge olmadigi icin `backend.app.optical_form_service` icine varsayilan/katipcelebi/katipcelebi63 ailesi icin sag panel sanal digit bolgeleri eklendi; `exam_code` ile `exam_date_day/month/year` decode edilip tarihte `GG.AA.YYYY` birlestiriliyor. `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `46 passed, 1 deselected`; ancak gercek form/cihaz matrisiyle son saha teyidi halen gerekli |
| F4 | F4.9 | [DISCOVERED] Kullanici kabulunde tekrar eden saha hatalarini ham cihaz matrisi ve gercek export artefaktiyla yeniden uretip kapat | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | `örnek/ÇOCUK HAS. VİZE DEVAM.txt` kullanicinin belirttigi artefakt olarak incelendi; dosya `[sheet_] front_marks` ham matrisi degil, sabit-genislik vendor exportu. Prefix kaniti parser'a tasinip `backend.app.import_service` icinde `classroom` ile baskin `exam_code` materyalize edildi; answer blob regex'i isim alanina tasmayacak sekilde duzeltildi. `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `48 passed`. Kalan tek acik nokta, bu export artefaktinin `exam_date` tasimadigi teyit edildigi icin tarih bilgisinin ancak farkli saha artefakti veya ust metadata kaynagiyla kapatilabilecek olmasidir |
| F4 | F4.10 | [DISCOVERED] `örnek/optik.pdf` saha formunu diklestirip orientasyon ve yardimci alan koordinatorlerini gercek raster kanitiyla kalibre et | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-14 | 2026-04-14 | OK | `probe-output/optik_page1_clockwise.png` kullanici saha teyidiyle birlikte yeniden yorumlandi; alt-sol fiziksel `sinav tarihi` (8 rakam) ve `sinav/anket kodu` (1 harf + 3 rakam) bloklarinin mevcut oldugu teyit edildi. `backend.app.optical_form_service` icindeki filtre kaldirilarak bu alanlar yeniden decode'a alindi; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `48 passed` |
| F4 | F4.13 | [DISCOVERED] Komsu siklarda sessiz yanlis optik secimi yerine muhafazakar ambiguity kilidi uygula | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-14 | 2026-04-14 | OK | `backend.app.optical_form_service` komsu siklar arasi yakin B/C benzeri near-tie durumlarini `adjacent_ambiguous` olarak bos + warning uretecek sekilde sertlestirildi; gevsetilmis esik adayi artik mevcut cevabi/booklet'i degistiremez, yalniz eksik cevap veya eksik kitapcik kazanimi saglarsa kabul edilir; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -q` -> `57 passed` |
| F4 | F4.14 | [DISCOVERED] Gercek SR matrisinde sinif blogunu 4 haneli numeric semantik olarak cozumle ve tek-zayif tarih hanesini muhafazakar fallback ile geri kazan | TAMAMLANDI | MF-10 | GitHub Copilot | 2026-04-14 | 2026-04-14 | OK | `backend.app.optical_form_service` varsayilan/katipcelebi/katipcelebi63 ailesinde C31-C34 sinif blogunu virtual 4-haneli numeric region olarak override edecek sekilde guncellendi; class_section fallback'i bu aile icin bloke edildi. Exam-date alanlarinda yalniz `day/month/year` bloklari icin soft-single recovery acildi. `pytest backend/tests -q` -> `67 passed`; ham `last-mark-read.txt` icindeki SIN ADAM sheet'i `class_number=0001`, `classroom=0001`, `exam_code=A001`, `exam_date=11.01.1990` uretti |
| F4 | F4.15 | [DISCOVERED] Kurumsal Excel sablonu, universite rapor basligi, cift-mod cevap matrisi ve toplu ZIP exportu ekle | TAMAMLANDI | MF-11 | GitHub Copilot | 2026-04-15 | 2026-04-15 | OK | `backend.app.definition_template_service` ile kurumsal ve dinamik Excel sablonu uretildi; `backend.app.export_service` universite ust basligi, kanonik+form pozisyonu matrix bloklari, ODS exportu ve ZIP paketini ekledi. Son hotfix ile ZIP paketine PDF de dahil edildi; canli smoke'ta arsiv icinde `.csv/.xlsx/.ods/.pdf/.txt/.json` dosyalari ve `%PDF` imzasi dogrulandi. `pytest backend/tests/test_exam_flow.py -q` -> `29 passed`; lokal `.venv` sunucusu `http://127.0.0.1:8140` uzerinde yeniden baslatildi |
| F4 | F4.16 | [DISCOVERED] Hazirlik butunlugu uyarilarini export katmaninda kurumsal Turkce ve UI-paritesiyle kilitle | TAMAMLANDI | MF-12 | GitHub Copilot | 2026-04-15 | 2026-04-15 | OK | `backend.app.exam_service` warning copy'leri Turkcelestirildi; `backend.app.export_service` icinde `Hazırlık Bütünlüğü Uyarıları` bolumu, affected-column mapping'i ve XLSX/ODS/PDF kirmizi warning stili eklendi. `backend/tests/test_exam_flow.py` warning metni ve header-fill regresyonuyla genisletildi; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -q` -> `65 passed`. Lokal `.venv` sunucusu `http://127.0.0.1:8140` uzerinde yeniden baslatildi ve `/api/health` -> `{"status":"ok"}` |
| F4 | F4.17 | [DISCOVERED] Kitapcik sirasi ve blok agirlik hizli-yapistir UX'ini aktif buton, sade format ve virgullu kusuratla duzelt | TAMAMLANDI | MF-13 | GitHub Copilot | 2026-04-15 | 2026-04-15 | OK | `frontend/index.html` ve `frontend/js/app.js` bulk-edit alaninda textarea input listener'lari eklenerek `Kitapçık sırasını uygula` ve `Ağırlık bloklarını uygula` butonlari aninda aktif hale getirildi; agirlik formatı `soru araligi = puan/agırlık` seviyesine sadeleştirildi, legacy `| grup | agirlik` parse'i geriye donuk korundu. Manual weight input'u `3,33` ve `3.33` kabul edecek sekilde metin+decimal parse zincirine alindi; `backend.app.import_service` Excel tanim agirliklarinda da ayni localized parse'i kabul ediyor. JS cache-bust `20260415b` ile yenilendi; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -q` -> `67 passed`; localhost root sayfasi yeni JS marker'i ve `/api/health` -> `{"status":"ok"}` smoke ile dogrulandi |
| F4 | F4.18 | [DISCOVERED] `paste-ranges` explicit metadata'sinin optik cevap anahtari sonrasi `inferred/defaulted` profile'a ezilmesini durdur | TAMAMLANDI | MF-14 | GitHub Copilot | 2026-04-15 | 2026-04-15 | OK | Ilk hotfix ile `backend.app.optical_form_service` optik cevap anahtari okurken mevcut profildeki explicit `canonical_mapping_source` ve `weight_source` alanlarini secici sekilde koruyacak hale getirildi; boylece `paste-ranges` ve benzeri metadata-first akislar answer layer'i optikten alsa bile provizyonel warning'e dusmuyor. Sonraki incelemede asil kopuklugun UI tarafinda `Kitapçık sırası + blok ağırlık` butonlarinin `prep_method_code` alanini otomatik `paste-ranges` yapmamasi oldugu bulundu; `frontend/js/app.js` bu iki aksiyonda prep method secimini artik zorunlu olarak `paste-ranges`a cekiyor ve `frontend/index.html` JS cache-bust `20260415c` ile yenilendi. Ayrica `backend.app.exam_service` ile `backend.app.optical_form_service`, gecmiste `manual` damgasi ile kaydedilmis ama acik `paste-ranges` izi tasiyan kayitlari (kitapcik pozisyon sapmasi / non-default agirlik-grup izi) dar heuristikle self-heal edecek sekilde guncellendi; stale `answer_key_profile` ve session `analysis_integrity` payload'lari canli okumada temizleniyor. `backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -q` -> `70 passed`; canli smoke'ta `/api/exams/MANUEL` ve son session `analysis_integrity` payload'i `status=ready`, `canonical_mapping_source=explicit`, `weight_source=explicit`, `warnings=[]` olarak dogrulandi |
| F4 | F4.19 | [DISCOVERED] Dusuk guvenli cihaz matrisi decode'unda blok-disi isaret baskinligina kalite kilidi koy | TAMAMLANDI | MF-15 | GitHub Copilot | 2026-04-15 | 2026-04-15 | OK | `backend.app.optical_form_service` icine blok-disi aday isaret baskinligini tespit eden kalite kilidi eklendi; `decode_exam_sheets` dusuk guvenli formu artik sessizce ogrenciye donusturmuyor, acik operator hatasi ile bloke ediyor. `backend/tests/test_optical_form_flow.py` icine gürültulu bordur matrisi regresyonu eklendi; `pytest backend/tests/test_optical_form_flow.py -q` -> `39 passed`, `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `71 passed` |
| F4 | F4.20 | [DISCOVERED] BSR formunda beklenen soru araligi disindaki cevaplari orientation skorunda cezalandir ve forma-ozel kimlik/date koordinatlarini ayir | DEVAM | MF-16 | GitHub Copilot | 2026-04-15 | - | PARTIAL | `backend.app.optical_form_service` artik `bsr-katipcelebi-snf` icin ayri coordinate source kullaniyor; orientation skorlayicisi yalniz sinavdaki beklenen booklet pozisyonlarini odullendirip Q25/Q89 gibi hayalet cevaplari sert cezalandiriyor. Grup tie-break'i calibrated default reverse yonunu tercih edecek sekilde duzeltildi; numeric named-field'lerde soft-single recovery yalniz ayni bolgede en az bir guclu isaret varsa acildi. `last-mark-read.txt` dogrulamasinda sheet-1 artik `flip_vertical`, `AYDEMİR ASLAN`, `0321`, `15.04.2026`, `4067865120` olarak cozuluyor; son TC hanesi halen ham matriste eksik/uyumsuz. Bu mikro-fazdaki kanit yalniz F7 genel aynalama fazina giris verisi sayilir; closure tum aktif form tiplerinde ayni evidence modeli cikmadan verilmeyecek. `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `76 passed` |
| F4 | F4.11 | [DISCOVERED] Operator-first kanonik metadata toplama akisinda secilebilir hazirlama yontemlerini ve cakismasiz merge kurallarini ekle | TAMAMLANDI | MF-09 | GitHub Copilot | 2026-04-14 | 2026-04-15 | OK | `Tam Excel`, `Excel metadata + optik`, `optik-only`, `kitapcik sirasi yapistirma + blok agirlik` ve `mevcut sinavdan hazir profil kopyala` yontemleri UI'da secilebilir hale getirildi; `prep_method_code` API/state'e tasindi; optik sentez explicit position katmanini ezmeden yalniz cevaplari tamamlayacak sekilde duzeltildi. Son hotfix ile yalniz `hybrid-excel-optical` yolunda definition-file kaynakli `canonical_mapping_source` ve `weight_source` alanlari optik cevap anahtari okunurken korunur hale getirildi; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -q` -> `64 passed` |
| F4 | F4.12 | [DISCOVERED] Akademisyen odakli 500 satirlik Excel sablonu ve provizyonel analiz gorunurlugunu ekle | TAMAMLANDI | MF-09 | GitHub Copilot | 2026-04-14 | 2026-04-14 | OK | `docs/akademisyen_sinav_tanim_sablonu_500.xlsx` Turkce basliklar ve kullanim sayfasiyla yeniden uretildi; Excel parser'i ilk sheet'e korlemesine bakmak yerine baslik skoruyla dogru `Sablon` sayfasini sececek sekilde duzeltildi; `definition-file` upload'u yalniz dolu satirlari soru sayacak, tek kitapcikla calisacak ve saga eklenen yeni `X_sira`/`X_cevap` kolonlarini kabul edecek sekilde genisletildi; tarayici tarafi dosya seciminde otomatik upload akisina gecirildi ve buton manuel retry rolune cekildi; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `55 passed` |
| F4 | F4.4 | [DISCOVERED] Ciktilari tam bloklu rapora cevir: kitapcik/grup/soru/ogrenci bloklari, soru-yanit matrisi, sinav geneli sirasi ve secilebilir net kurali | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | Session modeli agirlik-duyarli deterministic akademik yorum, birlestirilmis metodoloji tablosu ve soru bazli dagilimin altinda ayrica sik-cevap dagilim tablosu ile genisletildi; legacy session hydration artik bu yeni yorum/tablo alanlarini da geriye donuk dolduruyor; PDF export hucreleri sarilabilir paragraf + sayfaya olceklenen kolon genisligi ile yeniden kuruldu; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `42 passed, 1 deselected`; localhost `http://127.0.0.1:8141` uzerinde ayakta |
| F4 | F4.5 | [DISCOVERED] README'yi canli durumla hizala ve GitHub snapshot yedegi al | TAMAMLANDI | MF-06 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | Kok README guncel optik, raporlama, persist ve calistirma akislarini anlatacak sekilde yenilendi; workspace git ile baslatilip `https://github.com/zyganali-glitch/s-nav` reposuna `main` dali olarak pushlandi |
| F5 | F5.1 | Browser cekirdegi korunurken Windows masaustu launcher/installer kabul kriterlerini kilitle | DEVAM | MF-07 | GitHub Copilot | 2026-04-13 | - | OK | Masaustu dagitim browser UI'yi koruyan localhost shell olarak konumlandi; cift tikla acilis, tarayiciyi otomatik acma, dis veri klasoru, desktop kisayolu, uninstall ve offline kurulum acceptance seti plana eklendi |
| F5 | F5.2 | Launcher katmanini kur: health-check, otomatik browser acilisi, terminalsiz acilis ve harici state/log yolu | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Exe dogrudan uvicorn kosmak yerine operator dostu bir launcher ile localhost hazir olduktan sonra UI'yi acmali; state Program Files yerine yazilabilir klasore yonlenmeli |
| F5 | F5.3 | Windows installer/kisayol/icon/uninstall akislarini ekle | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Inno Setup veya esdegeri ile desktop icon, Start Menu girisi, kaldirma, runtime/config kopyalama ve tek-PC offline kurulum akisi uretilmeli |
| F5 | F5.4 | Temiz makinede bundle+installer smoke ve operator UX kabul turunu kos | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Kurulum, cift tik acilis, localhost UI yuklenmesi, veri kaliciligi ve uninstall sonrasi artik dosya davranisi dogrulanacak |
| F6 | F6.1 | Mevcut driver ve SDK uzerinden SR cihaz ailesi uyumluluk matrisini cikar | DEVAM | MF-08 | GitHub Copilot | 2026-04-13 | - | PARTIAL | Donor makinede aygit adi `SEKONIC OMR SR-3500/6000/6500 Device` olarak gorunuyor; ancak eldeki API wrapper `SkDvSr3500Img.dll` ve `SkDv_OpenSingle` ilk aygiti enumerasyonsuz aciyor. Bu nedenle ayni driver etiketi aile-geneli garanti sayilmiyor |
| F6 | F6.2 | Secure-PC veya SR-6000 bagli ortamda packaged runtime ile gercek cihaz smoke kos | NOT_STARTED | MF-08 | GitHub Copilot | 2026-04-13 | - | TODO | `/api/device/mark-read` ve ilgili probe scriptleri SR-6000 uzerinde bizzat denenmeden aile-geneli direct-read destegi ilan edilmeyecek |
| F6 | F6.3 | Family-wide destek stratejisini sec: ortak abstraction mi cihaz allowlist'i mi | NOT_STARTED | MF-08 | GitHub Copilot | 2026-04-13 | - | TODO | Probe sonuclarina gore SR-3500/6000/6500 ayni API davranisini veriyorsa ortak driver abstraction korunur; vermiyorsa model bazli capability/allowlist eklenir |
| F7 | F7.1 | Her aktif form tipinde fiziksel form, ham cihaz matrisi ve yazilim alanlari arasinda kanonik blok aynalama modelini cikar | DEVAM | MF-17 | GitHub Copilot | 2026-04-15 | - | PARTIAL | BSR/Katipcelebi uzerindeki son bulgular bu fazin seed evidence'i sayildi; kapanis icin her form tipinde ayni formatta fiziksel anotasyon + ham matrix + vendor/yazilim decode paketi gerekecek |
| F7 | F7.2 | Form ailesi bazli calibration/evidence artefaktlarini ve residual gap listesini standardize et | NOT_STARTED | MF-17 | GitHub Copilot | 2026-04-15 | - | TODO | Her form ailesi icin zorunlu artefakt seti: fiziksel form gorseli/anotasyonu, ham mark matrisi, vendor cikti varsa referans, decoder diagnostics ve bloke sebepleri |
| F7 | F7.3 | Makine dilinden operator diline ceviri yapan global blok kurallarini tasarla | NOT_STARTED | MF-18 | GitHub Copilot | 2026-04-15 | - | TODO | Satir/sutun/esik/orientasyon gibi teknik kavramlar operatora acilmayacak; sistem blok tipi, soru araligi, karakter sinifi, hane sayisi ve yon gibi semantik girdilerden teknik haritayi uretecek |
| F7 | F7.4 | Yeni form tipi tanimlama UI/API akisini yalniz blok bilgileriyle calisacak sekilde kur | NOT_STARTED | MF-18 | GitHub Copilot | 2026-04-15 | - | TODO | Operator yalniz blok adi, blok turu, soru kapsami, kitapcik/kimlik/tarih semantigi ve zorunlu alanlari girecek; teknik koordinat ve esikler arka planda derive edilecek |
| F7 | F7.5 | Siradan operator kabul turu ile teknik unsursuz yeni form tanimlama kolayligini dogrula | NOT_STARTED | MF-18 | GitHub Copilot | 2026-04-15 | - | TODO | Kullanicinin talep ettigi esik: en siradan operator bile yeni form tipini rahatlikla tanimlayabilmeli; kabul testi koordinat/threshold bilgisi kullanmadan tamamlanmali |

---

## 8) Gate Plani

| Gate | Durum | Kanit |
|---|---|---|
| Smoke Gate | PASS | `.venv` uzerinden `http://127.0.0.1:8140` yeniden ayaga kaldirildi; export-warning guncellemesi sonrasinda `/api/health` -> `{"status":"ok"}` |
| Binding Gate | PASS | `backend/tests/test_exam_flow.py` exam save + CSV import + vendor-style TXT import akisini dogruladi |
| Related-Tests Gate | PASS | `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -q` -> `76 passed` |
| Parity Gate | PASS | Backend API, static frontend ve lokal state ayni repo kokunden servis ediliyor; source ayrismasi yok |
| Desktop-Package Gate | NOT_RUN | Launcher, terminalsiz acilis, icon/kisayol ve installer smoke henuz implement edilmedi |
| Installer-UX Gate | NOT_RUN | Temiz makinede cift tik acilis, tarayici oto-acilis ve uninstall davranisi henuz kanitlanmadi |
| SR-Family Gate | DEVAM | Driver aygit adi `SR-3500/6000/6500` coklu aileyi isaret ediyor; fakat API wrapper ve probe kaniti su an yalniz SR-3500 donor zincirinde var, SR-6000 smoke bekleniyor |
| Canonical-Prep-Integrity Gate | DEVAM | Baslangic fazinda operatorce girilen kanonik soru agirligi ve kitapcik sirasi alanlari sessiz `weight=1` / `position=canonical_no` varsayimina dusmeden ya toplu kaynaktan materyalize edilmeli ya da akademik analiz provizyonel/blocked etiketine gecmeli |
| Method-Orchestration Gate | DEVAM | Backend ve test tarafinda yontem secimli orkestrasyon, Turkce/dinamik kitapcik kolonlu `definition-file` parse semantigi ve provizyonel analiz payload'i eklendi; hem `hybrid-excel-optical` hem explicit metadata tasiyan `paste-ranges` benzeri akislar optik cevap anahtari merge'inde source alanlarini koruyacak sekilde testle kilitlendi. Browser katmaninda manuel operator kabul turu henuz ayrica kosulmadi |
| Optical-Reliability Gate | DEVAM | Komsu siklarda sessiz yanlis secim yerine ambiguity warning + blank fallback kurali backend/test katmaninda eklendi. Son olarak `last-mark-read.txt` benzeri blok-disi aday isaret baskinliginda sahte `ogrenci/cevap` materializasyonunu bloke eden kalite kilidi ve regresyon testi eklendi. BSR yamasiyla beklenen soru araligi disindaki hayalet cevaplar orientation skorundan dusulup `bsr-katipcelebi-snf` icin ayri kimlik/date koordinatlari acildi; ham sheet-1 artik `flip_vertical`, `AYDEMİR ASLAN`, `0321`, `15.04.2026`, `4067865120` olarak geliyor. Ancak kullanici geri bildirimi uzerine bu tek-form sonuc closure sayilmiyor; gate kapanisi artik F7 altinda tum aktif form tiplerinde fiziksel form <-> ham matrix <-> yazilim alan aynalamasi kanitina baglandi |
| Form-Mirroring Gate | DEVAM | F7 kapanisi icin her aktif form tipinde fiziksel form anotasyonu, ham cihaz matrisi, vendor/yazilim cikti korelasyonu ve residual gap listesi ayni canonical evidence paketiyle eslesmeli; tek-form hotfix PASS sayilmayacak |
| Operator-Defined-Form Gate | NOT_RUN | Yeni form tipi UI'si operatora koordinat/esik/orientasyon gibi teknik kavram gostermeden yalniz blok bilgileriyle calisacak; siradan kullanici kabul turu kosulana kadar gate acik kalacak |
| No-UI-Regression Gate | DEVAM | Kod/test tarafinda export sadeleştirme, metadata alanlari, olusturma tarihi formatlama, sinif/form alanlari icin LTR gosterim, preparation-warning semantics'inin rapor katmanina kirmizi baslik paritesiyle tasinmasi ve `paste-ranges` bulk-edit buton/decimal UX kusurlari kilitlendi; buna ragmen kullanici kabulunde sinif yonu ile form kodu/tarihi sorunlari halen acik oldugu icin gate ancak gercek export artefakti ve ham cihaz matrisiyle kapatilacak |
| Export-Branding Gate | PASS | Dinamik kurumsal Excel sablonu, universite rapor basligi, kanonik+form pozisyonu export bloklari, `Hazırlık Bütünlüğü Uyarıları` warning alani ve CSV/XLSX/ODS/TXT/JSON ZIP paketi test + localhost smoke ile dogrulandi |
| Field-Calibration Gate | PASS | `örnek/optik.pdf` icin dogru insan-okur yon `90 derece saat yonu` olarak artefaktlastirildi; kullanici saha teyidiyle alt-sol fiziksel `sinav tarihi` ve `sinav/anket kodu` bloklari decoder'a yeniden baglandi. Son kalan capraz dogrulama ham `last-mark-read.txt` icindeki gercek SIN ADAM matrisiyle tamamlandi: `class_number=0001`, `classroom=0001`, `exam_code=A001`, `exam_date=11.01.1990` |
| I18N-Completeness Gate | PASS | Phase-0 TR-only kilidi dogrultusunda arayuz Turkceye cekildi; karisik dil etiketleri temizlendi |
| Integrity-Lock Gate | PASS | Header, faz, backlog, task, gate, risk ve handoff ayni editte implementasyon ve test kanitiyle guncellendi |
| Repo-Snapshot Gate | PASS | Workspace git ile baslatildi; README ve guncel kaynak snapshot'i `https://github.com/zyganali-glitch/s-nav` reposunda `main` dalina pushlandi |
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
| R-10 | GitHub hedef reposu bos degilse veya kimlik dogrulamasi yoksa snapshot push bloke olabilir | MITIGATED | Hedef repo bos/uygun durumda bulundu; yerel root commit ve sonraki parity commit'i `main` dalina basariyla pushlandi |
| R-11 | CSV/XLSX/TXT exportlarinda karma alfa-sayisal alanlar (sinif, form kodu, tarih) RTL gorunup operatorun alanlari ters saniyor olabilir | MITIGATED | Export katmaninda LTR mark uygulandi ve CSV/XLSX regresyon testi eklendi; son saha kabul turunda PDF/TXT gozlemiyle teyit et |
| R-12 | Teacher-prep metadata alanlari yoksa export genel ozetinde sinav baglami eksik kalir | MITIGATED | Sinav yili/donem/tur alanlari teacher-prep, API summary ve export genel ozetine eklendi; regresyon testi metadata satirlarini dogruluyor |
| R-13 | Optik kod/tarih bloklari hakkinda yanlis gorusel yorum decoderi gereksizce kapatabilir veya hatali kolonlara kaydirabilir | MITIGATED | Kullanici saha teyidi + raster artefakti birlikte esas alindi; decoder yeniden acildi ve regresyon testiyle kilitlendi. Kalan risk yalniz gercek cihaz matrisiyle son kolon/hane caprazi seviyesindedir |
| R-14 | Browser kaynak ile Windows masaustu kabugu farkli davranmaya baslarsa ileride webe tasima maliyeti artar | OPEN | Launcher/installer yalniz ayni frontend+API kaynagini host edecek; ayri UI fork'u acilmayacak |
| R-15 | Installer Program Files benzeri korumali dizine yazip state/log dosyalarini bozarsa operator veri kaybi veya sessiz hata gorur | OPEN | Launcher state/log/incoming klasorlerini yazilabilir dis klasore (or. `C:\SecureExam` veya kullanici-veri dizini) yonlendirecek; bundle exe dogrudan kalici veri yolu sayilmayacak |
| R-16 | Driver adi `SR-3500/6000/6500` ortak gorunse de DLL yuzeyi veya cihaz davranisi gercekte model farki tasiyabilir | OPEN | Aile-geneli destek yalniz gercek SR-6000 packaged smoke ve probe sonrasinda acilacak; gerekirse model bazli capability allowlist uygulanacak |
| R-17 | Sentetik optik test matrisi ile gercek SR cihaz cikisi farkliysa LTR/koordinat duzeltmeleri laboratuvarda yesil olup sahada yine kirmizi kalabilir | OPEN | Kalan kabul kriterleri yalniz ham cihaz matrisi, ayni forma ait export artefakti ve kullanicinin gordugu somut ters/yok okuma kanitlariyla kapatilacak; sentetik test tek basina yeterli sayilmayacak |
| R-18 | Decoder su anda yalniz `as_is` ve `flip_vertical` orientasyonlarini deniyor; yatik (90 derece) taranmis formda cevap bloklariyla yardimci alanlar yanlis pozitif uretebilir | MITIGATED | `örnek/optik.pdf` yalniz insan-okur kalibrasyon artefakti olarak kullanildi; bu saha kanitiyle desteklenmeyen sanal `exam_code` / `exam_date` decode'u kapatildi ve yardimci alanlarda zayif isaret tahmini durduruldu |
| R-19 | Operator akisi cevap anahtari ve puanlamaya izin verirken kanonik soru agirligi ile kitapcik permutasyonunu sessiz `1` ve `ayni sira` varsayarsa akademik yorum ve puan dagilimlari gecersizlesebilir | OPEN | Varsayim yerine explicit toplu kaynaklar (mapping CSV/XLSX, optik cevap anahtari, gelecekte toplu agirlik seti) one cekilecek; alanlar yoksa sistem analizi `provizyonel`/`eksik metadata` olarak bloke veya keskin warning ile etiketleyecek |
| R-20 | Bir hazirlama yontemi digerinin answers/positions/weights katmanini fark ettirmeden ezip operatoru yanlis guven duygusuna sokabilir | OPEN | Yontemler katman-bazli birlestirilecek: ayrintili Excel tam set overwrite, optik anahtar yalniz answer layer update, permutation paste yalniz position layer update, range agirlik yalniz weight/group update, profil ise tum set kopyalayip sonradan answer override'a izin verecek |
| R-21 | 500 satirlik akademisyen sablonunda bos kuyruq satirlar parser tarafinda zorunlu soru sanilirse kullanim kirilir | OPEN | Excel parser'i canonical satirlarda yalniz anlamli veri girilen satirlari isleyecek; sadece sablon dolgu satirlari sessizce atlanacak, kismi dolu ama eksik satirlar ise acik hata verecek; Turkce baslik alias'lari ile tek/ekstra kitapcik kolonlari da kabul edilecek |
| R-22 | Optik decoder komsu siklarda (ornegin C isaretliyken B hucresi de yuksek gelirse) sessizce en guclu hucreyi secip yanlis puan uretebilir | MITIGATED | Cevap decoder'i komsu siklar arasi near-tie durumunu ambiguity sayip bos + warning uretir; threshold fallback yalniz eksik cevap/kitapcik geri kazaniyorsa kabul edilir, mevcut cevabi mutate edemez |
| R-23 | Varsayilan/katipcelebi sinif blogu sahada 4 haneli numeric iken template C34'u ayri harf alanı sayarsa sinif `A001` gibi yanlis materyalize olur; exam-date yilinda tek kolon zayif mark da tarihi tamamen bos dusurebilir | MITIGATED | C31-C34 blogu explicit virtual 4-digit class region olarak override edildi; class_section fallback'i bloke edildi. Exam-date icin yalniz day/month/year alanlarinda soft-single recovery eklendi ve ham SR matrisi + `pytest backend/tests -q` ile sinirlandi |
| R-24 | Kurumsal rapor basligi ve ODS/ZIP exportu eklenirken mevcut CSV/XLSX/PDF ciktilari veya import-sablon endpointi kirilabilir | MITIGATED | Export formatlari `backend/tests/test_exam_flow.py` ile kilitlendi; template endpointi dinamik ama xlsx-uyumlu tutuldu, ZIP paketi deterministic adlarla yalniz istenen formatlari uretiyor |
| R-25 | UI'da kirmizi uyariyla gosterilen provizyonel analiz kolonlari export/PDF tarafinda normal gorunurse operator sahada farkli anlam okuyabilir | MITIGATED | `analysis_integrity.affected_columns` export katmanina tasinip XLSX/ODS/PDF header stilleri ve kurumsal warning bolumu ayni semantics uzerinden uretildi; regresyon testi kirmizi fill + Turkce warning metnini dogruluyor |
| R-26 | `paste-ranges` hazirlama yolunda buton state'i textarea input'larina bagli degilse operator metin girdikten sonra butonlari olu sanip akisi kirik kabul eder; ayrica agirlik parse'i `3,33` gibi saha aliskanligini reddederse yanlis format desteği algisi olusur | MITIGATED | Textarea input listener, sade parser, localized decimal normalizasyonu ve JS cache-bust ayni yama icinde eklendi; backend regression testleri comma-decimal Excel agirligini de dogruluyor |
| R-27 | `paste-ranges` veya benzeri explicit metadata akislari optik cevap anahtari sonrasi profil kaynak alanlarini kaybederse sistem puanlamayi dogru yapsa bile operatora provizyonelmis gibi warning gosterip guven zincirini bozar | MITIGATED | `apply_optical_answer_key` explicit `canonical_mapping_source` ve `weight_source` alanlarini, answer layer optikten gelse bile koruyacak sekilde guncellendi; `paste-ranges -> device-answer-key -> device-import` regresyonu warning yoklugunu ve agirlikli skorun korunmasini dogruluyor |
| R-28 | Ham cihaz matrisi beklenen cevap/kimlik bloklariyla guvenilir eslesmediginde mevcut skor fonksiyonu yine de bir template/orientasyon secip sahte ogrenci/cevap materialize edebilir | MITIGATED | `outside_candidate_mark_count` ve benzeri diagnostics alanlari import oncesi kalite kilidine baglandi; guvenilmez form artik acik warning/error ile bloke edilip operator yeniden okutmaya yonlendiriliyor |
| R-29 | Orientation skorlayicisi sinavin beklenen soru araligi disindaki cevaplari pozitif sayarsa BSR gibi saha formlarinda gercek kimlik/date alanlari dogru orientation'da cozulsa bile `as_is` adayi Q25/Q89 hayalet cevaplariyla kazanabilir | MITIGATED | Skor fonksiyonu artik booklet bazli beklenen pozisyonlar disindaki cevaplari sert cezalandiriyor; BSR formu icin explicit coordinate source ve regresyon testleri eklendi |
| R-30 | AYDEMIR sheet'inde TC kimlik numarasinin son hanesi ham SR matrisinde vendor yazilimindaki kadar net materyalize olmuyor; mevcut decoder `4067865120`a kadar guvenli geliyor ama son haneyi sessiz uydurmuyor | OPEN | Son hane icin fiziksel matris izini veya vendor cikti korelasyonunu F7 canonical aynalama paketi icinde kanitla; sessiz tahmin yerine eksik haneyi acik residual gap olarak koru |
| R-31 | Tek-form hotfixler tum form ailelerine genellenmezse her yeni form tipinde ayni tersine muhendislik maliyeti tekrar eder ve decoder davranisi parcali kalir | OPEN | F7 ile her form tipini ayni fiziksel form <-> ham matrix <-> yazilim alan modeliyle dokumante et; form ailesi bazli evidence seti cikmadan closure verme |
| R-32 | Yeni form tipi tanimlama ozelligi operatora satir/sutun/esik/orientasyon gibi teknik detay sizdirirsa hedeflenen siradan kullanici akisi kirilir ve konfigurasyon hatalari artar | OPEN | Global blok kurallari uretici katmanda tutulacak; UI yalniz blok adi, blok turu, soru araligi, karakter sinifi, hane sayisi ve semantik yon bilgilerini gosterecek; preview ve validation zorunlu olacak |

---

## 10) Handoff

- Son tamamlanan mikro-adim: `Master plan icine F7 ayri faz olarak eklendi: her form tipi icin fiziksel form <-> ham cihaz matrisi <-> yazilim alan aynalamasi ve bunun uzerine teknik-detaysiz yeni form tipi tanimlama hattinin governance kilidi yazildi. Mevcut BSR/Katipcelebi bulgulari F7 icin yalniz seed evidence sayiliyor; birlesik regresyon suiti son kanitta `76 passed`.`
- Sonraki mikro-adim: `F7.1 kapsaminda aktif form tiplerini envanterle; her biri icin fiziksel form anotasyonu, ham mark matrisi, vendor cikti varsa referansi ve decoder alanlarini ayni evidence paketinde esle.`
- Acik risk/bloke: `Kullanici geri bildirimi geregi BSR uzerindeki tek-form iyilesme artik cozuldu kabul edilmiyor; tum form tiplerinde tekrar edilebilir aynalama modeli ve residual gap listesi henuz yok.`
- Degisen dosyalar: `plans/PLAN_20260409_exam_reading_platform_master.md`
- Gate durumu: `Smoke PASS, Binding PASS, Related-Tests PASS, Parity PASS, Desktop-Package NOT_RUN, Installer-UX NOT_RUN, SR-Family DEVAM, Canonical-Prep-Integrity Gate DEVAM, Method-Orchestration Gate DEVAM, Optical-Reliability Gate DEVAM, Form-Mirroring Gate DEVAM, Operator-Defined-Form Gate NOT_RUN, Export-Branding Gate PASS, Field-Calibration PASS, I18N PASS, No-UI-Regression DEVAM, Repo-Snapshot PASS, Release/NFR DEVAM.`
- Checkpoint: `Bu is artik F4 altinda izole bir decode hotfix'i degil; F7 capraz-form aynalama ve sonrasinda teknik olmayan yeni form tipi tanimlama programi olarak izlenecek.`

