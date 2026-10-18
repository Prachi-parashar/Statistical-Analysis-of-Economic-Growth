"""
app.py - Single project runner for "Statistical Analysis of Economic Growth"

Executes both FastAPI Backend (http://127.0.0.1:8000) and Vite Frontend (http://localhost:5173)
in a single terminal session. Handles Ctrl+C gracefully to stop all processes cleanly.
No PowerShell or external shell scripts required.
"""

import sys
import os
import time
import socket
import signal
import shutil
import threading
import subprocess
import webbrowser
from pathlib import Path

# Dynamically determine project root
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
VENV_DIR = PROJECT_ROOT / ".venv"

# Determine Python and NPM executables
if os.name == 'nt':
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
    NPM_CMD = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"
    NPM_CMD = shutil.which("npm") or "npm"

PYTHON_EXEC = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a network port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def check_environment():
    """Verify prerequisites before launching servers."""
    if not BACKEND_DIR.exists():
        print("ERROR: backend/ directory not found.")
        sys.exit(1)

    if not FRONTEND_DIR.exists():
        print("ERROR: frontend/ directory not found.")
        sys.exit(1)

    # Check for frontend node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("\n" + "=" * 60)
        print("ERROR: frontend/node_modules is missing.")
        print("Please install frontend dependencies first:")
        print("  cd frontend")
        print("  npm install")
        print("  cd ..")
        print("=" * 60 + "\n")
        sys.exit(1)

    # Check port availability
    if is_port_in_use(8000):
        print("\n" + "=" * 60)
        print("ERROR: Port 8000 is already in use (Backend target port).")
        print("Please close any process using port 8000 before running app.py.")
        print("=" * 60 + "\n")
        sys.exit(1)

    if is_port_in_use(5173):
        print("\n" + "=" * 60)
        print("ERROR: Port 5173 is already in use (Frontend target port).")
        print("Please close any process using port 5173 before running app.py.")
        print("=" * 60 + "\n")
        sys.exit(1)


def open_browser_delayed(url: str, delay: float = 2.5):
    """Open the application in the default web browser after a short delay."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def kill_process_tree(pid: int):
    """Cleanly terminate a process and its child subprocesses."""
    try:
        if os.name == 'nt':
            subprocess.call(
                ['taskkill', '/F', '/T', '/PID', str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


def main():
    check_environment()

    print("==================================================")
    print(" Statistical Analysis of Economic Growth")
    print(" Single Application Launcher")
    print("==================================================")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python:       {PYTHON_EXEC}")
    print("")

    # Start backend
    print("Starting backend server...")
    print("Backend:  http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("")

    backend_cmd = [PYTHON_EXEC, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(BACKEND_DIR),
            stdout=None,
            stderr=None
        )
    except Exception as e:
        print(f"ERROR: Failed to start backend: {e}")
        print("Ensure dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

    # Start frontend
    print("Starting frontend server...")
    print("Frontend: http://localhost:5173")
    print("")

    frontend_cmd = [NPM_CMD, "run", "dev"]
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=str(FRONTEND_DIR),
            stdout=None,
            stderr=None
        )
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {e}")
        if backend_process and backend_process.poll() is None:
            kill_process_tree(backend_process.pid)
        sys.exit(1)

    print("==================================================")
    print(" Application running successfully!")
    print(" Open in browser: http://localhost:5173")
    print(" Press Ctrl+C in this terminal to stop.")
    print("==================================================")
    print("")

    # Auto-open browser
    threading.Thread(target=open_browser_delayed, args=("http://localhost:5173", 2.0), daemon=True).start()

    cleaning_up = False

    def cleanup(signum=None, frame=None):
        nonlocal cleaning_up
        if cleaning_up:
            return
        cleaning_up = True

        print("\nStopping application...")

        print("Stopping frontend...")
        if frontend_process and frontend_process.poll() is None:
            kill_process_tree(frontend_process.pid)

        print("Stopping backend...")
        if backend_process and backend_process.poll() is None:
            kill_process_tree(backend_process.pid)

        print("Application stopped.")
        sys.exit(0)

    # Signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            b_code = backend_process.poll()
            f_code = frontend_process.poll()
            if b_code is not None or f_code is not None:
                cleanup()
            time.sleep(0.5)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
