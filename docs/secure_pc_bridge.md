# Secure PC Bridge

Bu entegrasyon modeli mevcut vendor yaziliminin kurulu oldugu klasore, driver'ina veya registry ayarlarina mudahale etmez. Yalnizca vendor export klasorune birakilan dosyalari alip lokal API'ye yollar.

## Akis

1. Vendor yazilimi `TXT` veya `CSV` exportu ayri bir staging klasorune yazar.
2. Uygulama `127.0.0.1:8140` uzerinde lokal olarak calisir.
3. [ops/watch_vendor_export.ps1](../ops/watch_vendor_export.ps1) staging klasorundeki dosyalari `POST /api/exams/{exam_code}/imports` endpoint'ine gonderir.
4. Basarili importlar `_processed`, hatalar `_error` altina tasinir.

Bu modelde veri cihaz disina cikmaz; tum trafik ayni bilgisayarda `localhost` uzerinden akar.

## Guvenlik tedbirleri

- Vendor uygulamanin kurulu oldugu dizine yazmayin.
- Export icin ayrilmis bir klasor kullanin. Onerilen yapi: `C:\SecureExam\incoming`, `C:\SecureExam\incoming\_processed`, `C:\SecureExam\incoming\_error`.
- Bridge scripti sadece staging klasorundeki export dosyalarini tasir; vendor program dosyalarina veya driver'lara dokunmaz.
- Uygulamayi standart lokal kullanici ile calistirin. Servis gerekiyorsa once test ortaminda deneyin.
- Web uygulamasini `127.0.0.1` ile sinirli tutun. Dis interface bind etmeyin.

## Ornek cagrilar

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\watch_vendor_export.ps1 \
  -InputFolder C:\SecureExam\incoming \
  -ExamCode TEKKITAPCIK \
  -ApiBaseUrl http://127.0.0.1:8140 \
  -FilePattern *.txt
```

Script tek kosuda mevcut dosyalari isler. En dusuk riskli surekli calisma modeli, bu komutu Windows Task Scheduler ile periyodik tetiklemektir.

## Acik kaynak servis secenekleri

- `NSSM`: lokal exe veya PowerShell scriptini Windows service olarak sarmalamak icin kullanilabilir.
- `WinSW`: XML tabanli servis tanimi isteyen ortamlar icin alternatiftir.

Bu iki secenek de opsiyoneldir. Varsayilan ve en dusuk riskli yol, once Task Scheduler ile ilerlemektir.

## Python'siz secure-PC dagitimi
3. Bundle klasorunu secure-PC'ye offline kopyalayin.
4. Secure-PC'de yalnizca paketlenmis runtime, `backend/data/` ve bridge script calissin.

Bu modelde secure-PC'ye `pip`, `uvicorn` veya Python runtime kurmak gerekmez.

## Format notlari

- Repodaki ornek `TXT`, ham cevap importu icin esas referanstir.
- Repodaki ornek `XLSX` ve `PDF`, ozet rapordur; ham cevap kaynagi olarak import edilmez.
- Coklu kitapcikli sinavlarda vendor exportunun kitapcik bilgisini satir basi marker veya ayri dosya duzeyinde tasimasi gerekir.# Secure PC Bridge

Bu belge, mevcut vendor optik okuyucu yazilimina dokunmadan yeni sistemi guvenli PC'ye baglamak icin kanonik entegrasyon yolunu tarif eder.

## Hedef

- Guvenli PC'ye Python kurmak zorunlu olmayacak.

## Onerilen baglanti modeli

1. Vendor yazilimi mevcut akista calismaya devam eder.
2. Vendor yazilimi cevap exportunu ayri bir klasore `TXT` olarak yazar.
3. `ops/watch_vendor_export.ps1` yalnizca bu klasoru izler.
4. Script yeni dosyayi `http://127.0.0.1:8140/api/exams/{exam_code}/imports` adresine yollar.
5. Script isterse dosyanin bir kopyasini ayri bir arsiv klasorune alir.

Bu modelin kritik ozelligi: vendor kurulumuna, driver'a, registry'ye, TWAIN ayarlarina veya mevcut uygulama dizinine yazma ihtiyaci yoktur.

## Neden bu model

- Entegrasyon dosya seviyesindedir; mevcut driver davranisini degistirmez.
- Veri akisi `localhost` ile sinirlidir.

1. Vendor yaziliminda mevcut export akisini degistirmeden, yalnizca yeni bir export klasoru tanimlayin.
2. Yeni klasor icin vendor yazilimindan ayri bir yol secin.

## Driver koruma tedbirleri

- Vendor uygulamasinin kendi klasorlerine dosya yazmayin.
- Export dosyasini tasimak yerine kopya almak daha guvenlidir.
- Bridge icin ayrica ayri bir log ve arsiv klasoru kullanin.
- Ilk denemede scripti vendor uygulamasi kapaliyken degil, normal akis altinda gozlemleyin.
- Ayni anda hem vendor yazilimi hem bridge ayni dosyaya yazmasin; bridge dosya boyutu ve zaman damgasi sabitlenmeden import etmez.

## Python'siz dagitim

Uygulama runtime'i Python tabanli olsa da secure PC'ye Python kurmak zorunda degilsiniz. Onerilen yol:

1. Gelistirme makinesinde Windows artifact'i uretin.
2. Artifact icine Python runtime'i gomulu gelsin.
3. Secure PC'ye yalnizca bu artifact'i kopyalayin.
4. Secure PC'de internet baglantisi gerektirmeden uygulamayi calistirin.

Pratikte bu, gelistirme makinesinde `PyInstaller` benzeri paketleyici ile `onedir` bundle uretmek anlamina gelir. `onedir` secenegi, tek dosya paketlere gore antivirus ve debug acisindan daha ongorulebilir davranir.

## Servisleştirme secenekleri

- En dusuk risk: scripti elle veya Windows Task Scheduler ile baslatmak.
- Daha kalici servis: acik kaynak `NSSM` ile PowerShell scriptini Windows service olarak host etmek.

`NSSM` kullanilirsa sadece bridge scripti servisleştirilir; vendor yazilimina veya driver servisine dokunulmaz.

## Ornek calistirma

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\watch_vendor_export.ps1 \
  -ExamCode TEKKITAPCIK \
  -WatchPath C:\VendorExports \
  -ArchivePath C:\SinavOkuma\archive
```

## Bilinen limitler

- Ornek `ADS 510 VİZE.xlsx` tipi rapor dosyalari import edilmez; bunlar soru-cevap degil ozet rapordur.
- Birden fazla kitapcikli sinavda vendor TXT kitapcik kodu tasimiyorsa sistem dosyayi bilincli olarak reddeder.
- Tarayici walkthrough ve saha kabul turu halen manuel adim gerektirir.