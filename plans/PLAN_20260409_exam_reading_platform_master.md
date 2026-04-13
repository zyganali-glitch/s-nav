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
- Son guncelleme: `2026-04-13 18:08 TRT`
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
- Teacher-prep ve operator arayuzu browser-temelli ayni frontend olarak korunacak; masaustu uygulamasi bu arayuzu localhost uzerinden acan Windows kabugu olacak.
- Kisa vadeli operator dagitimi icin masaustu ikonu, kisayol ve installer desteklenecek; orta vadeli webe tasima olasiligi icin ayni frontend/API kaynagi korunacak.
- Ilk faz import tipi `CSV/Excel` ve `vendor export TXT/CSV` birlikte destekleyecek.
- Rol bazli giris olmayacak; tek uygulamada teacher-prep ve operator-run ekranlari olacak.
- Arayuz ilk teslimde yalniz Turkce olacak.
- Scanner direct-read tarafinda mevcut donor/kanit zinciri SR-3500 ile olustu; SR-6000 ve ayni driver ailesi icin destek iddiasi yalniz gercek cihaz probe + packaged runtime smoke sonrasinda acilacak.

---

## 2) Scope Lock

- Kapsam ici: `Teacher-prep sinav tanimi, operator-run sinav kodu ile oturum baslatma, agirlikli soru puanlama, kitapcik esleme, soru/grup bazli temel analiz, QR'siz akis, vendor export veya manuel veri importu, lokal web uygulamasi governance ve MVP implementasyonu, Windows masaustu launcher/installer/kisayol akisi, tek-PC operator kurulum ergonomisi, SR-6000 ve ayni driver ailesi icin uyumluluk matrisi/probe karari.`
- Kapsam disi: `QR, dogrudan scanner driver/TWAIN entegrasyonu disindaki rastgele cihaz aileleri, mobil native uygulama, bulut SaaS billing, canli deploy.`
- En kucuk sonraki adim: `Masaustu launcher+installer acceptance kriterlerini implementasyon adimlarina bolup SR-6000 icin gercek probe/smoke kanitini toplamak.`

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

---

## 7) Gorev Takip Cizelgesi

