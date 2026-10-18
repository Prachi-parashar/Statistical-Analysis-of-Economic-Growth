import os
import re

ROOT_DIR = r"c:\Users\Harshit Tiwari\OneDrive\Desktop\Statistical Analysis of Economic Growth"

def audit():
    targets = ["1991", "1993", "2023", "2025", "31", "35"]
    
    matches = []

    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip node_modules, .git, venv, outputs, artifacts, scratch
        if any(skip in root for skip in ["node_modules", ".git", "venv", "dist", "scratch"]):
            continue
            
        for file in files:
            if not file.endswith((".py", ".jsx", ".js", ".json", ".md")):
                continue
                
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, ROOT_DIR)
            
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                for idx, line in enumerate(lines, 1):
                    for t in targets:
                        if t in line:
                            matches.append((rel_path, idx, t, line.strip()))

    print(f"Total target matches found across project: {len(matches)}\n")
    for rel_path, idx, t, text in matches:
        print(f"[{t}] {rel_path}:{idx} -> {text[:100]}")

if __name__ == "__main__":
    audit()
