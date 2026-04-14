"""
SIN ADAM formundaki isaretli hucrelerin matris koordinatlarini tespit et.
Satir merkezleri sag zamanlama seridinden, sutun merkezleri ise
bilinen grid yapisina gore hesaplanir.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
import fitz

doc = fitz.open(str(ROOT / "örnek" / "SIN ADAM.pdf"))
page = doc[0]
pix = page.get_pixmap(dpi=300)
width, height = pix.width, pix.height
samples = pix.samples
stride = pix.stride
n = pix.n

def get_gray(x: int, y: int) -> int:
    if x < 0 or x >= width or y < 0 or y >= height:
        return 255
    offset = y * stride + x * n
    return (samples[offset] + samples[offset + 1] + samples[offset + 2]) // 3

# --- Satir merkezleri (sag zamanlama seridinden) ---
right_timing_x = 2413  # onceki analizden
MARK_THRESHOLD = 40

timing_profile = []
for y in range(height):
    darkness = 0
    cnt = 0
    for dx in range(-5, 6):
        xx = right_timing_x + dx
        if 0 <= xx < width:
            darkness += (255 - get_gray(xx, y))
            cnt += 1
    timing_profile.append(darkness / cnt if cnt else 0)

in_mark = False
mark_start = 0
row_centers = []
for y in range(height):
    if timing_profile[y] > MARK_THRESHOLD:
        if not in_mark:
            mark_start = y
            in_mark = True
    else:
        if in_mark:
            row_centers.append((mark_start + y) // 2)
            in_mark = False
if in_mark:
    row_centers.append((mark_start + height) // 2)

print(f"Satir sayisi: {len(row_centers)}")
row_spacing = (row_centers[-1] - row_centers[0]) / (len(row_centers) - 1) if len(row_centers) > 1 else 50
print(f"Satir araligi: {row_spacing:.1f}px")

# --- Sutun merkezlerini bul ---
# Sol kenar timing veya form sol kenari tespiti
# Formun ust satirindaki isaret merkezlerinden sutun pozisyonlarini cikar
# İlk satir (row_centers[0]) uzerinden yatay tarama
first_row_y = row_centers[0]
print(f"\nIlk satir y={first_row_y}, yatay profil taranıyor...")

# İlk satirda sutun isaretlerini bul
h_profile = []
for x in range(width):
    darkness = 0
    cnt = 0
    for dy in range(-8, 9):
        yy = first_row_y + dy
        if 0 <= yy < height:
            darkness += (255 - get_gray(x, yy))
            cnt += 1
    h_profile.append(darkness / cnt if cnt else 0)

# Ilk satirdaki koyu bolgelerin merkezleri = sutun pozisyonlari
in_mark = False
mark_start = 0
col_centers_r1 = []
for x in range(width):
    if h_profile[x] > 50:
        if not in_mark:
            mark_start = x
            in_mark = True
    else:
        if in_mark:
            w = x - mark_start
            if w > 5:  # cok kucuk gurultuyu filtrele
                col_centers_r1.append((mark_start + x) // 2)
            in_mark = False
if in_mark and (width - mark_start) > 5:
    col_centers_r1.append((mark_start + width) // 2)

print(f"Ilk satirdaki koyu bolge sayisi: {len(col_centers_r1)}")
if col_centers_r1:
    print(f"Ilk 10 x: {col_centers_r1[:10]}")
    print(f"Son 10 x: {col_centers_r1[-10:]}")

# Alternatif: birden fazla satiri kullanarak ortak sutun pozisyonlarini bul
# Orta satirlari kullan (name/answer bolgeleri dolu)
print("\nCoklu satir analizi ile sutun tespiti...")
col_votes = {}
SCAN_ROWS = list(range(0, min(len(row_centers), 65)))  # tum satirlar
for ri in SCAN_ROWS:
    ry = row_centers[ri]
    profile = []
    for x in range(width):
        darkness = 0
        cnt = 0
        for dy in range(-6, 7):
            yy = ry + dy
            if 0 <= yy < height:
                darkness += (255 - get_gray(x, yy))
                cnt += 1
        profile.append(darkness / cnt if cnt else 0)
    
    # Bu satirdaki koyu bolgelerin merkezleri
    in_m = False
    ms = 0
    for x in range(width):
        if profile[x] > 35:
            if not in_m:
                ms = x
                in_m = True
        else:
            if in_m:
                w = x - ms
                if 8 < w < 40:  # makul balon genisligi
                    cx = (ms + x) // 2
                    # En yakin 5px'lik gruba ekle
                    found = False
                    for key in list(col_votes.keys()):
                        if abs(key - cx) < 8:
                            col_votes[key] = col_votes[key] + 1
                            found = True
                            break
                    if not found:
                        col_votes[cx] = 1
                in_m = False

# En cok oy alan sutunlar (tum satirlarda gorunenler = timing veya grid cizgileri)
sorted_cols = sorted(col_votes.items(), key=lambda x: -x[1])
print(f"Toplam aday sutun: {len(sorted_cols)}")
# En az 20 satirda gorunen sutunlar = grid sutunlari
consistent_cols = sorted([x for x, count in sorted_cols if count >= 15], key=lambda x: x)
print(f"Tutarli sutun sayisi (>=15 satirda): {len(consistent_cols)}")
if consistent_cols:
    print(f"Sutun x pozisyonlari: {consistent_cols}")

# 48 sutun bekliyoruz (veya yakin)
if len(consistent_cols) >= 40:
    col_spacing = (consistent_cols[-1] - consistent_cols[0]) / (len(consistent_cols) - 1) if len(consistent_cols) > 1 else 50
    print(f"Sutun araligi: {col_spacing:.1f}px")
    
    # Grid matrisi olustur ve dolu hucreleri bul
    print(f"\n--- DOLU HUCRELER ({len(row_centers)} satir x {len(consistent_cols)} sutun) ---")
    CELL_R = 8
    FILL_THR = 90
    
    filled = []
    for ri, ry in enumerate(row_centers):
        for ci, cx in enumerate(consistent_cols):
            total = 0
            cnt = 0
            for dy in range(-CELL_R, CELL_R + 1, 2):
                for dx in range(-CELL_R, CELL_R + 1, 2):
                    total += (255 - get_gray(cx + dx, ry + dy))
                    cnt += 1
            avg = total / cnt if cnt else 0
            if avg > FILL_THR:
                filled.append((ri + 1, ci + 1, round(avg)))
    
    print(f"Toplam dolu hucre: {len(filled)}")
    
    # Tum dolu hucreleri bas
    for r, c, d in filled:
        print(f"  R{r:02d}C{c:02d} = {d}")
    
    # SINAV KODU ve TARIH bolgesi (satir 38-60)
    print(f"\n--- SATIR 38-60 ARASI DOLU HUCRELER ---")
    for r, c, d in filled:
        if 38 <= r <= 60:
            print(f"  R{r:02d}C{c:02d} = {d}")
    
    # SINIF (satir 23-32 ve ust sutunlar)
    print(f"\n--- SINIF BOLGESI (satir 23-34, sutun 30-48) ---")
    for r, c, d in filled:
        if 23 <= r <= 34 and 30 <= c:
            print(f"  R{r:02d}C{c:02d} = {d}")
