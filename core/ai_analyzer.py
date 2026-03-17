import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from .models import ResumeAnalysisResponse

# Load from working .env only (not .env.example)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=str(_env_path), override=True)
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


def analyze_resume(resume_text: str, job_description: str, lang: str = "en") -> ResumeAnalysisResponse:
    """Analyze resume against job description and return structured result in the requested language."""
    client = _get_client()
    if lang == "ru":
        lang_instruction = (
            "LANGUAGE: You MUST write the entire response in RUSSIAN only. "
            "All values for summary, strengths, weaknesses, and suggestions must be in Russian. No English."
        )
        json_example = (
            '"match_score": <number 0-100>, '
            '"strengths": ["сильная сторона 1", "сильная сторона 2", ...], '
            '"weaknesses": ["слабость 1", ...], '
            '"suggestions": ["рекомендация 1", ...], '
            '"summary": "Краткий вывод на русском языке."'
        )
    else:
        lang_instruction = "LANGUAGE: Write the entire response in English only."
        json_example = (
            '"match_score": <number 0-100>, '
            '"strengths": ["strength 1", "strength 2", ...], '
            '"weaknesses": ["weakness 1", ...], '
            '"suggestions": ["suggestion 1", ...], '
            '"summary": "Brief summary in English."'
        )
    prompt = """You are an expert HR analyst. Analyze how well the given resume matches the job description.

{lang_instruction}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Respond with ONLY a valid JSON object, no other text. Use this exact structure:
{{
  {json_example}
}}
Remember: all text fields must be in the required language.""".format(
        lang_instruction=lang_instruction,
        job_description=job_description,
        resume_text=resume_text,
        json_example=json_example,
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    try:
        data = _extract_json(content)
    except Exception:
        raise
    return ResumeAnalysisResponse(
        match_score=int(data["match_score"]),
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        suggestions=data.get("suggestions", []),
        summary=data.get("summary", ""),
    )


def answer_question(
    question: str, resume_text: str, job_description: str, lang: str = "en"
) -> str:
    """Answer a question about the resume and job fit in the requested language."""
    client = _get_client()
    lang_instruction = "Answer ONLY in Russian." if lang == "ru" else "Answer ONLY in English."
    prompt = """You have the following job description and resume. Answer the question based only on this information. Be concise.

{lang_instruction}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

QUESTION: {question}

Answer in 1-3 short paragraphs. No JSON, just plain text.""".format(
        lang_instruction=lang_instruction,
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


def translate_analysis_content(
    summary: str,
    strengths: list[str],
    weaknesses: list[str],
    suggestions: list[str],
    target_lang: str,
) -> dict:
    """Translate analysis text fields to target language (en or ru). Returns dict with summary, strengths, weaknesses, suggestions."""
    if target_lang not in ("en", "ru"):
        target_lang = "en"
    client = _get_client()
    target_name = "Russian" if target_lang == "ru" else "English"
    content_json = json.dumps({
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
    }, ensure_ascii=False)
    prompt = f"""Translate the following resume analysis from its current language into {target_name}. Preserve the meaning and tone. Return ONLY a valid JSON object with the same keys: summary, strengths, weaknesses, suggestions. No other text.

Input (translate this):
{content_json}

Output (JSON only in {target_name}):"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    data = _extract_json(content)
    return {
        "summary": data.get("summary", summary),
        "strengths": data.get("strengths", strengths),
        "weaknesses": data.get("weaknesses", weaknesses),
        "suggestions": data.get("suggestions", suggestions),
    }
