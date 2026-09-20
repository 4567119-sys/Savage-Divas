# Royal Square Financial — AI Document Extractor Module

> **Component:** AI & Document Processing Subsystem  
> **Team Role:** Person 3 (AI / Document Extraction Specialist)  
> **Project:** Royal Square Financial Claim Automation

A standalone, decoupled AI document extraction microservice designed to ingest police accident reports, dockets, and SAPS crash documentation (PDF, PNG, JPG, TXT), automatically extracting verified claim fields with confidence metrics and returning structured JSON.

---

## 🎯 Primary Goal & Extracted Fields

The module accepts accident/police report files and extracts:
- **Case Number** (e.g., `CAS 412/03/2024`, `AR-88219/2024`) with confidence score
- **Police Station** (e.g., `Sandton SAPS`, `Johannesburg Central`) with confidence score
- **Officer Name** (e.g., `Sgt. K. Sithole`, `Constable M. Dlamini`) with confidence score
- **Incident Date** (normalized to ISO `YYYY-MM-DD`, e.g. `2024-03-14`) with confidence score
- **Contextual Fields**: Incident time, location, vehicles involved (make/model, registration), damage summary, officer statement description, and confidence audit flags.

---

## 🏗️ Architecture

```
[Uploaded Document (PDF / Image)]
               │
               ▼
┌──────────────────────────────────────────────┐
│       1. Document Ingestion Pipeline         │
│  - Multi-format (PDF / PNG / JPG / TXT)      │
│  - Stream buffer handling                    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│     2. Dual-Engine Extraction Strategy       │
│  Primary: Multimodal Vision AI (Gemini Flash)│
│    - Handles handwriting, stamps, messy scans│
│  Fallback: Local Heuristic Text/OCR Engine   │
│    - Pattern parser with zero external cost  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│    3. Schema Enforcement & Confidence Meter  │
│  - Weighted confidence calculation           │
│  - Audit warning flags for missing fields    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│    4. Standalone Microservice Endpoints      │
│  - POST /api/extract (Multipart Form)        │
│  - Interactive Live Web Testing UI (/)       │
│  - Swagger Interactive API Docs (/docs)      │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Launch with run.bat (Windows)
Double-click `run.bat` or run in terminal:
```cmd
.\run.bat
```

### 2. Or Run with Python Virtual Environment
```powershell
# Activate venv
.\.venv\Scripts\activate

# Launch FastAPI server with live reload
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Live Interactive Playground**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Service Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Contract Schema**: [http://localhost:8000/api/schema](http://localhost:8000/api/schema)

---

## 🔑 AI Configuration (Optional Gemini Vision)

The module operates out-of-the-box using the local heuristic text extraction engine.

To enable **Multimodal Vision AI** (for handwriting, stamps, and photos):
1. Get a free API key at [Google AI Studio](https://aistudio.google.com/).
2. In `ai-extractor/.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

---

## 🧪 Automated Testing & Sample Documents

Run the automated test suite verifying PDF extraction and field accuracy:
```powershell
.\.venv\Scripts\python.exe tests/test_extraction.py
```

Sample test documents included in `tests/sample_reports/`:
- `saps_accident_report_1.pdf` (Sandton SAPS CAS docket)
- `saps_accident_report_2.pdf` (Johannesburg Central crash report)
- `saps_accident_report_1.png` (High-res document visual render)

---

## 📦 Connecting to Node.js / Express Backend

A ready-to-copy integration helper is available at `node_integration/client_example.js`.

### Example Controller in Express:
```javascript
const { extractPoliceReport } = require('./aiExtractor');

app.post('/api/claims/upload-report', upload.single('doc'), async (req, res) => {
  const result = await extractPoliceReport(req.file.path);
  
  const { caseNumber, policeStation, officerName, incidentDate } = result.coreFields;
  res.json({ caseNumber, policeStation, officerName, incidentDate, confidence: result.overallConfidence });
});
```

See [node_integration/README.md](file:///c:/Users/makha/Desktop/Savage-Divas/ai-extractor/node_integration/README.md) for full integration details.
