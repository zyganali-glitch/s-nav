"""
SIN ADAM PDF → tam hucreli grid haritasi.
1) 65 satir merkezini sag zamanlama seridinden bul
2) 48 sutun merkezini HER SATIRDAKI zamanlama iziinden bul (satir 1 timing row)
3) Her hucrenin ortalama karanligini olc
4) Rows 38-65 icin dolu hucreleri raporla
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
nc = pix.n

def get_gray(x: int, y: int) -> int:
    if x < 0 or x >= width or y < 0 or y >= height:
        return 255
    off = y * stride + x * nc
    return (samples[off] + samples[off + 1] + samples[off + 2]) // 3

# ────────────────────────────────────────────
# 1) Satir merkezleri (sag zamanlama seridi x~2390)
# ────────────────────────────────────────────
RIGHT_TIMING_X = 2390
row_centers = []
in_mark = False
mark_start = 0
for y in range(height):
    d = sum(255 - get_gray(RIGHT_TIMING_X + dx, y) for dx in range(-5, 6))
    val = d / 11
    if val > 40:
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
if len(row_centers) >= 2:
    row_spacing = (row_centers[-1] - row_centers[0]) / (len(row_centers) - 1)
    print(f"Satir araligi: {row_spacing:.1f} px")
else:
    row_spacing = 50.0

# ────────────────────────────────────────────
# 2) Sutun merkezlerini bul: birden fazla bos satirdaki zamanlama izlerini kullan
#    Satir 1 (y=row_centers[0]) boyunca zamanlama izlerini ara
#    Ayrica: bilindigine gore C1 en sagda, C48 en solda
#    Sag zamanlama = C1, Sol zamanlama = C48 olmali
# ────────────────────────────────────────────

# Satir 1'den koyu bolgeleri bul (zamanlama izleri)
def find_dark_clusters(y_center, threshold=40, half_h=7, min_width=5):
    """y_center etrafinda yatay karanlik profili cek, kumeleri dondur"""
    profile = []
    for x in range(width):
        d = 0
        c = 0
        for dy in range(-half_h, half_h + 1):
            yy = y_center + dy
            if 0 <= yy < height:
                d += 255 - get_gray(x, yy)
                c += 1
        profile.append(d / c if c else 0)

    clusters = []
    in_cl = False
    cs = 0
    for x, v in enumerate(profile):
        if v > threshold:
            if not in_cl:
                cs = x
                in_cl = True
        else:
            if in_cl:
                if x - cs >= min_width:
                    cx = (cs + x) // 2
                    peak = max(profile[cs:x])
                    clusters.append((cx, peak))
                in_cl = False
    return clusters

# Birden fazla satirdaki zamanlama izlerini topla
# Bos satir = ogrenci bilgisi veya cevap isaretlenmemis satir
# Satir 1, 33-36 arasi (bos bolge) kullan
timing_rows = [0]  # row 1
if len(row_centers) >= 36:
    timing_rows.extend([32, 33, 34, 35])  # rows 33-36 (0-indexed)

all_timing_x = []
for ri in timing_rows:
    if ri >= len(row_centers):
        continue
    ry = row_centers[ri]
    clusters = find_dark_clusters(ry, threshold=35, half_h=6)
    print(f"  Satir {ri+1} (y={ry}): {len(clusters)} kume")
    for cx, pk in clusters:
        all_timing_x.append(cx)

# Zamanlama izlerini kumelere ayir
if all_timing_x:
    all_timing_x.sort()
    col_clusters = []
    current = [all_timing_x[0]]
    for x in all_timing_x[1:]:
        if x - current[-1] <= 15:
            current.append(x)
        else:
            col_clusters.append(sum(current) // len(current))
            current = [x]
    col_clusters.append(sum(current) // len(current))
    print(f"\nToplam sutun kume sayisi: {len(col_clusters)}")
    if len(col_clusters) <= 60:
        for i, cx in enumerate(col_clusters):
            print(f"  Kume {i}: x={cx}")

# ────────────────────────────────────────────
# 2b) Eger kume sayisi 48'e yakin degilse, grid'i hesapla
#     Sol timing = C48, Sag timing = C1
#     Sol timing: form sol kenarindaki ilk koyu bolge
#     Sag timing: x~2390
# ────────────────────────────────────────────

# Sol ve sag zamanlama x'lerini tum satirlardan bul
LEFT_TIMING_X = None
RIGHT_TIMING_X_EXACT = None

# Satir 1'deki en sol ve en sag kumeleri kullan
r1_clusters = find_dark_clusters(row_centers[0], threshold=35, half_h=6)
if r1_clusters:
    LEFT_TIMING_X = r1_clusters[0][0]  # en sol
    RIGHT_TIMING_X_EXACT = r1_clusters[-1][0]  # en sag
    print(f"\nSol timing x: {LEFT_TIMING_X}")
    print(f"Sag timing x: {RIGHT_TIMING_X_EXACT}")

# Grid hesapla: C48 = sol, C1 = sag
if LEFT_TIMING_X and RIGHT_TIMING_X_EXACT:
    col_spacing = (RIGHT_TIMING_X_EXACT - LEFT_TIMING_X) / 47
    print(f"Sutun araligi: {col_spacing:.2f} px")

    col_centers = {}
    for c in range(1, 49):
        # C1 = sag timing, C48 = sol timing
        col_centers[c] = round(RIGHT_TIMING_X_EXACT - (c - 1) * col_spacing)

    print(f"\nSutun pozisyonlari:")
    for c in range(1, 49):
        print(f"  C{c:02d} = x={col_centers[c]}")

# ────────────────────────────────────────────
# 3) Her hucrenin karanligini olc (rows 1-65, cols 1-48)
# ────────────────────────────────────────────
CELL_HALF = 8  # hucre merkezinin +/- bu kadar piksel cevresi

def cell_darkness(row_idx, col_num):
    """0-indexed row, 1-indexed col → ortalama karanlik"""
    if row_idx >= len(row_centers):
        return 0
    cy = row_centers[row_idx]
    cx = col_centers[col_num]
    total = 0
    cnt = 0
    for dy in range(-CELL_HALF, CELL_HALF + 1):
        for dx in range(-CELL_HALF, CELL_HALF + 1):
            total += 255 - get_gray(cx + dx, cy + dy)
            cnt += 1
    return total / cnt if cnt else 0

# ────────────────────────────────────────────
# 4) Rows 23-55 x Cols 30-48 (student+class+exam bolgeleri)
#    Isaretli hucreleri raporla
# ────────────────────────────────────────────
print("\n" + "=" * 70)
print("HUCRE KARANLIK HARITASI (karanlik > 50 = DOLU)")
print("=" * 70)

# Once bilinen alanlari dogrula: student number
print("\n--- OGRENCI NUMARASI (R23-R32, C35-C45) ---")
for ri in range(22, 32):  # 0-indexed
    for c in range(35, 46):
        d = cell_darkness(ri, c)
        if d > 50:
            print(f"  R{ri+1:02d} C{c:02d} = {d:.0f}")

print("\n--- SINIF (R23-R32, C31-C34) ---")
for ri in range(22, 32):
    for c in range(31, 35):
        d = cell_darkness(ri, c)
        if d > 50:
            print(f"  R{ri+1:02d} C{c:02d} = {d:.0f}")

print("\n--- KITAPCIK (R37, C36-C42) ---")
for c in range(36, 43):
    d = cell_darkness(36, c)
    if d > 50:
        print(f"  R37 C{c:02d} = {d:.0f}")

# Bilinen cevap alanlari (R36-R40 civarinda 5 cevap)
print("\n--- CEVAPLAR (R36-R40, C26-C30) ---")
for ri in range(35, 40):
    for c in range(26, 31):
        d = cell_darkness(ri, c)
        if d > 50:
            print(f"  R{ri+1:02d} C{c:02d} = {d:.0f}")

# Sinav kodu/tarih bolgesini genisce tara
print("\n--- SINAV KODU + TARİH TARAMASI (R38-R60, C30-C48) ---")
print("    (satir x sutun : karanlik)")
for ri in range(37, 60):
    row_marks = []
    for c in range(30, 49):
        d = cell_darkness(ri, c)
        if d > 50:
            row_marks.append((c, d))
    if row_marks:
        marks_str = ", ".join(f"C{c}={d:.0f}" for c, d in row_marks)
        print(f"  R{ri+1:02d}: {marks_str}")

# Daha genis tarama: R38-R60, C1-C48 (tum sutunlar)
print("\n--- GENIS TARAMA (R38-R60, C1-C48) ---")
for ri in range(37, 60):
    row_marks = []
    for c in range(1, 49):
        d = cell_darkness(ri, c)
        if d > 50:
            row_marks.append((c, d))
    if row_marks:
        # timing strip (C48) haric
        non_timing = [(c, d) for c, d in row_marks if c != 48]
        if non_timing:
            marks_str = ", ".join(f"C{c}={d:.0f}" for c, d in non_timing)
            print(f"  R{ri+1:02d}: {marks_str}")

# Ekstra: SIN ADAM'in ISIM alanini dogrula (rows 2-33, cols 19-28)
print("\n--- ISIM 'SIN' dogrulama (R2-R33, C19-C28) ---")
for ri in range(1, 33):
    for c in range(19, 29):
        d = cell_darkness(ri, c)
        if d > 80:
            print(f"  R{ri+1:02d} C{c:02d} = {d:.0f}")

print("\n--- SOYISIM 'ADAM' dogrulama (R2-R33, C6-C15) ---")
for ri in range(1, 33):
    for c in range(6, 16):
        d = cell_darkness(ri, c)
        if d > 80:
            print(f"  R{ri+1:02d} C{c:02d} = {d:.0f}")
