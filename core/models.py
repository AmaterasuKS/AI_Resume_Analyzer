from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    match_score: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    summary: str


class QuestionRequest(BaseModel):
    question: str
    resume_text: str
    job_description: str


class QuestionResponse(BaseModel):
    answer: str
