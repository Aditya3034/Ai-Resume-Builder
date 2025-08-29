from pydantic import BaseModel
from typing import List, Dict

class Resume(BaseModel):
    personal_info: Dict[str, str]
    summary: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    projects: List[Dict[str, str]]
    keywords: List[str]
