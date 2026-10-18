import sys
import subprocess
import os

def test_app_syntax():
    print("Testing app.py compilation and import...")
    res = subprocess.run([sys.executable, "-c", "import app; print('app.py imported successfully!')"],
                         cwd=r"c:\Users\Harshit Tiwari\OneDrive\Desktop\Statistical Analysis of Economic Growth",
                         capture_output=True, text=True)
    print("STDOUT:", res.stdout.strip())
    print("STDERR:", res.stderr.strip())
    assert res.returncode == 0, "app.py failed syntax/import test!"
    print("✓ app.py syntax and import verified.")

if __name__ == "__main__":
    test_app_syntax()
