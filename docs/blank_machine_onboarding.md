# Blank Machine Onboarding

Bu belge, driver'i olmayan bosta bir Windows makineyi guvenli entegrasyon hedefi olarak hazirlamak icin gerekli dosya ve ayarlari tarif eder.

## Hedef

- Makineyi bozmadan klasor yapisini kurmak.
- Probe, bridge ve runtime dosyalarini ayni paketle hazirlamak.
- Python kurulu olmasa bile bundle ile ilerleyebilmek.

## Hazirlanan dosyalar

- [ops/secure_pc_config.template.json](../ops/secure_pc_config.template.json)
- [ops/setup_blank_machine.ps1](../ops/setup_blank_machine.ps1)
- [ops/register_bridge_task.ps1](../ops/register_bridge_task.ps1)
- [ops/build_windows_bundle.ps1](../ops/build_windows_bundle.ps1)
- [ops/start_runtime_from_config.ps1](../ops/start_runtime_from_config.ps1)
- [ops/probe_secure_pc_reader.ps1](../ops/probe_secure_pc_reader.ps1)

## Adimlar

1. Gelistirme makinesinde bundle uretin.
2. Bos makinede klasor yapisini kurun.
3. Probe alin.
4. Cihaz enumerate oluyorsa direct bypass fizibilitesini degerlendirin.
5. Enumerate olmuyorsa bridge veya gecici UI otomasyonu fazina gecin.

## 1. Bundle uretme

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\build_windows_bundle.ps1
```

Bu script PyInstaller kullanarak Windows bundle klasoru uretir ve probe/bridge scriptlerini ayni ciktiya kopyalar.

## 2. Bos makinede klasor ve config kurma

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\setup_blank_machine.ps1 \
  -BaseFolder C:\SecureExam \
  -ExamCode TEKKITAPCIK
```

Bu komut su yapilari olusturur:

- `C:\SecureExam\incoming`
- `C:\SecureExam\incoming\_processed`
- `C:\SecureExam\incoming\_error`
- `C:\SecureExam\probe-output`
- `C:\SecureExam\runtime`
- `C:\SecureExam\logs`
- `C:\SecureExam\secure_pc_config.json`

## 3. Probe alma

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\probe_secure_pc_reader.ps1 \
  -OutputFolder C:\SecureExam\probe-output \
  -IncludeUsbDevices
```

## 4. Bridge gorevi kaydetme

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\register_bridge_task.ps1 \
  -ConfigPath C:\SecureExam\secure_pc_config.json \
  -ScriptPath .\ops\watch_vendor_export.ps1
```

Bu adim sadece bridge fazi kullanilacaksa gerekir.

## 5. Runtime baslatma

Bundle `C:\SecureExam\runtime` altina kopyalandiktan sonra:

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\start_runtime_from_config.ps1 \
  -ConfigPath C:\SecureExam\secure_pc_config.json
```

Bu script host, port ve state dosyasi ortam degiskenlerini config'ten okuyup bundle exe'yi baslatir.

## Kritik not

Bu makinede driver olmamasi, direct bypass'in imkansiz oldugu anlamina gelmez; ama hicbir standart imaging katmani enumerate olmuyorsa dogrudan alim karari veremeyiz. Bu durumda probe sonucu beklenmeli.