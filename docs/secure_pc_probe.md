# Secure PC Offline Probe

Bu belge, cihaz bu gelistirme makinesinde kurulu degilken direct bypass fizibilitesini guvenli PC uzerinde nasil toplayacagimizi tarif eder.

## Amac

- Cihazin Windows tarafinda `WIA`, `TWAIN`, `USB` veya vendor program seviyesinde nasil gorundugunu ogrenmek.
- Bunu tamamen read-only yapmak.
- Driver'a, registry'ye veya vendor kurulumuna yazmadan kanit toplamak.

## Kullanilacak script

- [ops/probe_secure_pc_reader.ps1](../ops/probe_secure_pc_reader.ps1)

Bu script Windows surumu, muhtemel imaging cihazlari, WIA, TWAIN, ilgili kurulu programlar ve olasi export klasor ipuclarini toplar.

## Calistirma

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\probe_secure_pc_reader.ps1 \
  -OutputFolder C:\SecureExam\probe-output \
  -IncludeUsbDevices
```

## Uretilen ciktilar

- `secure-pc-probe-YYYYMMDD-HHMMSS.json`
- `secure-pc-probe-YYYYMMDD-HHMMSS.txt`

Ilk bakista `txt` dosyasi yeterlidir. Daha fazla detay gerekirse `json` kullanilir.

## Yorumlama mantigi

1. `WIA devices` doluysa cihaz standart imaging yolu uzerinden alinabilir.
2. `TWAIN registry` doluysa vendor UI olmadan acquisition katmani yazma sansimiz artar.
3. Ikisi de bos ama vendor program gorunuyorsa export hook veya UI otomasyonu ara faz olabilir.
4. `Recent text exports` bolumu mevcut bridge akisini daha guvenli baglamamizi saglar.

## Guvenlik notu

- Script read-only tasarlanmistir.
- Yalnizca `OutputFolder` altina rapor yazar.
- Vendor dizinlerine, driver dosyalarina ve registry'ye yazmaz.