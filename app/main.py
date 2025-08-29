from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from app.utils.helpers import (
    extract_github_data,
    scrape_portfolio,
    extract_jd_keywords,
    pdf_to_text,
    generate_resume_json
)

from dotenv import load_dotenv
import os
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

app = FastAPI(title="Intelligent Resume Builder")

class JDRequest(BaseModel):
    jd: str  # Single job description string


@app.get("/test/github")
def test_github(url: str):
    return extract_github_data(url)

@app.get("/test/portfolio")
def test_portfolio(url: str):
    return scrape_portfolio(url)


@app.post("/test/jd-keywords")
async def test_jd_keywords(request: Request):
    jd_text = await request.body()
    jd_str = jd_text.decode("utf-8")
    keywords = extract_jd_keywords(jd_str)
    return JSONResponse(content={"keywords": keywords})

@app.post("/test/pdf-to-text")
async def test_pdf_to_text(file: UploadFile):
    text = await pdf_to_text(file)
    return {"text": text}

from pydantic import BaseModel
from typing import List

class ResumeRequest(BaseModel):
    github_data: str
    portfolio_data: str
    jd_keywords: List[str]
    old_resume: str
    user_additions: str
    user_feedback: str

@app.post("/test/generate-resume")
async def test_generate_resume(data: ResumeRequest):
    resume = generate_resume_json(
        github_data=data.github_data,
        portfolio_data=data.portfolio_data,
        jd_keywords=data.jd_keywords,
        old_resume=data.old_resume,
        user_additions=data.user_additions,
        user_feedback=data.user_feedback
    )
    return JSONResponse(content=resume)
