document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const fileBanner = document.getElementById("fileBanner");
  const fileName = document.getElementById("fileName");
  const fileSize = document.getElementById("fileSize");
  const clearFileBtn = document.getElementById("clearFileBtn");
  const engineSelect = document.getElementById("engineSelect");
  const extractBtn = document.getElementById("extractBtn");
  const serviceStatus = document.getElementById("serviceStatus");
  const statusText = document.getElementById("statusText");

  // Sample Buttons
  const sample1Btn = document.getElementById("sample1Btn");
  const sample2Btn = document.getElementById("sample2Btn");
  const sample3Btn = document.getElementById("sample3Btn");

  // Royal Square Insurance Triage Elements
  const insuranceCategoryValue = document.getElementById("insuranceCategoryValue");
  const policyValue = document.getElementById("policyValue");
  const claimTypeValue = document.getElementById("claimTypeValue");

  // Views & States
  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const dashboardView = document.getElementById("dashboardView");
  const jsonView = document.getElementById("jsonView");
  const integrationView = document.getElementById("integrationView");

  // Tabs
  const tabSummary = document.getElementById("tabSummary");
  const tabJson = document.getElementById("tabJson");
  const tabIntegration = document.getElementById("tabIntegration");

  // Dashboard Fields
  const confidenceGauge = document.getElementById("confidenceGauge");
  const overallScore = document.getElementById("overallScore");

  const caseValue = document.getElementById("caseValue");
  const caseConf = document.getElementById("caseConf");
  const caseSource = document.getElementById("caseSource");

  const stationValue = document.getElementById("stationValue");
  const stationConf = document.getElementById("stationConf");
  const stationSource = document.getElementById("stationSource");

  const officerValue = document.getElementById("officerValue");
  const officerConf = document.getElementById("officerConf");
  const officerSource = document.getElementById("officerSource");

  const dateValue = document.getElementById("dateValue");
  const dateConf = document.getElementById("dateConf");
  const dateSource = document.getElementById("dateSource");

  const timeLocValue = document.getElementById("timeLocValue");
  const vehiclesValue = document.getElementById("vehiclesValue");
  const damagesValue = document.getElementById("damagesValue");
  const descValue = document.getElementById("descValue");

  const warningsBox = document.getElementById("warningsBox");
  const warningsList = document.getElementById("warningsList");

  const metaEngine = document.getElementById("metaEngine");
  const metaTime = document.getElementById("metaTime");
  const metaPages = document.getElementById("metaPages");

  const jsonContent = document.getElementById("jsonContent");
  const integrationCode = document.getElementById("integrationCode");
  const copyJsonBtn = document.getElementById("copyJsonBtn");
  const copyCodeBtn = document.getElementById("copyCodeBtn");
  const toast = document.getElementById("toast");

  let currentFile = null;
  let lastResponse = null;

  // 1. Check Service Health
  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        const data = await res.json();
        statusText.textContent = data.gemini_configured
          ? `Online (Gemini ${data.gemini_model})`
          : "Online (Local OCR Mode)";
        serviceStatus.classList.remove("error");
        serviceStatus.classList.add("online");
      } else {
        throw new Error();
      }
    } catch {
      statusText.textContent = "Service Offline";
      serviceStatus.classList.remove("online");
      serviceStatus.classList.add("error");
    }
  }
  checkHealth();

  // 2. Drag & Drop Handlers
  dropzone.addEventListener("click", () => fileInput.click());
  browseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    if (dt.files && dt.files.length > 0) {
      setFile(dt.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  });

  clearFileBtn.addEventListener("click", () => {
    currentFile = null;
    fileInput.value = "";
    fileBanner.classList.add("hidden");
    dropzone.classList.remove("hidden");
    extractBtn.disabled = true;
  });

  function setFile(file) {
    currentFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    fileBanner.classList.remove("hidden");
    dropzone.classList.add("hidden");
    extractBtn.disabled = false;
  }

  // 3. Quick Test Fixtures
  sample1Btn.addEventListener("click", () => {
    const sampleText = `================================================================================
SOUTH AFRICAN POLICE SERVICE (SAPS) - ACCIDENT REPORT DOCKET
================================================================================
STATION: Sandton SAPS
CAS NO: 412/03/2024
OAR REF NO: AR-88219/2024
INVESTIGATING OFFICER: Sgt. K. Sithole (Force No: 7041928-1)
TELEPHONE: (011) 722-7000

SECTION A: INCIDENT PARTICULARS
--------------------------------------------------------------------------------
DATE OF ACCIDENT: 14/03/2024
TIME OF ACCIDENT: 14h30
ACCIDENT SCENE / LOCATION: Corner Rivonia Road and 5th Street, Sandton, Gauteng
WEATHER CONDITIONS: Clear, Dry Road Surface

SECTION B: VEHICLES INVOLVED
--------------------------------------------------------------------------------
VEHICLE 1:
  Make & Model: Toyota Hilux 2.8 GD-6
  Registration No: CA 123-456 GP
  Driver: Mr. Sipho Nkosi (ID: 880412 5123 088)

VEHICLE 2:
  Make & Model: Volkswagen Polo TSI
  Registration No: ND 987-654 GP
  Driver: Ms. Jane Van Der Merwe (ID: 920719 0045 081)

SECTION C: ACCIDENT DESCRIPTION / OFFICER STATEMENT
--------------------------------------------------------------------------------
BRIEF DESCRIPTION:
Vehicle 1 was travelling south along Rivonia Road when Vehicle 2 executed a right turn
at the intersection into 5th Street against oncoming traffic. Vehicle 1 was unable to
stop in time and collided with the side of Vehicle 2. No critical injuries reported.
DAMAGE TO VEHICLE: Heavy front bumper and radiator damage to Toyota Hilux. Side panel damage to Polo.`;
    const blob = new Blob([sampleText], { type: "text/plain" });
    const file = new File([blob], "saps_sandton_accident_docket.txt", { type: "text/plain" });
    setFile(file);
    triggerExtraction();
  });

  sample2Btn.addEventListener("click", () => {
    const sampleText = `================================================================================
POLICE ACCIDENT & CRASH INVESTIGATION REPORT
================================================================================
POLICE STATION: Johannesburg Central
CAS NUMBER: CAS 89/11/2023
OB NUMBER: OB 441/2023
REPORTING OFFICER: Constable M. Dlamini
BADGE NO: 88412

INCIDENT INFORMATION:
--------------------------------------------------------------------------------
INCIDENT DATE: 2023-11-20
TIME: 08:45 AM
LOCATION: Corner Eloff & Marshall Street, Johannesburg CBD

DETAILS OF INCIDENT:
--------------------------------------------------------------------------------
DESCRIPTION OF ACCIDENT:
Ford Ranger collided with rear end of Nissan NP200 at traffic signal.
The Nissan had come to a stationary stop at the red light when the Ford failed
to maintain safe following distance due to wet road conditions.

VEHICLE & DAMAGE ASSESSMENT:
--------------------------------------------------------------------------------
Vehicle A: Ford Ranger (Reg: BB 22 CC GP)
Vehicle B: Nissan NP200 (Reg: DZ 44 KL GP)
DAMAGES TO VEHICLE: Crumpled rear tailgate, shattered left tail light assembly.`;
    const blob = new Blob([sampleText], { type: "text/plain" });
    const file = new File([blob], "jhb_central_crash_report.txt", { type: "text/plain" });
    setFile(file);
    triggerExtraction();
  });

  sample3Btn.addEventListener("click", () => {
    const sampleText = `================================================================================
SOUTH AFRICAN POLICE SERVICE (SAPS) - COMMERCIAL ACCIDENT REPORT
================================================================================
STATION: Midrand SAPS
CAS NO: 512/08/2024
COMMERCIAL DOCKET REF: RSF-FLEET-9941
INSURANCE PROVIDER: Royal Square Financial - Commercial Insurance Division
POLICY NUMBER: POL-COM-448102

SECTION A: INCIDENT PARTICULARS
--------------------------------------------------------------------------------
DATE OF ACCIDENT: 2024-08-18
TIME OF ACCIDENT: 11h15
ACCIDENT LOCATION: Allandale Road near K101 Intersection, Midrand
WEATHER: Clear, Dry

SECTION B: COMMERCIAL VEHICLE PARTICULARS
--------------------------------------------------------------------------------
VEHICLE 1 (Commercial Fleet):
  Company / Fleet Owner: Express Cargo Logistics Pty Ltd
  Make & Model: Isuzu NPR 400 Freight Truck (4-Ton)
  Registration No: GP 55 TT GP
  Driver: Mr. Thabo Mokoena (PrDP Code 14 Heavy Vehicle License)
  Royal Square Financial Commercial Policy: POL-COM-448102

VEHICLE 2:
  Make & Model: BMW 320i
  Registration No: JX 88 YZ GP
  Driver: Mr. David Miller

SECTION C: ACCIDENT SUMMARY & OFFICER STATEMENT
--------------------------------------------------------------------------------
BRIEF DESCRIPTION:
Vehicle 1 (Isuzu commercial freight truck) was turning into logistics depot when
Vehicle 2 attempted an illegal overtake on the left shoulder and made contact
with the commercial truck's passenger step and cargo chassis. No driver casualties.
DAMAGES TO VEHICLE: Passenger side diesel tank guard scraped on truck; front bumper torn off on BMW.

INVESTIGATING OFFICER: Warrant Officer P. Ndlovu (Force No: 441092-8)
SIGNATURE: W/O P. NDLOVU
STAMP: MIDRAND SAPS - OFFICIAL DISPATCH 2024-08-18`;
    const blob = new Blob([sampleText], { type: "text/plain" });
    const file = new File([blob], "rsf_commercial_fleet_docket.txt", { type: "text/plain" });
    setFile(file);
    triggerExtraction();
  });

  // 4. Trigger Extraction
  extractBtn.addEventListener("click", triggerExtraction);

  async function triggerExtraction() {
    if (!currentFile) return;

    // Show loading
    emptyState.classList.add("hidden");
    dashboardView.classList.add("hidden");
    jsonView.classList.add("hidden");
    integrationView.classList.add("hidden");
    loadingState.classList.remove("hidden");
    extractBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", currentFile);
    formData.append("engine", engineSelect.value);

    try {
      const res = await fetch("/api/extract", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || err.error || "Failed to extract document");
      }

      const data = await res.json();
      lastResponse = data;
      renderResults(data);
    } catch (err) {
      alert(`Extraction Error: ${err.message}`);
      emptyState.classList.remove("hidden");
    } finally {
      loadingState.classList.add("hidden");
      extractBtn.disabled = false;
    }
  }

  // 5. Render Extraction Dashboard
  function renderResults(res) {
    const d = res.data;
    const m = res.metadata;

    // Confidence gauge
    const pct = Math.round((res.overall_confidence || 0) * 100);
    overallScore.textContent = `${pct}%`;
    confidenceGauge.classList.remove("hidden");

    // Case Number
    renderField(caseValue, caseConf, caseSource, d.case_number);
    // Police Station
    renderField(stationValue, stationConf, stationSource, d.police_station);
    // Officer Name
    renderField(officerValue, officerConf, officerSource, d.officer_name);
    // Incident Date
    renderField(dateValue, dateConf, dateSource, d.incident_date);

    // Royal Square Insurance Triage
    if (insuranceCategoryValue) {
      insuranceCategoryValue.textContent = d.insurance_category?.value || "Personal Insurance (Motor)";
    }
    if (policyValue) {
      policyValue.textContent = d.policy_number?.value || "Pending Policy Verification";
    }
    if (claimTypeValue) {
      claimTypeValue.textContent = d.claim_type?.value || "Standard Collision Assessment";
    }

    // Secondary Details
    const timeVal = d.incident_time?.value || "Not specified";
    const locVal = d.incident_location?.value || "Not specified";
    timeLocValue.textContent = `${timeVal} | ${locVal}`;

    if (d.vehicles_involved && d.vehicles_involved.length > 0) {
      vehiclesValue.innerHTML = d.vehicles_involved
        .map((v) => `<strong>${v.make_model || "Vehicle"}:</strong> Reg ${v.registration_number || "N/A"}`)
        .join("<br/>");
    } else {
      vehiclesValue.textContent = "None specified in document";
    }

    damagesValue.textContent = d.damages_summary?.value || "No specific vehicular damages noted";
    descValue.textContent = d.incident_description?.value || "No detailed officer statement provided";

    // Warnings
    if (res.warnings && res.warnings.length > 0) {
      warningsList.innerHTML = res.warnings.map((w) => `<li>${w}</li>`).join("");
      warningsBox.classList.remove("hidden");
    } else {
      warningsBox.classList.add("hidden");
    }

    // Metadata
    metaEngine.textContent = `Engine: ${m.extraction_engine}`;
    metaTime.textContent = `Processing Time: ${m.processing_time_ms} ms`;
    metaPages.textContent = `Pages: ${m.pages_processed}`;

    // JSON View
    jsonContent.textContent = JSON.stringify(res, null, 2);

    // Integration Code
    updateIntegrationSnippet();

    // Show dashboard
    switchTab("summary");
  }

  function renderField(valEl, confEl, srcEl, field) {
    if (field && field.value) {
      valEl.textContent = field.value;
      const conf = field.confidence || 0.0;
      confEl.textContent = `${Math.round(conf * 100)}%`;
      confEl.className = "conf-pill " + (conf >= 0.85 ? "conf-high" : conf >= 0.65 ? "conf-med" : "conf-low");
      if (field.source_snippet) {
        srcEl.textContent = `Evidence: ${field.source_snippet}`;
        srcEl.classList.remove("hidden");
      } else {
        srcEl.classList.add("hidden");
      }
    } else {
      valEl.textContent = "Not Detected";
      valEl.style.color = "var(--text-muted)";
      confEl.textContent = "0%";
      confEl.className = "conf-pill conf-low";
      srcEl.classList.add("hidden");
    }
  }

  // 6. Tabs
  tabSummary.addEventListener("click", () => switchTab("summary"));
  tabJson.addEventListener("click", () => switchTab("json"));
  tabIntegration.addEventListener("click", () => switchTab("integration"));

  function switchTab(tab) {
    [tabSummary, tabJson, tabIntegration].forEach((btn) => btn.classList.remove("active"));
    dashboardView.classList.add("hidden");
    jsonView.classList.add("hidden");
    integrationView.classList.add("hidden");

    if (tab === "summary") {
      tabSummary.classList.add("active");
      dashboardView.classList.remove("hidden");
    } else if (tab === "json") {
      tabJson.classList.add("active");
      jsonView.classList.remove("hidden");
    } else if (tab === "integration") {
      tabIntegration.classList.add("active");
      integrationView.classList.remove("hidden");
    }
  }

  // 7. Snippet Generator
  function updateIntegrationSnippet() {
    const origin = window.location.origin || "http://localhost:8000";
    integrationCode.textContent = `// In your Express.js backend (e.g. routes/claims.js or controllers/documentController.js)
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios'); // or native fetch with Node 18+

/**
 * Extracts accident document fields via Royal Square AI Extractor Service
 * @param {string} filePath - Path to uploaded PDF or image
 * @returns {Promise<Object>} Structured document fields with confidence
 */
async function extractDocumentFields(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('engine', 'auto'); // 'auto', 'gemini', or 'local'

  try {
    const response = await axios.post('${origin}/api/extract', form, {
      headers: {
        ...form.getHeaders(),
      },
      timeout: 30000,
    });

    const { data, overall_confidence, warnings } = response.data;
    
    // Core requested fields:
    const caseNumber = data.case_number.value;        // e.g. "CAS 412/03/2024"
    const policeStation = data.police_station.value;  // e.g. "Sandton SAPS"
    const officerName = data.officer_name.value;      // e.g. "Sgt. K. Sithole"
    const incidentDate = data.incident_date.value;    // e.g. "2024-03-14"

    console.log(\`Extracted Case \${caseNumber} with \${Math.round(overall_confidence * 100)}% confidence\`);

    return response.data;
  } catch (error) {
    console.error('AI Document Extraction failed:', error.response?.data || error.message);
    throw error;
  }
}

module.exports = { extractDocumentFields };`;
  }
  updateIntegrationSnippet();

  // 8. Clipboard Copy
  copyJsonBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(jsonContent.textContent);
    showToast("JSON copied to clipboard!");
  });

  copyCodeBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(integrationCode.textContent);
    showToast("Node.js snippet copied to clipboard!");
  });

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2500);
  }
});
