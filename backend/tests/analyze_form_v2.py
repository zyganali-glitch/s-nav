"""
SIN ADAM formunu analiz et:
- Satir merkezleri zamanlama seridinden (65 adet)
- Sutun merkezleri: zamanlama izi + grid araligi ile hesapla
- Her hucredeki karanlik = isaretli balon
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

# Satir merkezleri
RIGHT_X = 2413
row_centers = []
in_mark = False
ms = 0
for y in range(height):
    d = 0
    c = 0
    for dx in range(-5, 6):
        xx = RIGHT_X + dx
        if 0 <= xx < width:
            d += (255 - get_gray(xx, y))
            c += 1
    val = d / c if c else 0
    if val > 40:
        if not in_mark:
            ms = y
            in_mark = True
    else:
        if in_mark:
            row_centers.append((ms + y) // 2)
            in_mark = False
if in_mark:
    row_centers.append((ms + height) // 2)

print(f"Satir: {len(row_centers)}")

# Sutun merkezlerini bul: sol kenardaki zamanlama seridini ara
# Sol kenarda (x < 200) dikey karanlik profili
print("\nSol kenar zamanlama tespiti...")
for test_x in [50, 100, 130, 150, 170, 200]:
    darkness = 0
    cnt = 0
    for y in range(0, height, 5):
        darkness += (255 - get_gray(test_x, y))
        cnt += 1
    avg = darkness / cnt if cnt else 0
    print(f"  x={test_x}: avg_darkness={avg:.1f}")

# Sag kenar (2350-2450 arasi)
print("\nSag kenar zamanlama tespiti...")
for test_x in [2350, 2370, 2390, 2410, 2430, 2450]:
    if test_x >= width:
        continue
    darkness = 0
    cnt = 0
    for y in range(0, height, 5):
        darkness += (255 - get_gray(test_x, y))
        cnt += 1
    avg = darkness / cnt if cnt else 0
    print(f"  x={test_x}: avg_darkness={avg:.1f}")

# Ilk satir (row 1) boyunca yatay profili detayli tara
# Grid yapisini bulmak icin
row1_y = row_centers[0]
print(f"\nSatir 1 (y={row1_y}) yatay profili:")
# Her 10px'te karanlik
profile = []
for x in range(0, width, 5):
    d = 0
    c = 0
    for dy in range(-6, 7):
        d += (255 - get_gray(x, row1_y + dy))
        c += 1
    profile.append((x, d / c if c else 0))

# Koyu noktalar (>50)
dark_points = [(x, v) for x, v in profile if v > 50]
print(f"Koyu nokta sayisi: {len(dark_points)}")
for x, v in dark_points:
    print(f"  x={x}: {v:.0f}")

# Satir 37 (booklet satiri) boyunca tara
r37_y = row_centers[36]
print(f"\nSatir 37 (y={r37_y}) koyu noktalar:")
for x in range(0, width, 5):
    d = 0
    c = 0
    for dy in range(-6, 7):
        d += (255 - get_gray(x, r37_y + dy))
        c += 1
    val = d / c if c else 0
    if val > 50:
        print(f"  x={x}: {val:.0f}")

# Simdi farkli satirlardaki koyu noktalari toplayarak sutun grid'ini olustur
# Ogrenci numarasi satirlarini (23-32) tara - bilinen doluluk
print(f"\nSatir 23-32 (ogrenci no) koyu noktalar (x pozisyonlari):")
all_dark_x = []
for ri in range(22, 32):  # 0-indexed: satir 23-32
    ry = row_centers[ri]
    for x in range(0, width, 3):
        d = 0
        c = 0
        for dy in range(-5, 6):
            d += (255 - get_gray(x, ry + dy))
            c += 1
        val = d / c if c else 0
        if val > 70:
            all_dark_x.append(x)

# x pozisyonlarini kumelere ayir
if all_dark_x:
    all_dark_x.sort()
    clusters = []
    current = [all_dark_x[0]]
    for x in all_dark_x[1:]:
        if x - current[-1] <= 8:
            current.append(x)
        else:
            clusters.append(sum(current) // len(current))
            current = [x]
    clusters.append(sum(current) // len(current))
    print(f"Kume sayisi: {len(clusters)}")
    print(f"Kume merkezleri: {clusters}")

# Cevap bolgesindeki satirlari da tara (36-45, bilinen doluluk)
print(f"\nSatir 36-45 (cevaplar) koyu noktalar:")
ans_dark_x = []
for ri in range(35, 45):
    ry = row_centers[ri]
    for x in range(0, width, 3):
        d = 0
        c = 0
        for dy in range(-5, 6):
            d += (255 - get_gray(x, ry + dy))
            c += 1
        val = d / c if c else 0
        if val > 70:
            ans_dark_x.append(x)

if ans_dark_x:
    ans_dark_x.sort()
    clusters2 = []
    current = [ans_dark_x[0]]
    for x in ans_dark_x[1:]:
        if x - current[-1] <= 8:
            current.append(x)
        else:
            clusters2.append(sum(current) // len(current))
            current = [x]
    clusters2.append(sum(current) // len(current))
    print(f"Kume sayisi: {len(clusters2)}")
    print(f"Kume merkezleri: {clusters2}")

# SINAV KODU bolgesini tara (satir 38-60)
print(f"\nSatir 38-60 koyu noktalar:")
code_dark_x = []
for ri in range(37, min(60, len(row_centers))):
    ry = row_centers[ri]
    for x in range(0, width, 3):
        d = 0
        c = 0
        for dy in range(-5, 6):
            d += (255 - get_gray(x, ry + dy))
            c += 1
        val = d / c if c else 0
        if val > 70:
            code_dark_x.append((ri + 1, x, round(val)))

print(f"Dolu nokta sayisi: {len(code_dark_x)}")
for r, x, d in code_dark_x:
    print(f"  R{r:02d} x={x}: {d}")
