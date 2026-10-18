import os
import re

ROOT_DIR = r"c:\Users\Harshit Tiwari\OneDrive\Desktop\Statistical Analysis of Economic Growth"

def audit():
    targets = ["1991", "1993", "2023", "2025", "31", "35"]
    matches = []

    for sub in ["backend", "frontend"]:
        target_dir = os.path.join(ROOT_DIR, sub)
        for root, dirs, files in os.walk(target_dir):
            if "node_modules" in root or "dist" in root:
                continue
            for file in files:
                if not file.endswith((".py", ".jsx", ".js", ".json")):
                    continue
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, ROOT_DIR)
                
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        for t in targets:
                            # regex word boundary to find hardcoded year numbers/n values
                            if re.search(r'\b' + re.escape(t) + r'\b', line):
                                matches.append((rel_path, idx, t, line.strip()))

    print(f"Total target matches found in code: {len(matches)}\n")
    for rel_path, idx, t, text in sorted(matches, key=lambda x: x[0]):
        # Encode printable ascii only to avoid cp1252 print errors
        clean_text = text.encode("ascii", "replace").decode()
        print(f"[{t}] {rel_path}:{idx} -> {clean_text[:120]}")

if __name__ == "__main__":
    audit()
