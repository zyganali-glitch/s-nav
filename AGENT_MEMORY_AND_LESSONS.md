# Agent Memory And Lessons

- 2026-04-09: Proje yanlislikla baska repoda baslatildi; bu kokte governance kurulmadan implementasyona gecilmeyecek.
- 2026-04-09: Bu urunde QR kapsami bilincli olarak disarida; ilk operator yolu vendor export veya manuel veri importudur.
- 2026-04-09: Workspace Python ortami bu repoda paylasilan `.venv` olarak otomatik cozulebilir; komutlar explicit Python executable ile calistirilirsa karisiklik azalir.
- 2026-04-09: Testler runtime state dosyasini kirletmemeli; `create_app(state_file=...)` gibi injectable state yolu kullanilip production `app_state.json` bos tutulacak.