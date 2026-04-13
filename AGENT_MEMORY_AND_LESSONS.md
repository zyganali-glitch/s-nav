# Agent Memory And Lessons

- 2026-04-09: Proje yanlislikla baska repoda baslatildi; bu kokte governance kurulmadan implementasyona gecilmeyecek.
- 2026-04-09: Bu urunde QR kapsami bilincli olarak disarida; ilk operator yolu vendor export veya manuel veri importudur.
- 2026-04-09: Workspace Python ortami bu repoda paylasilan `.venv` olarak otomatik cozulebilir; komutlar explicit Python executable ile calistirilirsa karisiklik azalir.
- 2026-04-09: Testler runtime state dosyasini kirletmemeli; `create_app(state_file=...)` gibi injectable state yolu kullanilip production `app_state.json` bos tutulacak.
- 2026-04-13: `Varsayilan`/`katipcelebi` aileli optik sablonlarda saha semantigi bu repoda `soyad solda, ad sagda` olarak ele alinmali; ad-soyad swap bug'inde once coordinate source ve fallback named-region eslemesi kontrol edilmeli.
- 2026-04-13: Exportlarda `001A`, `ANKET01`, `13.04.2026` gibi karma alanlar bazi goruntuleyicilerde RTL ters gorunebiliyor; CSV/XLSX/TXT/PDF uretiminde bu alanlara LTR mark (`\u200e`) eklemek operator gorunumunu stabilize ediyor.