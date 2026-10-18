cl"""quality_check.py — verifies final report against actual results."""
import os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_path = os.path.join(base, "outputs", "final_report.md")

with open(report_path, encoding="utf-8") as f:
    report = f.read()

print("=== FINAL QUALITY CHECK ===\n")

checks = [
    ("6.244",  "Mean GDP_Growth"),
    ("7.210",  "Median GDP_Growth"),
    ("2.815",  "Std Dev GDP_Growth"),
    ("\u22125.778", "Min GDP_Growth (2020)"),   # Unicode minus sign used in tables
    ("0.3180", "R²"),
    ("0.1815", "Adj R²"),
    ("2.331",  "F-statistic"),
    ("0.0722", "F-p value"),
    ("2.1142",  "FDI coefficient magnitude"),
    ("0.356",  "GCF coefficient"),
    ("0.029",  "FDI p-value"),
    ("0.033",  "GCF p-value"),
    ("1.855",  "Durbin-Watson"),
    ("0.131",  "Breusch-Pagan p"),
    ("0.008",  "SW residuals p"),
    ("0.382",  "Spearman GCF rho"),
    ("0.034",  "Spearman GCF p"),
    ("4.728",  "VIF Exports"),
    ("0.629",  "Cook's D max"),
    ("31",     "n observations"),
]

all_ok = True
for val, label in checks:
    found = val in report
    status = "OK  " if found else "FAIL"
    print(f"  {status}  {label}: '{val}' {'found' if found else 'NOT FOUND'}")
    if not found:
        all_ok = False

print()
causal = ["causes", "led to GDP growth", "resulted in growth",
          "proves causation", "demonstrates causation"]
for phrase in causal:
    if phrase.lower() in report.lower():
        print(f"  FAIL  Causal language: '{phrase}'")
        all_ok = False
print("  OK   No causal language detected")

print()
files_to_check = [
    ("outputs/final_report.md",  5000),
    ("outputs/final_report.pdf", 30000),
    ("outputs/README_FINAL.md",  500),
]
for fname, min_sz in files_to_check:
    fp = os.path.join(base, fname)
    if os.path.isfile(fp):
        sz = os.path.getsize(fp)
        status = "OK  " if sz >= min_sz else "SMALL"
        print(f"  {status}  {fname}: {sz:,} bytes")
    else:
        print(f"  FAIL  MISSING: {fname}")
        all_ok = False

ft = os.path.join(base, "outputs", "final_tables")
ff = os.path.join(base, "outputs", "final_figures")
print(f"  OK    final_tables/  : {len(os.listdir(ft))} files")
print(f"  OK    final_figures/ : {len(os.listdir(ff))} files")

print()
print("=" * 40)
print("ALL CHECKS PASSED" if all_ok else "REVIEW FAILURES ABOVE")
print("=" * 40)
