# SR-3500 Input Trace

Bu arac, SR-3500 okutmasi sirasinda Windows seviyesinde iki sinyali birlikte kaydeder:

- Global keyboard event'leri
- Bilinen SR-3500 VID/PID ciftleri icin ham HID raporlari

Amac, tarayiciya veri dusmediginde cihazin aslinda Windows'a herhangi bir keyboard veya HID akisi gonderip gondermedigini kanitlamaktir.

## Calistirma

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.
\ops\run_sr3500_input_trace.ps1 -DurationSeconds 120
```

Dogrudan Python ile:

```powershell
.
\.venv\Scripts\python.exe .\ops\trace_sr3500_input.py --duration 120
```

Varsayilan log dosyasi:

- `C:\SecureExam\probe-output\sr3500-live-trace.log`

## Beklenen Yorum

- `KEY_EVENT` goruluyorsa cihaz keyboard-wedge gibi calisiyor demektir.
- `HID_EVENT` goruluyorsa veri keyboard yerine ham HID kanalindan akiyordur.
- Ikisi de sifirsa tarayici sorunu degil; cihaz veri gondermiyor, farkli driver/protokol gerekiyor veya okutma bu oturumda vendor yazilimi uzerinden yapiliyor olabilir.