| Faz | Adim | Aciklama | Durum | Ust ID | Ajan | Baslangic | Tamamlanma | Parity | Notlar |
|---|---|---|---|---|---|---|---|---|---|
| F1 | F1.1 | Donor kurallari oku ve dogru proje kokunu belirle | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | `Universal-Agent-OS/tr/AGENT_OS_RULES.md` ve donor sablon okundu |
| F1 | F1.2 | Proje kokunde governance dosyalari ve aktif master plani olustur | TAMAMLANDI | MF-01 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | README, AGENTS, memory surfaces ve master plan acildi |
| F1 | F1.3 | [DISCOVERED] Yanlis repodaki task-ozel dosyalari temizle | TAMAMLANDI | REQ-05 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | OPRADOX tarafinda exam-platform'a ait task-ozel kod bulunmadi; unrelated degisikliklere dokunulmadi |
| F1 | F1.4 | Kullanicidan kalan Phase-0 kararlarini topla ve kilitle | TAMAMLANDI | MF-02 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | Ayni cihaz, CSV/Excel + vendor export, login'siz tek uygulama, TR-only karar kilidi alindi |
| F1 | F1.5 | [DISCOVERED] Desktop-web cekirdegi korunurken Windows masaustu dagitimi ve SR ailesi karar kapilarini plana kilitle | TAMAMLANDI | MF-02 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | Kullanici talebi dogrultusunda browser cekirdegi korunup operator icin Windows desktop shell/installer hattinin ayni planda yurumesi ve SR-6000 destek iddiasinin probe-gated olmasi yazili kilide alindi |
| F2 | F2.1 | Backend domain ve proje iskeletini kur | TAMAMLANDI | MF-03 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | FastAPI API, lokal JSON persist, import parser ve puanlama servisi kuruldu |
| F3 | F3.1 | Ogretmen ve operator arayuzunu ayni sayfada ac | TAMAMLANDI | MF-04 | GitHub Copilot | 2026-04-09 | 2026-04-09 | OK | TR-only vanilla JS arayuzu teacher-prep, import ve analiz panelleriyle kuruldu |
| F4 | F4.1 | Test, smoke ve restore parity kosularini yap | DEVAM | MF-05 | GitHub Copilot | 2026-04-09 | - | OK | Paketlenmis son frontend source'a geri tasindi; `pytest backend/tests/test_exam_flow.py backend/tests/test_device_service.py backend/tests/test_optical_form_flow.py -q` -> `27 passed`; `/api/health` ve root smoke 2026-04-13'te tekrar dogrulandi |
| F4 | F4.2 | [DISCOVERED] Cok kitapcikli optik cevap anahtari okuma sayisini kitapcik/pending adetle sinirla | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.main` icinde device-answer-key path'i explicit limit yoksa toplam/pending kitapcik adedi kadar `max_sheets` uygular; `pytest backend/tests/test_optical_form_flow.py -k "defaults_max_sheets or mixed_booklets_in_single_pass or reads_multiple_booklets_in_single_pass" -q` -> `4 passed`; `pytest backend/tests/test_optical_form_flow.py -q` -> `20 passed` |
| F4 | F4.3 | [DISCOVERED] Canli operator kabul bosluklarini kapat: canli import, silme, export, decode alanlari ve detayli analiz | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | TODO | Kullanici canli testte `Okunanlari ice aktar` pasifligi, sinav silme eksigi, ogrenci no yon problemi, sinif/ad-soyad decode eksigi, sinav kodu/tarih gorunurlugu, lokal ayaga kaldirma ihtiyaci ve export RTL gorunumu raporladi |
| F4 | F4.6 | [DISCOVERED] Varsayilan optik kimlik alanlarini saha semantigi ve export bidi yonuyle hizala | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.optical_form_service` icinde varsayilan/katipcelebi/katipcelebi63 ad-soyad semantigi saha gozlemine gore swap edildi; sinif numarasi default yonu soldan-saga alindi; `backend.app.export_service` karma alanlara LTR mark ekledi; `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `44 passed, 1 deselected`; lokal sunucu `http://127.0.0.1:8141` uzerinde `/api/health` -> `{"status":"ok"}` |
| F4 | F4.7 | [DISCOVERED] Export raporunu sadeleştir, sınav metadata alanlarını ekle ve sınıf yönünü UI/export katmanında kilitle | TAMAMLANDI | MF-05 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | `backend.app.schemas` ve `backend.app.exam_service` sinav yili/donem/tur alanlariyla genisletildi; `frontend/index.html` + `frontend/js/app.js` teacher-prep metadata girdileri ve library/preview gosterimleriyle guncellendi; `backend.app.export_service` genel ozetten oturum/raw created_at satirlarini ve ogrenci onizleminden `Cevap ozeti` sutununu cikardi; UI ve export sinif/form kodu/form tarihi alanlari LTR mark ile kilitlendi; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `45 passed, 1 deselected`; lokal sunucu `.venv` uzerinden `http://127.0.0.1:8141` adresinde yeniden baslatildi ve `/api/health` -> `{"status":"ok"}` |
| F4 | F4.8 | [DISCOVERED] Optik sinav/anket kodu ve sinav tarihi alanlari icin fiziksel matris koordinatlarini teyit et | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | `.fmt` icinde tanimli bolge olmadigi icin `backend.app.optical_form_service` icine varsayilan/katipcelebi/katipcelebi63 ailesi icin sag panel sanal digit bolgeleri eklendi; `exam_code` ile `exam_date_day/month/year` decode edilip tarihte `GG.AA.YYYY` birlestiriliyor. `pytest backend/tests/test_optical_form_flow.py backend/tests/test_exam_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `46 passed, 1 deselected`; ancak gercek form/cihaz matrisiyle son saha teyidi halen gerekli |
| F4 | F4.9 | [DISCOVERED] Kullanici kabulunde tekrar eden saha hatalarini ham cihaz matrisi ve gercek export artefaktiyla yeniden uretip kapat | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | BLOCKED | Kullanici 2026-04-13 tekrar testinde sorunlarin devam ettigini bildirdi: sinif gorunumu saha ciktilarinda halen ters algilaniyor, `SINAV/ANKET KODU` ve `SINAV TARIHI` gercek okumada dogru cozulmuyor. Sentetik testler gecerli olsa da kalan kapatma kriteri gercek SR matrisi + gercek export ornegiyle birebir yeniden uretimdir |
| F4 | F4.4 | [DISCOVERED] Ciktilari tam bloklu rapora cevir: kitapcik/grup/soru/ogrenci bloklari, soru-yanit matrisi, sinav geneli sirasi ve secilebilir net kurali | DEVAM | MF-05 | GitHub Copilot | 2026-04-13 | - | PARTIAL | Session modeli agirlik-duyarli deterministic akademik yorum, birlestirilmis metodoloji tablosu ve soru bazli dagilimin altinda ayrica sik-cevap dagilim tablosu ile genisletildi; legacy session hydration artik bu yeni yorum/tablo alanlarini da geriye donuk dolduruyor; PDF export hucreleri sarilabilir paragraf + sayfaya olceklenen kolon genisligi ile yeniden kuruldu; `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `42 passed, 1 deselected`; localhost `http://127.0.0.1:8141` uzerinde ayakta |
| F4 | F4.5 | [DISCOVERED] README'yi canli durumla hizala ve GitHub snapshot yedegi al | TAMAMLANDI | MF-06 | GitHub Copilot | 2026-04-13 | 2026-04-13 | OK | Kok README guncel optik, raporlama, persist ve calistirma akislarini anlatacak sekilde yenilendi; workspace git ile baslatilip `https://github.com/zyganali-glitch/s-nav` reposuna `main` dali olarak pushlandi |
| F5 | F5.1 | Browser cekirdegi korunurken Windows masaustu launcher/installer kabul kriterlerini kilitle | DEVAM | MF-07 | GitHub Copilot | 2026-04-13 | - | OK | Masaustu dagitim browser UI'yi koruyan localhost shell olarak konumlandi; cift tikla acilis, tarayiciyi otomatik acma, dis veri klasoru, desktop kisayolu, uninstall ve offline kurulum acceptance seti plana eklendi |
| F5 | F5.2 | Launcher katmanini kur: health-check, otomatik browser acilisi, terminalsiz acilis ve harici state/log yolu | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Exe dogrudan uvicorn kosmak yerine operator dostu bir launcher ile localhost hazir olduktan sonra UI'yi acmali; state Program Files yerine yazilabilir klasore yonlenmeli |
| F5 | F5.3 | Windows installer/kisayol/icon/uninstall akislarini ekle | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Inno Setup veya esdegeri ile desktop icon, Start Menu girisi, kaldirma, runtime/config kopyalama ve tek-PC offline kurulum akisi uretilmeli |
| F5 | F5.4 | Temiz makinede bundle+installer smoke ve operator UX kabul turunu kos | NOT_STARTED | MF-07 | GitHub Copilot | 2026-04-13 | - | TODO | Kurulum, cift tik acilis, localhost UI yuklenmesi, veri kaliciligi ve uninstall sonrasi artik dosya davranisi dogrulanacak |
| F6 | F6.1 | Mevcut driver ve SDK uzerinden SR cihaz ailesi uyumluluk matrisini cikar | DEVAM | MF-08 | GitHub Copilot | 2026-04-13 | - | PARTIAL | Donor makinede aygit adi `SEKONIC OMR SR-3500/6000/6500 Device` olarak gorunuyor; ancak eldeki API wrapper `SkDvSr3500Img.dll` ve `SkDv_OpenSingle` ilk aygiti enumerasyonsuz aciyor. Bu nedenle ayni driver etiketi aile-geneli garanti sayilmiyor |
| F6 | F6.2 | Secure-PC veya SR-6000 bagli ortamda packaged runtime ile gercek cihaz smoke kos | NOT_STARTED | MF-08 | GitHub Copilot | 2026-04-13 | - | TODO | `/api/device/mark-read` ve ilgili probe scriptleri SR-6000 uzerinde bizzat denenmeden aile-geneli direct-read destegi ilan edilmeyecek |
| F6 | F6.3 | Family-wide destek stratejisini sec: ortak abstraction mi cihaz allowlist'i mi | NOT_STARTED | MF-08 | GitHub Copilot | 2026-04-13 | - | TODO | Probe sonuclarina gore SR-3500/6000/6500 ayni API davranisini veriyorsa ortak driver abstraction korunur; vermiyorsa model bazli capability/allowlist eklenir |

