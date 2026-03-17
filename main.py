from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from core.ai_analyzer import analyze_resume, answer_question
from core.file_reader import read_docx, read_pdf, read_txt
from core.models import QuestionRequest, QuestionResponse, ResumeAnalysisResponse

app = FastAPI(title="AI Resume Analyzer")

STATIC_DIR = Path(__file__).parent / "static"


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
    result = analyze_resume(resume_text, job_description)
    return ResumeAnalysisResponse(
        **result.model_dump(),
        resume_text=resume_text,
    )


@app.post("/question", response_model=QuestionResponse)
async def question(body: QuestionRequest):
    """Answer a question about the resume and job."""
    answer = answer_question(
        body.question,
        body.resume_text,
        body.job_description,
    )
    return QuestionResponse(answer=answer)
