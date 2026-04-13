# Sinav Okuma Platformu

Sinav Okuma Platformu, ogretmenin sinavi ve cevap anahtarini onceden tanimladigi; operatorun ise ayni cihazda import, optik okuma ve raporlama akislarini yonettigi lokal-oncelikli bir sinav degerlendirme uygulamasidir.

Mevcut surum, yalnizca temel MVP iskeleti degil; canli operator kabulunden gelen sorunlar uzerinden sertlestirilmis, optik toleranslari artirilmis ve ayrintili rapor uretebilen guncel calisir snapshot'tir.

## Neler Var

- Teacher-prep akisi: sinav, kitapcik, soru grubu, soru agirligi ve cevap anahtari tanimlama
- Operator-run akisi: sinav secip import, optik cevap anahtari okutma, tepsi okuma ve puanlama
- Lokal persist: tum sinavlar ve oturumlar `backend/data/app_state.json` icinde saklanir
- Cok kitapcikli puanlama: kitapcik bazli soru esleme, cevap anahtari eslestirme ve toplamlar
- Secilebilir net kurali: net hesaplari oturum aninda kilitlenir ve tum raporlara ayni sekilde yansir
- Gelismis raporlama: ogrenci, soru, grup, kitapcik ve sinav geneli analizleri
- Coklu export: CSV, TXT, XLSX, PDF ve JSON
- Legacy session hydration: eski kaydedilmis oturumlar yeni rapor kolonlariyla geriye donuk zenginlestirilir
- Optik sertlestirme: Turkish karakter koruma, saga-sola kodlanan ad alanlari, satir kaymasi toleransi, soluk isaret hassasiyeti
- SR-3500 odakli operator yardimcilari: HID capture, probe ve secure-PC bridge scriptleri

## Guncel Operator Yetkinlikleri

### Cevap anahtari ve import

- Sinav taslak olarak sorusuz kaydedilebilir.
- Cevap anahtari daha sonra toplu dosya ile yuklenip soru yapisi otomatik kurulabilir.
- Desteklenen cevap anahtari formatlari:
	- Detayli mapping: `canonical_no, group_label, weight, A_position, A_answer, B_position, B_answer...`
	- Sirali tablo: `booklet_code, Q1, Q2...` veya `booklet_code, answer_key`
	- Tek kitapcikli header'siz sabit-genislik TXT
- Cevap anahtari yoksa puanlama bloke edilir; sistem sessizce anlamsiz sonuc uretmez.

### Optik okuma

- Operator panelinde iki ana cihaz akisi vardir:
	- `Cevap anahtarini okut`
	- `Tepsiyi oku ve puanla`
- `.fmt` form yerlesimi secimi aktif olarak kullanilir ve gerekirse oturum bazli override uygulanir.
- Named-field decode tarafinda su iyilestirmeler vardir:
	- ogrenci no, sinif/sube, ad ve soyad alanlari
	- Turkish karakterlerin korunmasi
	- ters yonlu ad kodlamasi icin aday denemesi
	- bir satir asagidan baslayan kodlamaya tolerans
	- zayif ama tekil isaretleri bos saymayan kontrollu esik

### Raporlama ve analiz

- Sinav ozetleri: ortalama puan, net, dogru, yanlis, bos, alfa, standart sapma
- Kitapcik ozetleri: toplam ve ortalama puan/net/dogru/yanlis/bos
- Grup ozetleri: soru grubu bazli toplam ve ortalama performans
- Soru analizleri:
	- gucluk indeksi
	- ayirt edicilik indeksi
	- point-biserial korelasyon
	- varyans ve standart sapma
	- ust-alt grup dogruluk oranlari
	- bos birakma orani
- Ogrenci tablolari:
	- puan, yuzde, net, sira, sinif sirasi, kitapcik, kimlik alanlari
	- soru bazli isaret matrisi
- Akademik yorumlar:
	- deterministic uretilir
	- soru agirliklarini dikkate alir
	- metodoloji aciklamalariyla birlikte export edilir
- Yeni ayrintili tablo:
	- `Sorulara Siklara Gore Verilen Cevaplarin Dagilimi`
	- her soru icin A/B/C/D/E ve bos oranlarini ayrica verir

## Mimari Ozet

- Backend API: `backend/app/main.py`
- Sinav normalization ve puanlama: `backend/app/exam_service.py`
- Export uretimi: `backend/app/export_service.py`
- Import ayristirma: `backend/app/import_service.py`
- Optik decode: `backend/app/optical_form_service.py`
- Lokal persist: `backend/app/storage.py`
- Frontend: `frontend/index.html`, `frontend/js/app.js`, `frontend/css/app.css`
- Yerel baslatma: `backend/run_local_server.py`
- Operasyon scriptleri: `ops/`
- Form sablonlari: `optik_kagit_formatlari/`

