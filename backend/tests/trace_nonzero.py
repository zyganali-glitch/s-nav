"""Matriste sifir olmayan hucrelerin tam haritasini cikar."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.device_service import parse_mark_output_detailed

raw_path = ROOT / "backend" / "data" / "device-runtime" / "last-mark-read.txt"
raw = raw_path.read_text(encoding="utf-8")
sheets = parse_mark_output_detailed(raw)
matrix = sheets[0]["front_matrix"]
flipped = list(reversed(matrix))

THR = 12

print("=== HAM MATRIS (as_is) - Sifir olmayan hucreler ===")
for r, row in enumerate(matrix):
    for c, val in enumerate(row):
        if val > 0:
            label = f"R{r+1:02d}C{c+1:02d}={val:3d}"
            if val >= THR:
                label += " ***"
            print(label)

print(f"\n=== FLIP_VERTICAL - Esik ustu (>={THR}) hucreler ===")
for r, row in enumerate(flipped):
    for c, val in enumerate(row):
        if val >= THR:
            print(f"R{r+1:02d}C{c+1:02d}={val:3d}")

# Toplam isaret sayisi
total_nonzero = sum(1 for row in matrix for v in row if v > 0)
total_above = sum(1 for row in matrix for v in row if v >= THR)
print(f"\nToplam sifir-olmayan: {total_nonzero}, esik ustu: {total_above}")
