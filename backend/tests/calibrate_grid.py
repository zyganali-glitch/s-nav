"""
SIN ADAM PDF → isabetli grid kalibrasyon.
Bilinen hucre kümelerinden (student_number) ters hesaplama ile
DOĞRU sütun merkezlerini bulan, sonra sinav kodu/tarih bolgesini haritalayan script.
"""
import sys, json
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

# ── 1) SATIR MERKEZLERİ ──
RIGHT_TIMING_X = 2390
row_centers = []
in_mark = False
mark_start = 0
for y in range(height):
    d = sum(255 - get_gray(RIGHT_TIMING_X + dx, y) for dx in range(-5, 6)) / 11
    if d > 40:
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
row_spacing = (row_centers[-1] - row_centers[0]) / (len(row_centers) - 1)
print(f"Satir araligi: {row_spacing:.2f} px  (R1 y={row_centers[0]}, R65 y={row_centers[-1]})")

# ── 2) SÜTUN KALİBRASYONU ──
# Bilinen: öğrenci numarası R23-R32, C35-C45, 10 satırlık 0-9 grid
# Her sütundaki EN KOYU hücre-x'ini bul → sütun merkezleri

# Ama once: bos bubble ring'lerini (basılı boş daireler) hariç tutmamız lazım.
# Dolayısıyla, her satır-kolon hücresinin karanliğini farklı yarıçaplarla ölçelim.
# Dolu balonlar merkez 8px yaricap, bos balonlar halka (center lighter than ring).

def sample_cell(cx, cy, half=8):
    """cx,cy pixel merkez → ortalama karanlik (255=siyah, 0=beyaz)"""
    total = 0
    cnt = 0
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            total += 255 - get_gray(cx + dx, cy + dy)
            cnt += 1
    return total / cnt

# Her studentnumber satirindaki tum x-pozisyonlarini 3px aralikla tara, 
# bulunan balon merkezlerini ver
print("\n── Satir bazli yatay profil (R23-R32) ──")
for ri in range(22, 32):
    ry = row_centers[ri]
    # Yatay profil: 3px aralik, 6px yaricapli dikey pencere
    profile = []
    for x in range(50, width - 50, 2):
        d = sum(255 - get_gray(x, ry + dy) for dy in range(-6, 7)) / 13
        profile.append((x, d))
    # Peak detection
    peaks = []
    for i in range(2, len(profile) - 2):
        x, v = profile[i]
        if v > 60:  # yüksek eşik: sadece dolu balonlar
            if v >= profile[i-1][1] and v >= profile[i+1][1] and v >= profile[i-2][1] and v >= profile[i+2][1]:
                if not peaks or x - peaks[-1][0] > 25:
                    peaks.append((x, v))
                elif v > peaks[-1][1]:
                    peaks[-1] = (x, v)
    if peaks:
        print(f"  R{ri+1:02d}: {len(peaks)} peak → {[(x, round(v)) for x, v in peaks]}")

# ── 3) Satır 35 (indeks 34) profil: genellikle bos satır, form çizgileri görülebilir
# Satır 35'i zamanlama referans satiri olarak kullan (bos-ish)
print("\n── Row 35 (timing reference) ──")
ry35 = row_centers[34]
r35_clusters = []
profile = []
for x in range(20, width - 20, 2):
    d = sum(255 - get_gray(x, ry35 + dy) for dy in range(-6, 7)) / 13
    profile.append((x, d))
# Orta seviye peaks (>35, hem bos hem dolu balonlari yakalamak icin)
for i in range(2, len(profile) - 2):
    x, v = profile[i]
    if v > 35:
        if v >= profile[i-1][1] and v >= profile[i+1][1]:
            if not r35_clusters or x - r35_clusters[-1][0] > 20:
                r35_clusters.append((x, round(v)))
            elif v > r35_clusters[-1][1]:
                r35_clusters[-1] = (x, round(v))
print(f"  {len(r35_clusters)} peak bulundu")
for x, v in r35_clusters:
    print(f"    x={x}: {v}")

# ── 4) Bilinen alan haritalaması: Booklet (R37, C36-C42) & Cevaplar
# İlk 10 cevap satirini (R36-R45) tüm x ekseni boyunca tara
print("\n── R36-R45 cevap+booklet profil (>60 threshold) ──")
for ri in range(35, 45):
    ry = row_centers[ri]
    peaks = []
    profile = []
    for x in range(50, width - 50, 2):
        d = sum(255 - get_gray(x, ry + dy) for dy in range(-6, 7)) / 13
        profile.append((x, d))
    for i in range(2, len(profile) - 2):
        x, v = profile[i]
        if v > 60:
            if v >= profile[i-1][1] and v >= profile[i+1][1] and v >= profile[i-2][1] and v >= profile[i+2][1]:
                if not peaks or x - peaks[-1][0] > 25:
                    peaks.append((x, v))
                elif v > peaks[-1][1]:
                    peaks[-1] = (x, v)
    if peaks:
        print(f"  R{ri+1:02d}: {len(peaks)} peak → {[(x, round(v)) for x, v in peaks]}")

# ── 5) SINAV KODU + TARİH BÖLGESİ (R38-R60, tüm x)
print("\n── R38-R60 sinav kodu/tarih profil (>60 threshold) ──")
for ri in range(37, 60):
    ry = row_centers[ri]
    peaks = []
    profile = []
    for x in range(50, width - 50, 2):
        d = sum(255 - get_gray(x, ry + dy) for dy in range(-6, 7)) / 13
        profile.append((x, d))
    for i in range(2, len(profile) - 2):
        x, v = profile[i]
        if v > 60:
            if v >= profile[i-1][1] and v >= profile[i+1][1] and v >= profile[i-2][1] and v >= profile[i+2][1]:
                if not peaks or x - peaks[-1][0] > 25:
                    peaks.append((x, v))
                elif v > peaks[-1][1]:
                    peaks[-1] = (x, v)
    if peaks:
        # Timing strip (x>2350) haric
        non_timing = [(x, v) for x, v in peaks if x < 2350]
        if non_timing:
            print(f"  R{ri+1:02d}: {len(non_timing)} peak → {[(x, round(v)) for x, v in non_timing]}")

# ── 6) İsim/Soyisim (R2-R33, tüm x) – sadece en güçlü işaretler
print("\n── R2-R15 isim/soyisim (>90 threshold) ──")
for ri in range(1, 15):
    ry = row_centers[ri]
    peaks = []
    profile = []
    for x in range(50, width - 50, 2):
        d = sum(255 - get_gray(x, ry + dy) for dy in range(-6, 7)) / 13
        profile.append((x, d))
    for i in range(2, len(profile) - 2):
        x, v = profile[i]
        if v > 90:
            if v >= profile[i-1][1] and v >= profile[i+1][1] and v >= profile[i-2][1] and v >= profile[i+2][1]:
                if not peaks or x - peaks[-1][0] > 25:
                    peaks.append((x, v))
                elif v > peaks[-1][1]:
                    peaks[-1] = (x, v)
    if peaks:
        non_timing = [(x, v) for x, v in peaks if x < 2350]
        if non_timing:
            print(f"  R{ri+1:02d}: {len(non_timing)} peak → {[(x, round(v)) for x, v in non_timing]}")
