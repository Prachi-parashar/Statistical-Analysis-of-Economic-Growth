import os
import re

FRONTEND_DIR = r"c:\Users\Harshit Tiwari\OneDrive\Desktop\Statistical Analysis of Economic Growth\frontend\src"

def search_files():
    patterns = [
        r"correlationMatrix",
        r"matrixMap",
        r"0\.45",
        r"-0\.32",
        r"0\.67",
        r"0\.19",
        r"0\.318",
        r"\[1,\s*0,\s*0",
        r"\[\s*1\.0\s*,\s*0\s*,",
    ]

    found = []
    for root, dirs, files in os.walk(FRONTEND_DIR):
        for file in files:
            if file.endswith(".jsx") or file.endswith(".js"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for pat in patterns:
                        matches = re.finditer(pat, content)
                        for m in matches:
                            # get line number
                            line_no = content[:m.start()].count('\n') + 1
                            found.append((file, line_no, pat, content[max(0, m.start()-30):min(len(content), m.end()+30)].replace('\n', ' ')))

    print(f"Found {len(found)} pattern matches in frontend:")
    for f, line, pat, snippet in found:
        print(f"  File: {f}:{line} | Pattern: '{pat}' | Snippet: ...{snippet}...")

if __name__ == "__main__":
    search_files()
