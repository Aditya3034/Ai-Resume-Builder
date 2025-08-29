from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from app.services.resume_service import generate_resume, update_resume

router = APIRouter()

@router.post("/collect-inputs")
async def collect_user_inputs(
    github_url: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    old_resume: Optional[UploadFile] = File(None),
    job_descriptions: Optional[List[str]] = Form(None),
    additional_info: Optional[str] = Form(None)
):
    """
    Collect user inputs from various optional sources and generate a resume.
    """
    resume_json = await generate_resume(
        github_url=github_url,
        portfolio_url=portfolio_url,
        old_resume=old_resume,
        job_descriptions=job_descriptions,
        additional_info=additional_info
    )
    return resume_json


@router.post("/update-resume")
async def update_existing_resume(
    existing_resume: dict,
    updates: dict
):
    """
    Accept an existing resume and user-provided updates.
    Returns the updated resume JSON.
    """
    updated_resume = update_resume(existing_resume, updates)
    return updated_resume
