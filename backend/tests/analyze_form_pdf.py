"""
SIN ADAM formundaki isaretlenmis baloncuklari piksel analizi ile tespit et.
Form grid'ini zamanlama izleri (timing marks) kullanarak hizala
ve her hucredeki karalik oranini hesapla.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF gerekli: pip install PyMuPDF")
    sys.exit(1)

doc = fitz.open(str(ROOT / "örnek" / "SIN ADAM.pdf"))
page = doc[0]
pix = page.get_pixmap(dpi=300)
width, height = pix.width, pix.height
print(f"Gorsel: {width}x{height} piksel")

# Grayscale donusumu
samples = pix.samples  # RGB bytes
stride = pix.stride
n = pix.n  # channels per pixel

def get_gray(x: int, y: int) -> int:
    """0-255, 0=siyah, 255=beyaz"""
    if x < 0 or x >= width or y < 0 or y >= height:
        return 255
    offset = y * stride + x * n
    r, g, b = samples[offset], samples[offset + 1], samples[offset + 2]
    return (r + g + b) // 3


# --- ADIM 1: Zamanlama izlerini bul ---
# Formda sag kenar zamanlama seridine sahip (C48 = en soldaki fiziksel sutun aslinda)
# Usteki ve soldaki zamanlama izlerini tespit edelim

# Dikey zamanlama izi: en sag veya en sol sutunda duzgun aralikli koyu noktalar
# Yatay tarama: en karanlik dikey serit
print("\n--- Dikey zamanlama seridi tespiti ---")
# Her x icin ortalama karanlik
col_darkness = []
for x in range(width):
    total = 0
    sample_count = 0
    for y in range(0, height, 10):  # her 10 pikselde ornekle
        total += (255 - get_gray(x, y))
        sample_count += 1
    col_darkness.append(total / sample_count if sample_count else 0)

# En karanlik x bolgeleri
sorted_cols = sorted(range(width), key=lambda x: -col_darkness[x])
print(f"En karanlik x pozisyonlari: {sorted_cols[:20]}")

# Sag kenardaki zamanlama seridi (genellikle formun en sag kenari)
right_timing_x = None
for x in range(width - 1, width - 100, -1):
    if col_darkness[x] > 30:  # karanlik esigi
        right_timing_x = x
        break

# Sol kenardaki timing (eger varsa)
left_timing_x = None
for x in range(0, 100):
    if col_darkness[x] > 30:
        left_timing_x = x
        break

print(f"Sol zamanlama x: {left_timing_x}, Sag zamanlama x: {right_timing_x}")

# --- ADIM 2: Yatay zamanlama izlerini bul ---
print("\n--- Yatay zamanlama seridi tespiti ---")
row_darkness = []
for y in range(height):
    total = 0
    sample_count = 0
    for x in range(0, width, 10):
        total += (255 - get_gray(x, y))
        sample_count += 1
    row_darkness.append(total / sample_count if sample_count else 0)

# En karanlik y pozisyonlari  
sorted_rows = sorted(range(height), key=lambda y: -row_darkness[y])
print(f"En karanlik y pozisyonlari: {sorted_rows[:20]}")

# --- ADIM 3: Grid cozunurlugunu hesapla ---
# 65 satir x 48 sutun grid
# Grid baslangic ve bitis koordinatlari

# Sag kenardaki zamanlama seridindeki isaret merkezlerini bul
# Her satirin y koordinatini tespit et
print("\n--- Satir merkezleri (sag zamanlama seridinden) ---")
if right_timing_x:
    # Sag timing seridinde dikey profil
    timing_profile = []
    for y in range(height):
        # timing x etrafinda 10px genislikte ornekle
        darkness = 0
        cnt = 0
        for dx in range(-5, 6):
            xx = right_timing_x + dx
            if 0 <= xx < width:
                darkness += (255 - get_gray(xx, y))
                cnt += 1
        timing_profile.append(darkness / cnt if cnt else 0)
    
    # Koyu bolgelerin merkezlerini bul (isaretler)
    in_mark = False
    mark_start = 0
    mark_centers = []
    MARK_THRESHOLD = 40
    
    for y in range(height):
        if timing_profile[y] > MARK_THRESHOLD:
            if not in_mark:
                mark_start = y
                in_mark = True
        else:
            if in_mark:
                center = (mark_start + y) // 2
                mark_centers.append(center)
                in_mark = False
    if in_mark:
        mark_centers.append((mark_start + height) // 2)
    
    print(f"Zamanlama isareti sayisi: {len(mark_centers)} (beklenen: 65)")
    if len(mark_centers) >= 10:
        print(f"Ilk 5 merkez y: {mark_centers[:5]}")
        print(f"Son 5 merkez y: {mark_centers[-5:]}")
        if len(mark_centers) >= 2:
            spacing = (mark_centers[-1] - mark_centers[0]) / (len(mark_centers) - 1)
            print(f"Ortalama satir araligi: {spacing:.1f} piksel")

# Ust kenardaki zamanlama seridinden sutun merkezlerini bul
print("\n--- Sutun merkezleri (ust zamanlama seridinden) ---")

# Ustteki zamanlama satirinin y konumunu bul
top_timing_y = None
for y in range(0, 100):
    if row_darkness[y] > 20:
        top_timing_y = y
        break

if top_timing_y is not None:
    # Ustteki zamanlama satirinda yatay profil
    top_profile = []
    for x in range(width):
        darkness = 0
        cnt = 0
        for dy in range(-5, 6):
            yy = top_timing_y + dy
            if 0 <= yy < height:
                darkness += (255 - get_gray(x, yy))
                cnt += 1
        top_profile.append(darkness / cnt if cnt else 0)
    
    in_mark = False
    mark_start = 0
    col_centers = []
    
    for x in range(width):
        if top_profile[x] > MARK_THRESHOLD:
            if not in_mark:
                mark_start = x
                in_mark = True
        else:
            if in_mark:
                center = (mark_start + x) // 2
                col_centers.append(center)
                in_mark = False
    if in_mark:
        col_centers.append((mark_start + width) // 2)
    
    print(f"Zamanlama sutun sayisi: {len(col_centers)} (beklenen: 48)")
    if len(col_centers) >= 10:
        print(f"Ilk 5 sutun merkez x: {col_centers[:5]}")
        print(f"Son 5 sutun merkez x: {col_centers[-5:]}")

# --- ADIM 4: Her hucredeki karanlik degerini hesapla ve isaret haritasi cikar ---
if len(mark_centers) >= 60 and len(col_centers) >= 40:
    print(f"\n--- FORM MATRISI ({len(mark_centers)} satir x {len(col_centers)} sutun) ---")
    
    # Her hucre icin karanlik degerini hesapla
    CELL_RADIUS = 8  # piksel
    FILL_THRESHOLD = 80  # dolu balon esigi
    
    filled_cells = []
    for ri, ry in enumerate(mark_centers):
        for ci, cx in enumerate(col_centers):
            # Hucre merkezinde CELL_RADIUS cercevesinde ortalama karanlik
            total = 0
            cnt = 0
            for dy in range(-CELL_RADIUS, CELL_RADIUS + 1, 2):
                for dx in range(-CELL_RADIUS, CELL_RADIUS + 1, 2):
                    total += (255 - get_gray(cx + dx, ry + dy))
                    cnt += 1
            avg_darkness = total / cnt if cnt else 0
            if avg_darkness > FILL_THRESHOLD:
                filled_cells.append((ri + 1, ci + 1, round(avg_darkness)))
    
    print(f"Dolu hucre sayisi: {len(filled_cells)}")
    print("\nDolu hucreler (Satir, Sutun, Karanlik):")
    for r, c, d in filled_cells:
        print(f"  R{r:02d}C{c:02d} = {d}")
    
    # Ozellikle sinav kodu ve tarih bolgesi (rows 38-60, cols 30-48)
    print("\n--- SINAV KODU / TARIH BOLGESI (Satir 38-60) ---")
    for r, c, d in filled_cells:
        if 38 <= r <= 60:
            print(f"  R{r:02d}C{c:02d} = {d}")
    
    # Sinif bolgesi (rows 23-32, cols 31-34)
    print("\n--- SINIF BOLGESI ---")
    for r, c, d in filled_cells:
        if 23 <= r <= 32 and 31 <= c <= 34:
            print(f"  R{r:02d}C{c:02d} = {d}")
    
    # Ogrenci numarasi bolgesi (rows 23-32, cols 35-45)
    print("\n--- OGRENCI NUMARASI ---")
    for r, c, d in filled_cells:
        if 23 <= r <= 32 and 35 <= c <= 45:
            print(f"  R{r:02d}C{c:02d} = {d}")

else:
    print(f"\nYetersiz zamanlama isareti! Satir={len(mark_centers)}, Sutun={len(col_centers)}")
    print("Manuel analiz gerekli.")
