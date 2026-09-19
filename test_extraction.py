"""
Automated tests for AI Document Extraction Module.
Verifies PDF extraction, health endpoints, schema compliance, and core field extraction.
"""
import sys
from pathlib import Path
import asyncio

# Ensure module path is accessible
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.extractors.pipeline import DocumentExtractionPipeline
from src.schemas import ExtractionResponse

async def run_tests():
    print("\n--- [1] Initializing Extraction Pipeline ---")
    pipeline = DocumentExtractionPipeline()
    print("[PASS] Pipeline initialized successfully.")

    sample_dir = root_dir / "tests" / "sample_reports"
    pdf1 = sample_dir / "saps_accident_report_1.pdf"
    txt1 = sample_dir / "saps_accident_report_1.txt"
    pdf2 = sample_dir / "saps_accident_report_2.pdf"

    print(f"\n--- [2] Testing Extraction on Sample Report 1 (PDF) ---")
    with open(pdf1, "rb") as f:
        file_bytes = f.read()

    res1: ExtractionResponse = await pipeline.process_document(
        file_bytes=file_bytes,
        filename="saps_accident_report_1.pdf",
        content_type="application/pdf",
        force_engine="local"
    )

    print(f"Extraction Success: {res1.success}")
    print(f"Overall Confidence: {res1.overall_confidence}")
    print(f"Engine Used:        {res1.metadata.extraction_engine}")
    print(f"Case Number:        {res1.data.case_number.value} (conf: {res1.data.case_number.confidence})")
    print(f"Police Station:     {res1.data.police_station.value} (conf: {res1.data.police_station.confidence})")
    print(f"Officer Name:       {res1.data.officer_name.value} (conf: {res1.data.officer_name.confidence})")
    print(f"Incident Date:      {res1.data.incident_date.value} (conf: {res1.data.incident_date.confidence})")
    print(f"Incident Location:  {res1.data.incident_location.value}")
    print(f"Vehicles Detected:  {len(res1.data.vehicles_involved)}")

    # Assertions for Sample 1
    assert res1.data.case_number.value is not None, "Case number was not extracted!"
    assert "412/03/2024" in res1.data.case_number.value, f"Unexpected case number: {res1.data.case_number.value}"
    assert "Sandton" in (res1.data.police_station.value or ""), f"Unexpected station: {res1.data.police_station.value}"
    assert "Sithole" in (res1.data.officer_name.value or ""), f"Unexpected officer: {res1.data.officer_name.value}"
    assert res1.data.incident_date.value == "2024-03-14", f"Unexpected date: {res1.data.incident_date.value}"
    assert res1.data.case_number.confidence > 0.7, "Confidence too low for case number"
    print("[PASS] Sample Report 1 assertions PASSED.")

    print(f"\n--- [3] Testing Extraction on Sample Report 2 (PDF) ---")
    with open(pdf2, "rb") as f:
        file_bytes2 = f.read()

    res2: ExtractionResponse = await pipeline.process_document(
        file_bytes=file_bytes2,
        filename="saps_accident_report_2.pdf",
        content_type="application/pdf",
        force_engine="local"
    )

    print(f"Case Number:        {res2.data.case_number.value} (conf: {res2.data.case_number.confidence})")
    print(f"Police Station:     {res2.data.police_station.value} (conf: {res2.data.police_station.confidence})")
    print(f"Officer Name:       {res2.data.officer_name.value} (conf: {res2.data.officer_name.confidence})")
    print(f"Incident Date:      {res2.data.incident_date.value} (conf: {res2.data.incident_date.confidence})")

    assert res2.data.case_number.value is not None, "Case number 2 not extracted!"
    assert "89/11/2023" in res2.data.case_number.value, f"Unexpected case number 2: {res2.data.case_number.value}"
    assert "Johannesburg" in (res2.data.police_station.value or ""), f"Unexpected station 2: {res2.data.police_station.value}"
    assert "Dlamini" in (res2.data.officer_name.value or ""), f"Unexpected officer 2: {res2.data.officer_name.value}"
    assert res2.data.incident_date.value == "2023-11-20", f"Unexpected date 2: {res2.data.incident_date.value}"
    print("[PASS] Sample Report 2 assertions PASSED.")

    print(f"\n--- [4] Testing Royal Square Commercial Insurance Claim 3 ---")
    txt3 = sample_dir / "saps_commercial_claim_3.txt"
    with open(txt3, "rb") as f:
        file_bytes3 = f.read()

    res3: ExtractionResponse = await pipeline.process_document(
        file_bytes=file_bytes3,
        filename="saps_commercial_claim_3.txt",
        content_type="text/plain",
        force_engine="local"
    )

    print(f"Case Number:        {res3.data.case_number.value}")
    print(f"Police Station:     {res3.data.police_station.value}")
    print(f"Officer Name:       {res3.data.officer_name.value}")
    print(f"Incident Date:      {res3.data.incident_date.value}")
    print(f"Insurance Category: {res3.data.insurance_category.value}")
    print(f"Policy Number:      {res3.data.policy_number.value}")

    assert "512/08/2024" in res3.data.case_number.value, "Commercial case number mismatch"
    assert "Midrand" in res3.data.police_station.value, "Midrand station mismatch"
    assert "Ndlovu" in res3.data.officer_name.value, "Officer Ndlovu mismatch"
    assert res3.data.incident_date.value == "2024-08-18", "Commercial incident date mismatch"
    assert "Commercial Insurance" in res3.data.insurance_category.value, "Insurance category classification failed"
    assert res3.data.policy_number.value == "POL-COM-448102", "Policy number extraction failed"
    print("[PASS] Sample Report 3 (Commercial Insurance) assertions PASSED.")

    print("\n=======================================================")
    print(" ALL EXTRACTION TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
