import json
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from .models import ResumeAnalysisResponse

# Load from working .env only (not .env.example)
_env_path = Path(__file__).resolve().parent.parent / ".env"
_DEBUG_LOG = Path(__file__).resolve().parent.parent.parent / "debug-397b03.log"

def _debug_log(location: str, message: str, data: dict, hypothesis_id: str = ""):
    try:
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId": "397b03", "location": location, "message": message, "data": data, "hypothesisId": hypothesis_id, "timestamp": time.time() * 1000}) + "\n")
    except Exception:
        pass

load_dotenv(dotenv_path=str(_env_path), override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# #region agent log
def _log_env_load():
    try:
        _debug_log("ai_analyzer.py:load", "env_load", {"env_path": str(_env_path), "env_exists": _env_path.exists(), "cwd": os.getcwd(), "has_key": bool(GROQ_API_KEY), "key_len": len(GROQ_API_KEY) if GROQ_API_KEY else 0}, "env_read")
    except Exception:
        pass
_log_env_load()
# #endregion
MODEL = "llama-3.3-70b-versatile"


def _get_client() -> Groq:
    # #region agent log
    _debug_log("ai_analyzer.py:_get_client", "get_client", {"has_key": bool(GROQ_API_KEY), "key_preview": (GROQ_API_KEY[:8] + "...") if GROQ_API_KEY else None}, "H4")
    # #endregion
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")
    return Groq(api_key=GROQ_API_KEY)


def _extract_json(text: str) -> dict:
    """Extract JSON from response, handling optional markdown code block."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def analyze_resume(resume_text: str, job_description: str) -> ResumeAnalysisResponse:
    """Analyze resume against job description and return structured result."""
    # #region agent log
    _debug_log("ai_analyzer.py:analyze_resume", "analyze_resume_start", {"resume_len": len(resume_text), "jd_len": len(job_description)}, "H3")
    # #endregion
    client = _get_client()
    prompt = """You are an expert HR analyst. Analyze how well the given resume matches the job description.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Respond with ONLY a valid JSON object, no other text. Use this exact structure:
{{
  "match_score": <number 0-100>,
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1", "weakness 2", ...],
  "suggestions": ["specific suggestion 1", "suggestion 2", ...],
  "summary": "Brief 2-4 sentence summary of fit"
}}
""".format(
        job_description=job_description,
        resume_text=resume_text,
    )
    # #region agent log
    _debug_log("ai_analyzer.py:analyze_resume", "groq_call_start", {}, "H3")
    # #endregion
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    # #region agent log
    _debug_log("ai_analyzer.py:analyze_resume", "groq_call_done", {"content_preview": (content or "")[:300]}, "H3")
    # #endregion
    try:
        data = _extract_json(content)
    except Exception as e:
        # #region agent log
        _debug_log("ai_analyzer.py:analyze_resume", "extract_json_failed", {"error": str(e), "content_preview": (content or "")[:400]}, "H3")
        # #endregion
        raise
    return ResumeAnalysisResponse(
        match_score=int(data["match_score"]),
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        suggestions=data.get("suggestions", []),
        summary=data.get("summary", ""),
    )


def answer_question(
    question: str, resume_text: str, job_description: str
) -> str:
    """Answer a question about the resume and job fit."""
    client = _get_client()
    prompt = """You have the following job description and resume. Answer the question based only on this information. Be concise.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

QUESTION: {question}

Answer in 1-3 short paragraphs. No JSON, just plain text.""".format(
        job_description=job_description,
        resume_text=resume_text,
        question=question,
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
