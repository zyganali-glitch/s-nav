"""
SIN ADAM PDF → grid kalibrasyon DOGRULAMA.
Cevap blogundan bilinen hucreleri kullanarak grid formulunu kur,
sonra tum alanlari dogrula.
"""

# ── KALIBRASYON: C(n) = 2340 - (n-1)*50 ──
# C1 = 2340 (sag kenar), C48= -12 (sol kenar ~ timing strip)
# Dogrulama: C30=888 (Q1=A @R36 x=888), C29=938 (Q2=B @R37 x=938)

def col_x(n):
    return 2340 - (n - 1) * 50

def x_to_col(x):
    return round((2340 - x) / 50 + 1)

print("=" * 70)
print("GRID KALİBRASYONU DOĞRULAMA")
print("=" * 70)

# Bilinen cevap isretleri
answers = [
    ("R36", "Q1=A", "C30", 888),
    ("R37", "Q2=B", "C29", 938),
    ("R38", "Q3=C", "C28", 986),
    ("R39", "Q4=D", "C27", 1036),
    ("R40", "Q5=E", "C26", 1086),
]
print("\nCEVAP DOĞRULAMA:")
for row, q, expected_col, obs_x in answers:
    calc_col = x_to_col(obs_x)
    calc_x = col_x(int(expected_col[1:]))
    print(f"  {row} {q}: x={obs_x} → C{calc_col} (beklenen {expected_col}, hesaplanan x={calc_x}, fark={obs_x-calc_x})")

# Kitapçık dogrulama
print("\nKİTAPÇIK DOĞRULAMA:")
book_x = 476
book_col = x_to_col(book_x)
print(f"  R37 Kitapçık: x={book_x} → C{book_col} (FMT pattern 'D C B A' at C36-C42: C38=C)")
print(f"  Beklenen: kitapçık C → C38, hesaplanan C38 x={col_x(38)}")

# İsim dogrulama
print("\nISIM DOĞRULAMA:")
print(f"  R24 x=988 → C{x_to_col(988)} (isim bölgesi C19-C28): S harfi C28'de olmalı, C28 x={col_x(28)}")
print(f"  R12 x=1052 → C{x_to_col(1052)} (isim): I harfi, beklenen C27 x={col_x(27)}")

# Öğrenci numarası 05367246543 dogrulama
print("\nÖĞRENCİ NUMARASI DOĞRULAMA (05367246543, C35-C45 reverse_columns=True):")
stnum = "05367246543"
marks_rn = {
    23: [(688, 'C34'), (752, 'C33'), (796, 'C32')],  # digit 0 → class digits
    24: [(844, 'C31')],  # digit 1 → class digit
    25: [(398, 'C39??')],
    26: [(248, 'C42??'), (630, 'C35??')],
    27: [(448, 'C38??'), (598, 'C35??')],
    28: [(190, 'C44??'), (554, 'C36??')],
    29: [(298, 'C41??'), (498, 'C37??')],
    30: [(342, 'C40??')],
}
for row, peaks in marks_rn.items():
    for obs_x, label in peaks:
        calc = x_to_col(obs_x)
        print(f"  R{row} x={obs_x} → C{calc} (digit {row-23})")

# Öğrenci numarası ile eşleştirme
print("\nÖĞRENCİ NO EŞLEŞME (reverse_columns=True, C45→C35):")
# С45→digit 0 → R23, C44→digit 5 → R28, C43→digit 3 → R26, ...
for pos, digit in enumerate(stnum):
    col_num = 45 - pos
    expected_row = 23 + int(digit)
    cx = col_x(col_num)
    print(f"  Digit '{digit}' @ C{col_num} (x≈{cx}) → R{expected_row}")

# ── SINAV KODU/TARİH ANALİZİ ──
print("\n" + "=" * 70)
print("SINAV KODU + TARİH KOORDİNAT ANALİZİ")
print("=" * 70)

# R44 (offset 0) marks: 148, 188, 238, 500, 746
# R45 (offset 1) marks: 288, 388, 442, 534, 584
# R53 (offset 9) marks: 636, 696

r44_marks = [148, 188, 238, 500, 746]
r45_marks = [288, 388, 442, 534, 584]
r53_marks = [636, 696]

print("\nR44 (offset 0) → digit 0 / harf A:")
for x in r44_marks:
    print(f"  x={x} → C{x_to_col(x)}")

print("\nR45 (offset 1) → digit 1:")
for x in r45_marks:
    print(f"  x={x} → C{x_to_col(x)}")

print("\nR53 (offset 9) → digit 9:")
for x in r53_marks:
    print(f"  x={x} → C{x_to_col(x)}")

# Sonuç: exam kodu A001, tarih 11/01/1990
print("\n── SONUÇ ──")
print(f"Satır aralığı: R44-R53 (10 satır, 0-9 digit)")
print(f"")
print(f"exam_code_prefix:  C45 (x≈{col_x(45)})  → MEVCUT TANIMDAKIYLE AYNI")
print(f"exam_code_number:  C42-C44 → MEVCUT TANIMDAKIYLE AYNI")
print(f"exam_date_day:     C39-C40 (x≈{col_x(40)}-{col_x(39)})  → ESKİ: C38-C39, 1 sütun kaydı!")
print(f"exam_date_month:   C37-C38 (x≈{col_x(38)}-{col_x(37)})  → ESKİ: C36-C37, 1 sütun kaydı!")
print(f"exam_date_year:    C33-C36 (x≈{col_x(36)}-{col_x(33)})  → ESKİ: C32-C35, 1 sütun kaydı!")
print(f"")
print(f"SATIR KAYDI: Mevcut tanım 46-55, doğru aralık 44-53  → 2 satır kayma!")

# ── MEVCUT vs DOĞRU KARŞILAŞTIRMA ──
print("\n── DEĞİŞİKLİKLER ──")
changes = [
    ("exam_code_prefix",  "start_row", 46, 44),
    ("exam_code_prefix",  "end_row",   55, 53),
    ("exam_code_number",  "start_row", 46, 44),
    ("exam_code_number",  "end_row",   55, 53),
    ("exam_date_day",     "start_row", 46, 44),
    ("exam_date_day",     "end_row",   55, 53),
    ("exam_date_day",     "start_col", 38, 39),
    ("exam_date_day",     "end_col",   39, 40),
    ("exam_date_month",   "start_row", 46, 44),
    ("exam_date_month",   "end_row",   55, 53),
    ("exam_date_month",   "start_col", 36, 37),
    ("exam_date_month",   "end_col",   37, 38),
    ("exam_date_year",    "start_row", 46, 44),
    ("exam_date_year",    "end_row",   55, 53),
    ("exam_date_year",    "start_col", 32, 33),
    ("exam_date_year",    "end_col",   35, 36),
]
for field, key, old, new in changes:
    if old != new:
        print(f"  {field}.{key}: {old} → {new}")