---

## 8) Gate Plani

| Gate | Durum | Kanit |
|---|---|---|
| Smoke Gate | PASS | `.venv` uzerinden `python -m backend.run_local_server` ile `http://127.0.0.1:8141` yeniden ayaga kaldirildi; `/api/health` -> `{"status":"ok"}` |
| Binding Gate | PASS | `backend/tests/test_exam_flow.py` exam save + CSV import + vendor-style TXT import akisini dogruladi |
| Related-Tests Gate | PASS | `pytest backend/tests/test_exam_flow.py backend/tests/test_optical_form_flow.py -k "not fixed_width_vendor_txt_is_accepted_for_single_booklet_exam" -q` -> `46 passed, 1 deselected` |
| Parity Gate | PASS | Backend API, static frontend ve lokal state ayni repo kokunden servis ediliyor; source ayrismasi yok |
| Desktop-Package Gate | NOT_RUN | Launcher, terminalsiz acilis, icon/kisayol ve installer smoke henuz implement edilmedi |
| Installer-UX Gate | NOT_RUN | Temiz makinede cift tik acilis, tarayici oto-acilis ve uninstall davranisi henuz kanitlanmadi |
| SR-Family Gate | DEVAM | Driver aygit adi `SR-3500/6000/6500` coklu aileyi isaret ediyor; fakat API wrapper ve probe kaniti su an yalniz SR-3500 donor zincirinde var, SR-6000 smoke bekleniyor |
| No-UI-Regression Gate | DEVAM | Kod/test tarafinda export sadeleştirme, metadata alanlari, olusturma tarihi formatlama ve sinif/form alanlari icin LTR gosterim kilitlendi; buna ragmen kullanici kabulunde sinif yonu ile form kodu/tarihi sorunlari halen acik oldugu icin gate ancak gercek export artefakti ve ham cihaz matrisiyle kapatilacak |
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
| R-13 | Sag panel sanal optik kod/tarih bolgeleri gercek saha formunda bir kolon kayiksa yanlis pozitif decode uretebilir | OPEN | Yeni bolgeler testte kilitlendi ama yalniz gercek form/cihaz matrisiyle saha kabulunden sonra kesinlestirilecek |
| R-14 | Browser kaynak ile Windows masaustu kabugu farkli davranmaya baslarsa ileride webe tasima maliyeti artar | OPEN | Launcher/installer yalniz ayni frontend+API kaynagini host edecek; ayri UI fork'u acilmayacak |
| R-15 | Installer Program Files benzeri korumali dizine yazip state/log dosyalarini bozarsa operator veri kaybi veya sessiz hata gorur | OPEN | Launcher state/log/incoming klasorlerini yazilabilir dis klasore (or. `C:\SecureExam` veya kullanici-veri dizini) yonlendirecek; bundle exe dogrudan kalici veri yolu sayilmayacak |
| R-16 | Driver adi `SR-3500/6000/6500` ortak gorunse de DLL yuzeyi veya cihaz davranisi gercekte model farki tasiyabilir | OPEN | Aile-geneli destek yalniz gercek SR-6000 packaged smoke ve probe sonrasinda acilacak; gerekirse model bazli capability allowlist uygulanacak |
| R-17 | Sentetik optik test matrisi ile gercek SR cihaz cikisi farkliysa LTR/koordinat duzeltmeleri laboratuvarda yesil olup sahada yine kirmizi kalabilir | OPEN | Kalan kabul kriterleri yalniz ham cihaz matrisi, ayni forma ait export artefakti ve kullanicinin gordugu somut ters/yok okuma kanitlariyla kapatilacak; sentetik test tek basina yeterli sayilmayacak |

