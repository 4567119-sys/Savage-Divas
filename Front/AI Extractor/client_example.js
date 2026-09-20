/**
 * Royal Square Financial — AI Document Extractor
 * Node.js / Express Backend Integration Helper
 *
 * This client helper allows your Node.js/Express backend to communicate
 * with the AI Document Extractor microservice via HTTP multipart upload.
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const AI_EXTRACTOR_URL = process.env.AI_EXTRACTOR_URL || 'http://localhost:8000';

/**
 * Sends an uploaded police or accident report document (PDF, PNG, JPG)
 * to the AI Document Extraction service.
 *
 * @param {string|Buffer} fileInput - Absolute file path string OR a Buffer with a filename
 * @param {string} [originalFilename='document.pdf'] - Filename for buffer uploads
 * @param {string} [engine='auto'] - 'auto', 'gemini', or 'local'
 * @returns {Promise<Object>} Structured extraction response with confidence scores
 */
async function extractPoliceReport(fileInput, originalFilename = 'document.pdf', engine = 'auto') {
  const form = new FormData();

  if (typeof fileInput === 'string') {
    if (!fs.existsSync(fileInput)) {
      throw new Error(`Document file not found at path: ${fileInput}`);
    }
    form.append('file', fs.createReadStream(fileInput));
  } else if (Buffer.isBuffer(fileInput)) {
    form.append('file', fileInput, { filename: originalFilename });
  } else {
    throw new Error('Invalid file input: must be a file path string or Buffer.');
  }

  form.append('engine', engine);

  try {
    const response = await axios.post(`${AI_EXTRACTOR_URL}/api/extract`, form, {
      headers: {
        ...form.getHeaders(),
      },
      maxContentLength: 50 * 1024 * 1024, // 50MB
      timeout: 45000,
    });

    const result = response.data;
    const { data, overall_confidence, warnings } = result;

    // Destructure core fields requested for Royal Square Financial claims:
    const caseNumber = data.case_number?.value;         // e.g. "CAS 412/03/2024"
    const policeStation = data.police_station?.value;   // e.g. "Sandton SAPS"
    const officerName = data.officer_name?.value;       // e.g. "Sgt. K. Sithole"
    const incidentDate = data.incident_date?.value;     // e.g. "2024-03-14"

    return {
      success: true,
      overallConfidence: overall_confidence,
      coreFields: {
        caseNumber,
        caseConfidence: data.case_number?.confidence || 0,
        policeStation,
        stationConfidence: data.police_station?.confidence || 0,
        officerName,
        officerConfidence: data.officer_name?.confidence || 0,
        incidentDate,
        dateConfidence: data.incident_date?.confidence || 0,
      },
      additionalFields: {
        incidentTime: data.incident_time?.value,
        incidentLocation: data.incident_location?.value,
        damagesSummary: data.damages_summary?.value,
        description: data.incident_description?.value,
        vehiclesInvolved: data.vehicles_involved || [],
      },
      warnings,
      rawResponse: result,
    };
  } catch (error) {
    console.error('[AI Extractor] Error during document extraction:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Checks if the AI Extractor service is healthy and available.
 */
async function checkExtractorHealth() {
  try {
    const response = await axios.get(`${AI_EXTRACTOR_URL}/api/health`, { timeout: 5000 });
    return response.data;
  } catch (error) {
    return { status: 'offline', error: error.message };
  }
}

module.exports = {
  extractPoliceReport,
  checkExtractorHealth,
  AI_EXTRACTOR_URL,
};
