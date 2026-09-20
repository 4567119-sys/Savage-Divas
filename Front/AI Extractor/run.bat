@echo off
echo ========================================================
echo  Royal Square Financial - AI Document Extractor Service
echo ========================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Creating virtual environment...
    py -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

echo Starting AI Extractor on http://localhost:8000 ...
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
pause