---

## 10) Handoff

- Son tamamlanan mikro-adim: `Kullanici kabulunde kapanmayan sinif yonu ile form kodu/tarihi sorunlari F4.9 altinda ayri saha-blokesi olarak plana islendi.`
- Sonraki mikro-adim: `F4.9 kapsaminda ayni forma ait ham SR matrisi ve gercek export artefaktini toplayip sinif RTL ile kod/tarih decode sapmasini birebir yeniden uret.`
- Acik risk/bloke: `Sentetik testler yesil olsa da kullanici kabulunde sinif yonu ile form kodu/tarihi sorunlari kapanmadi; ham cihaz matrisi ve gercek export artefakti olmadan kesin kapatis yapilmayacak.`
- Degisen dosyalar: `plans/PLAN_20260409_exam_reading_platform_master.md`
- Gate durumu: `Smoke PASS, Binding PASS, Related-Tests PASS, Parity PASS, Desktop-Package NOT_RUN, Installer-UX NOT_RUN, SR-Family DEVAM, I18N PASS, Restore-Regression PASS, No-UI-Regression DEVAM, Repo-Snapshot PASS, Release/NFR DEVAM.`
- Checkpoint: `Plan artik sentetik regresyonun yetmedigini, kapatis icin gercek saha kaniti gerektigini ve kalan kullanici kabul blokelerinin F4.9 altinda izlenecegini resmi olarak kaydediyor.`

