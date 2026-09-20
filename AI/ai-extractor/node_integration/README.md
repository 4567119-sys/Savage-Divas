# Express.js Integration Guide for Backend Teammates

This guide explains how **Person 1, 2, or 4** can connect the Node.js/Express backend to the AI Document Extractor module built by Person 3.

---

## 1. Quick Start

Ensure the AI Extractor service is running (by default on `http://localhost:8000`).

In your Node.js project:

```bash
npm install axios form-data
```

Copy `client_example.js` into your backend project (e.g. `src/services/aiExtractor.js`).

---

## 2. Express Route Example with Multer

Here is an example Express endpoint where an insurance claimant or officer uploads a police report:

```javascript
const express = require('express');
const multer = require('multer');
const { extractPoliceReport } = require('./services/aiExtractor');

const router = express.Router();
const upload = multer({ dest: 'uploads/' });

// POST /api/claims/extract-report
router.post('/extract-report', upload.single('document'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No document file uploaded' });
    }

    // Call the AI Extraction service
    const extraction = await extractPoliceReport(req.file.path, req.file.originalname);

    // Access the core requested fields:
    const { caseNumber, policeStation, officerName, incidentDate } = extraction.coreFields;

    res.json({
      success: true,
      claimSummary: {
        caseNumber,
        policeStation,
        officerName,
        incidentDate,
        confidence: extraction.overallConfidence,
      },
      details: extraction.additionalFields,
      warnings: extraction.warnings,
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to process document', message: err.message });
  }
});

module.exports = router;
```

---

## 3. Environment Variable

In your Node.js `.env`:

```env
AI_EXTRACTOR_URL=http://localhost:8000
```