## Kurulum

### Gereksinimler

- Windows ortam
- Python 3.11+
- `pip`

### Ilk kurulum

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Uygulamayi baslatma

Varsayilan calistirma:

```powershell
.\.venv\Scripts\Activate.ps1
python -m backend.run_local_server
```

Varsayilan host/port:

- Host: `127.0.0.1`
- Port: `8140`

Port doluysa farkli portla baslatma:

```powershell
$env:SINAV_OKUMA_HOST='127.0.0.1'
$env:SINAV_OKUMA_PORT='8141'
python -m backend.run_local_server
```

Ardindan tarayicida ilgili adresi ac:

- `http://127.0.0.1:8140`
- veya override edildi ise `http://127.0.0.1:8141`

### Kalicilik

- Kod degisiklikleri proje dosyalarina yazildigi icin PC kapanip acilinca kaybolmaz.
- Sinav ve oturum verileri `backend/data/app_state.json` icinde tutulur; dosya silinmedigi veya ustune yazilmadigi surece korunur.
- Calisan sunucu prosesi reboot sonrasi otomatik geri gelmez; uygulamayi yeniden baslatmak gerekir.

## Test

Hizli regresyon:

```powershell
pytest backend/tests/test_exam_flow.py backend/tests/test_device_service.py -q
```

Genis regresyon:

```powershell
pytest backend/tests/test_exam_flow.py backend/tests/test_device_service.py backend/tests/test_optical_form_flow.py -q
```

Raporlama ve optik sertlestirme odakli son kosularda ilgili slice'lar yesil durumdadir.

## Import ve Export Notlari

### Desteklenen import kolonlari

- Kimlik: `student_id`, `ogrenci_no`, `student`, `id`, `numara`
- Kitapcik: `booklet_code`, `booklet`, `kitapcik`, `grup`, `group`
- Sorular: `Q1...Qn`, `S1...Sn`, `Soru1...SoruN`

### Export formatlari

- CSV
- TXT
- XLSX
- PDF
- JSON

PDF export tarafinda genis tablolar icin satir sarma ve sayfa genisligine gore kolon olcekleme uygulanir.

## Secure-PC ve Operasyon Scriptleri

- `ops/watch_vendor_export.ps1`
	- vendor export klasorunu izler ve yeni dosyalari API'ye yollar
- `ops/probe_secure_pc_reader.ps1`
	- secure-PC uzerinde read-only cihaz/probe toplar
- `ops/setup_blank_machine.ps1`
	- bos makine icin klasor/config iskeleti uretir
- `ops/register_bridge_task.ps1`
	- Task Scheduler kaydini olusturur
- `ops/build_windows_bundle.ps1`
	- dagitim artifact'i hazirlama akisina yardim eder

Ilgili belgeler:

- `docs/secure_pc_bridge.md`
- `docs/secure_pc_probe.md`
- `docs/blank_machine_onboarding.md`
- `docs/sr3500_driver_recovery.md`
- `docs/sr3500_input_trace.md`

## Bilinen Sinirlar

- Gercek scanner driver/TWAIN entegrasyonu halen kapsam disidir.
- Kullanici girisi ve yetkilendirme yoktur.
- Optik sinav kodu ve tarih alanlari icin guvenilir matris kaniti halen acik bir kalemdir.
- Legacy vendor sabit-genislik TXT ortalama puan uyumu konusu bilincli olarak ayri tutulmustur.
- Cok genis gerçek saha PDF'leri icin son operator kabul turu halen gereklidir.

## Proje Dosyalari

- Governance: `AGENTS.md`, `GLOBAL_PLAN_TASK_TRACKING_TEMPLATE.md`, `plans/PLAN_20260409_exam_reading_platform_master.md`
- Ajan hafizasi: `AGENT_MEMORY_AND_LESSONS.md`, `AGENT_ARCHITECTURE_AND_PATTERNS.md`, `AGENT_ENVIRONMENT_AND_API.md`, `AGENT_USER_PREFERENCES.md`
- Donor kaynak: `Universal-Agent-OS/tr/AGENT_OS_RULES.md`

## Sonraki Teknik Adimlar

- Gercek saha kagitlariyla PDF okunabilirligi ve yeni secenek-dagilim tablosu kabul turu
- Optik sinav kodu/tarih alanlari icin ek matris kaniti
- Gerekirse packaged runtime ve GitHub snapshot akisinin rutinlestirilmesi