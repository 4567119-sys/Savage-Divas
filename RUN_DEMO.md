# Savage Divas — Integrated Demo

## Run the whole application

1. Open a terminal in this folder.
2. Create/activate a Python virtual environment (optional but recommended):

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open **http://127.0.0.1:8000/** in the browser.

The frontend is now served by the FastAPI application. The API is available under `/api/v1` and the Swagger documentation is at `/api/v1/docs`.

## Demo flow for the video

1. Sign in with the demo South African ID shown on the login screen.
2. Choose **Report an accident**.
3. Enter the incident details.
4. Upload/select supporting documents.
5. Review the extracted police information.
6. Submit the claim.
7. Show the confirmation/status screen.
8. Optional: open `/api/v1/docs` to demonstrate the backend API.

The submit flow creates a real client record (or reuses the demo client), creates a case in SQLite, uploads document metadata/files, sends an AI-ingestion result to the workflow engine, and retrieves the resulting case progress.

## Notes

- The AI integration currently uses the backend's ingestion/workflow contract for the demo. It does not claim to be a live Gemini extraction service unless that service is separately configured.
- Uploaded files are stored in `uploads/`.
- `.env` contains no API key by default. Do not commit real secrets.
