# Running the Application

This project is configured for **one-command execution** using standard Python.

## Quick Start (One Command)

From the project root directory, run:

```text
.venv\Scripts\python.exe app.py
```

Or, if your Python environment is already active:

```text
python app.py
```

This single command will:
1. Dynamically detect the project root and environment.
2. Launch the **FastAPI Backend** server at `http://127.0.0.1:8000`.
3. Launch the **React + Vite Frontend** development server at `http://localhost:5173`.
4. Automatically open the web application in your default browser.
5. Provide live logs in the terminal.

---

## Application Access Links

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **Backend API Server**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Stopping the Application

To cleanly stop both the backend and frontend servers:

Press **`Ctrl+C`** in the terminal window where `app.py` is running.

`app.py` automatically terminates all background worker processes cleanly upon exit.
