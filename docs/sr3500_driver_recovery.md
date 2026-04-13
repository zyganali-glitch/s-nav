# SR-3500 Driver Recovery

Bu repo icinde makineyi veya vendor yazilimini "hackleme" akisi yok. Eksik driver problemi icin desteklenen yol, calisan bir makineden ilgili driver paketini mesru sekilde export edip hedef makineye kurmaktir.

Bu workflow iki makine varsayar:

- Calisan makine: SR-3500'in veya vendor yaziliminin duzgun calistigi makine
- Hedef makine: Bu repodaki lokal uygulamanin calistigi ama `Optical Mark Reader` aygitinin `Problem Code 28` verdigi makine

## 1) Calisan Makinede Driver Adaylarini Export Et

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\ops\export_sr3500_driver_candidates.ps1
```

Varsayilan cikti klasoru:

- `C:\SecureExam\driver-recovery\sr3500-driver-export-YYYYMMDD-HHMMSS`

Bu arac sunlari yapar:

- `C:\Windows\INF\oem*.inf` altinda `VID_0A41`, `VID_0461`, `Optical Mark Reader`, `Sekonic`, `SR-3500` eslesmelerini arar
- Eslesen INF paketlerini `pnputil /export-driver` ile export etmeye calisir
- Uygun gorunen uninstall/program kayitlarini rapora ekler
- `setupapi.dev.log` icinden ilgili satirlari ayri ipucu dosyasina yazar

Ana rapor dosyalari:

- `report.txt`
- `report.json`
- `exported-drivers\`

## 2) Export Klasorunu Hedef Makineye Tasiyin

Butun export klasorunu, ozellikle `exported-drivers` altindaki dosyalari hedef makineye kopyalayin.

## 3) Hedef Makinede Driver Paketini Kur

PowerShell'i yonetici olarak acip:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\ops\install_exported_driver_bundle.ps1 -DriverBundlePath 'D:\tasinan-klasor\exported-drivers'
```

Alternatif olarak tek INF icin dogrudan:

```powershell
pnputil /add-driver "D:\tasinan-klasor\exported-drivers\*.inf" /install
```

Kurulumdan sonra:

1. SR-3500'i USB'den cikarip tekrar tak
2. `ops\probe_secure_pc_reader.ps1` ile problem durumunu yeniden kontrol et
3. `ops\run_sr3500_input_trace.ps1 -DurationSeconds 120` ile canli trace'i tekrar al

## 4) Beklenen Sonuc

- `USB\VID_0A41&PID_1004` icin `Problem Code 28` kalkarsa driver katmani acilmis olur
- Trace log'unda `HID_EVENT` veya cihaz kaynakli `KEY_EVENT` gorulmeye baslarsa browser entegrasyonu tekrar denenir

## 5) Eger Export Hicbir Sey Bulamazsa

Bu durumda buyuk olasilikla driver, INF eslesmesinden degil vendor kurulum paketi icinden geliyor demektir. O zaman siradaki mesru yol:

1. Vendor CD/setup paketini bulmak
2. Calisan makinedeki `Program Files` veya kurulum medyasindan vendor driver paketini almak
3. Hedef makinede kurup trace/probe turlerini yeniden kosmak

Bu asamadan sonra hala event akmiyorsa sorun browser degil, vendor protokol veya servis bagimliligi olur.

## 6) Elinizde Ust Model Kurulum CD'si Varsa

Bu medyayi dogrudan kurup tek makineyi riske atmak yerine once read-only tarayin.

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\ops\inspect_driver_media.ps1 -MediaRoot 'F:\'
```

Not:

- Bu script hicbir sey kurmaz.
- Yalnizca INF, CAB, EXE, MSI, INI gibi dosyalari tarar ve `SR-3500`, `Sekonic`, `Optical Mark`, `VID_0A41`, `VID_0461` ipuclarini arar.

Eger medya okunamiyorsa once su durum dogrulanmali:

- Windows'ta CD surucusu hazir mi
- Gercekten disk takili mi
- `F:\` gibi yol `Test-Path` ile aciliyor mu

Eger INF veya model referansi iceren klasor bulunursa:

1. O klasoru once ayrica kopyalayin
2. Kurulumu hedef makinede direkt denemeyin
3. Mumkunse ayni medyayi baska test ortamina veya sanal/ayri makineye acip driver export workflow'u ile devam edin

Eger sadece setup EXE varsa:

1. EXE'yi bu makinede kör calistirmayin
2. Once medya tarama raporundan EXE ve yakinindaki CAB/INF dosyalarini belirleyin
3. Mumkunse ayri bir ortamda setup'i acip `export_sr3500_driver_candidates.ps1` ile driver paketini ayiklayin