from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    match_score: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    summary: str
    resume_text: str = ""  # for frontend to use with /question


class QuestionRequest(BaseModel):
    question: str
    resume_text: str
    job_description: str
    lang: str = "en"


class QuestionResponse(BaseModel):
    answer: str
