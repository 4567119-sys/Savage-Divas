from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .config import settings
from .schemas import ExtractionResponse, HealthResponse, ExtractionData
from .extractors.pipeline import DocumentExtractionPipeline


app = FastAPI(
    title="Royal Square Financial — AI Document Extractor",
    description=(
        "AI service for classifying and extracting information from "
        "Royal Square Financial client requests and documents."
    ),
    version="2.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# AI PIPELINE
# ---------------------------------------------------------

pipeline = DocumentExtractionPipeline()


# ---------------------------------------------------------
# STATIC PLAYGROUND
# ---------------------------------------------------------

static_dir = Path(__file__).parent / "static"

if static_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static"
    )


@app.get("/", include_in_schema=False)
async def serve_playground():

    index_path = static_dir / "index.html"

    if index_path.exists():
        return FileResponse(str(index_path))

    return {
        "message": (
            "Royal Square Financial AI Extractor is running. "
            "Visit /docs for API documentation."
        )
    }


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get(
    "/api/health",
    response_model=HealthResponse
)
async def health_check():

    return HealthResponse(
        status="ok",
        version="2.0.0",
        gemini_configured=settings.has_gemini,
        gemini_model=settings.GEMINI_MODEL,
        local_fallback_enabled=settings.ENABLE_LOCAL_FALLBACK
    )


# ---------------------------------------------------------
# GENERAL JSON SCHEMA
# ---------------------------------------------------------

@app.get("/api/schema")
async def get_schema():

    """
    Returns the general Royal Square Financial extraction
    schema used by the backend.
    """

    return ExtractionData.model_json_schema()


# ---------------------------------------------------------
# DOCUMENT EXTRACTION
# ---------------------------------------------------------

@app.post(
    "/api/extract",
    response_model=ExtractionResponse
)
async def extract_document(
    file: UploadFile = File(
        ...,
        description=(
            "Financial-service document or client request "
            "(PDF, PNG, JPG, JPEG, TXT)"
        )
    ),
    engine: str = Form(
        "auto",
        description=(
            "Extraction engine: "
            "'auto', 'gemini', or 'local'"
        )
    )
):

    """
    Main AI extraction endpoint.

    Accepts a Royal Square Financial document or client request
    and returns structured JSON containing:

    - Service classification
    - Request classification
    - Client information
    - Insurance information
    - Investment information
    - Accident information when applicable
    - Confidence scores
    - Missing information
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename."
        )

    try:

        file_bytes = await file.read()

        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        content_type = (
            file.content_type
            or "application/octet-stream"
        )

        response = await pipeline.process_document(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            force_engine=engine
        )

        return response

    except HTTPException:
        raise

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": (
                    "Internal document processing error: "
                    f"{str(e)}"
                ),
                "filename": file.filename
            }
        )


# ---------------------------------------------------------
# RAW TEXT EXTRACTION
# ---------------------------------------------------------

class RawTextInput(BaseModel):

    text: str

    engine: str = "auto"


@app.post(
    "/api/extract/text",
    response_model=ExtractionResponse
)
async def extract_from_raw_text(
    payload: RawTextInput
):

    """
    Extract structured Royal Square Financial information
    from pasted text.

    Useful for:

    - Client messages
    - Email text
    - OCR output
    - Chat requests
    - Testing
    """

    text_bytes = payload.text.encode("utf-8")

    return await pipeline.process_document(
        file_bytes=text_bytes,
        filename="pasted_text_input.txt",
        content_type="text/plain",
        force_engine=payload.engine
    )


# ---------------------------------------------------------
# DIRECT RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT
    )