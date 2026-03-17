import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

from .models import ResumeAnalysisResponse

# Load from working .env only (not .env.example)
load_dotenv(dotenv_path=".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"


def _get_client() -> Groq:
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
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    data = _extract_json(content)
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
