from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from groq import AuthenticationError

from core.ai_analyzer import analyze_resume, answer_question
from core.file_reader import read_docx, read_pdf, read_txt
from core.models import QuestionRequest, QuestionResponse, ResumeAnalysisResponse

app = FastAPI(title="AI Resume Analyzer")

STATIC_DIR = Path(__file__).parent / "static"


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Ensure 500 responses are always JSON; leave HTTPException to default handler."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server error: {str(exc)}"},
    )


def _read_resume_file(file: UploadFile, content: bytes) -> str:
    """Dispatch to the right reader by file extension."""
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        return read_pdf(content)
    if name.endswith(".docx"):
        return read_docx(content)
    if name.endswith(".txt"):
        return read_txt(content)
    raise HTTPException(
        status_code=400,
        detail="Unsupported format. Use PDF, DOCX or TXT.",
    )


@app.get("/")
def index():
    """Serve the frontend."""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """Analyze resume file against job description."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")
    resume_text = _read_resume_file(file, content)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from file.")
    try:
        result = analyze_resume(resume_text, job_description)
        # Build response; overwrite resume_text with extracted text (model_dump() already has resume_text)
        payload = result.model_dump() | {"resume_text": resume_text}
        return ResumeAnalysisResponse(**payload)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid or missing Groq API key. Put your key in .env as GROQ_API_KEY.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/question", response_model=QuestionResponse)
async def question(body: QuestionRequest):
    """Answer a question about the resume and job."""
    try:
        answer = answer_question(
            body.question,
            body.resume_text,
            body.job_description,
        )
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid or missing Groq API key. Put your key in .env as GROQ_API_KEY.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    return QuestionResponse(answer=answer)
