# Global Plan ve Gorev Takip Sablonu

Bu sablon self-contained'dir.
Bu repoda her yeni task icin plan dosyasi `plans/` altinda uretilir.

---

## 0) Belge Kimligi

- Plan dosya adi: `{{PLAN_FILENAME}}`
- Aktif plan yolu: `plans/{{PLAN_FILENAME}}`
- Tamamlanan plan yolu: `plans/completed/{{PLAN_FILENAME}}`
- Plan ID: `{{PLAN_ID}}`
- Hedef platform: `{{WEB|DESKTOP-WEB|API}}`
- Son guncelleme: `{{YYYY-MM-DD HH:mm TZ}}`
- Plan sahibi: `{{OWNER}}`
- Aktif durum: `{{PLANNING|IN_PROGRESS|BLOCKED|DONE}}`

### 0.1) Integrity Lock

- IL-01: Gorev takip cizelgesi resmi kaynaktir.
- IL-02: Header + faz + backlog + task table + gate + risk + handoff ayni editte guncellenir.
- IL-03: Alt kalemler acikken ust kalem kapanmaz.
- IL-04: Gelecek tarihli tamamlanma yazilmaz.
- IL-05: Zorunlu gate `NOT_RUN` veya `FAIL` ise closure yoktur.
- IL-06: Discovered work yeni satir olarak eklenir.
- IL-07: Mikro-adim baslarken `DEVAM`, biterken kanit yazilir.

---

## 1) Phase-0 Kararlari

- Iletisim tonu:
- Platform:
- Dagitim modeli:
- Veri saklama modeli:
- Auth/Billing kapsami:
- Dil modeli:

---

## 2) Scope Lock

- Kapsam ici:
- Kapsam disi:
- En kucuk sonraki adim:

---

## 3) Allowlist

-

---

## 4) Faz Plani

| Faz | Aciklama | Durum |
|---|---|---|
| F1 | Governance ve Phase-0 | |
| F2 | Domain ve backend | |
| F3 | Frontend ve operator akisi | |
| F4 | Test, smoke ve hardening | |

---

## 5) Mikro-Faz Backlogu

| ID | Baslik | Durum |
|---|---|---|

---

## 6) Talep Derleme Tablosu

| REQ-ID | Talep | Kapsam | Durum |
|---|---|---|---|

---

## 7) Gorev Takip Cizelgesi

| Faz | Adim | Aciklama | Durum | Ust ID | Ajan | Baslangic | Tamamlanma | Parity | Notlar |
|---|---|---|---|---|---|---|---|---|---|

---

## 8) Gate Plani

| Gate | Durum | Kanit |
|---|---|---|
| Smoke Gate | NOT_RUN | |
| Binding Gate | NOT_RUN | |
| Related-Tests Gate | NOT_RUN | |
| Parity Gate | NOT_RUN | |
| No-UI-Regression Gate | NOT_RUN | |
| I18N-Completeness Gate | NOT_RUN | |
| Integrity-Lock Gate | PASS | |
| Release/NFR Gate | NOT_RUN | |

---

## 9) Risk Kaydi

| Risk ID | Risk | Durum | Azaltma |
|---|---|---|---|

---

## 10) Handoff

- Son tamamlanan mikro-adim:
- Sonraki mikro-adim:
- Acik risk/bloke:
- Degisen dosyalar:
- Gate durumu:
- Checkpoint: