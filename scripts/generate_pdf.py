"""
generate_pdf.py
---------------
Converts Markdown report to PDF using the dynamic ReportLab engine.
"""

import os
import sys
from pathlib import Path

# Add backend to sys.path so we can import services
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services import report_generator, analysis_pipeline_service

def main():
    print("Running dynamic PDF generation...")
    res = analysis_pipeline_service.run_analysis_pipeline(force_refresh=False)
    if res.get("success"):
        print(f"Successfully generated dynamic reports for run: {res.get('analysis_id')}")
        print(f"PDF Output: {PROJECT_ROOT / 'outputs' / 'final_report.pdf'}")
        print(f"Markdown Output: {PROJECT_ROOT / 'outputs' / 'final_report.md'}")
    else:
        print(f"Error running pipeline: {res.get('error')}")

if __name__ == "__main__":
    main()
