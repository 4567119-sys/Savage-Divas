# Royal Square Financial demo

This workspace combines the three submitted pieces into one local demo:

- `Frontend/` — client self-service portal
- `Adviser Portal/` — adviser dashboard and case-review screens
- `AI Extractor/` — FastAPI document-extraction microservice and its test interface

## Open the browser demo

Double-click `Start Royal Square Demo.bat`. It starts a local web server and opens Chrome at `http://localhost:5173`.

Keep the command window open while presenting; closing it stops the local server.

## AI extraction service (optional)

The document extractor needs Python 3.10+ installed. From `AI Extractor/`, create a virtual environment, install requirements, then run:

```powershell
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

It will then be available at `http://localhost:8000`. Configure an optional Gemini key by copying `.env.example` to `.env` and adding your own key; do not commit that file.
