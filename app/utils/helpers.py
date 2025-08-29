import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from openai import OpenAI
import os,requests
from dotenv import load_dotenv
from datetime import datetime
from typing import List
load_dotenv()  # ⬅️ Load environment variables from .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_github_data(github_url: str):
    username = github_url.rstrip("/").split("/")[-1]
    repo_url = f"https://api.github.com/users/{username}/repos"

    # Load token from environment
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise EnvironmentError("Missing GITHUB_TOKEN in environment variables.")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    # Fetch repos
    response = requests.get(repo_url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"GitHub API error: {response.status_code} - {response.text}")

    repos = response.json()
    if not isinstance(repos, list):
        raise TypeError(f"Unexpected response format: {repos}")

    projects = []
    total_user_commits = 0
    recent_repo = None
    recent_date = None
    first_repo_date = None

    for r in repos:
        repo_name = r["name"]
        description = r.get("description", "")
        updated = r.get("updated_at")
        created = r.get("created_at")

        # Track recent repo
        if updated:
            updated_dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")
            if not recent_date or updated_dt > recent_date:
                recent_date = updated_dt
                recent_repo = repo_name

        # Track first repo
        if created:
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
            if not first_repo_date or created_dt < first_repo_date:
                first_repo_date = created_dt

        # Fetch user-authored commits (first page only)
        commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
        commits_response = requests.get(commits_url, headers=headers, params={"author": username, "per_page": 100})
        if commits_response.status_code == 200:
            commit_count = len(commits_response.json())
        else:
            commit_count = 0

        total_user_commits += commit_count
        projects.append({
            "name": repo_name,
            "description": description,
            "user_commits": commit_count
        })

    return {
        "username": username,
        "total_public_repos": len(projects),
        "total_user_commits": total_user_commits,
        "most_recent_repo": recent_repo,
        "last_active": recent_date.isoformat() if recent_date else None,
        "first_repo_created": first_repo_date.isoformat() if first_repo_date else None,
        "projects": projects
    }


from playwright.async_api import async_playwright
from langchain.schema import Document

async def scrape_portfolio(url: str) -> Document:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--disable-gpu", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        # Convert route handler to async function
        async def route_intercept(route, request):
            if request.resource_type in ["image", "stylesheet", "font"]:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", route_intercept)

        await page.goto(url, wait_until="domcontentloaded")
        text = await page.evaluate("document.body.innerText")

        await browser.close()

    return Document(page_content=text.strip(), metadata={"source": url})


# from playwright.sync_api import sync_playwright
# from langchain.schema import Document
# from playwright.async_api import async_playwright

# def scrape_portfolio(url: str) -> Document:
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
#         context = browser.new_context()
#         page = context.new_page()

#         page.route("**/*", lambda route, request: 
#             route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
#         )

#         page.goto(url, wait_until="domcontentloaded")
#         text = page.evaluate("document.body.innerText")

#         browser.close()

#     return Document(page_content=text.strip(), metadata={"source": url})

import re

def extract_jd_keywords(jd: str) -> List[str]:
    prompt = (
        "Please Extract key skills, action verbs, and technologies from this job description or any keywords which can be used in Resume to improve ATS Score. "
        "Return only the keywords as a comma-separated list, without any labels or categories. "
        "Avoid prefixes like 'skills:', 'action verbs:', or 'technologies:'. Just list the raw terms:\n\n" + jd
        )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content

    # Normalize, deduplicate, lowercase
    keywords = re.split(r",\s*|\n+", raw)
    return sorted(set(kw.lower().strip() for kw in keywords if kw.strip()))


from langchain_community.document_loaders import PyPDFLoader
import tempfile
import asyncio

async def pdf_to_text(file) -> str:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Load and extract text using LangChain's async loader
    loader = PyPDFLoader(tmp_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page.page_content.strip())

    return "\n\n".join(pages)



from typing import List, Dict
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Define the Resume schema

class SkillSet(BaseModel):
    frontend: List[str]
    backend: List[str]
    devops: List[str]
    cloud: List[str]
    ai_ml: List[str]
    tools: List[str]
    
class ExperienceEntry(BaseModel):
    title: str
    company: str
    duration: str
    location: str
    bullets: List[str] 
     
class ProjectEntry(BaseModel):
    name: str
    commits: int
    description: str
    bullets: List[str]
class Resume(BaseModel):
    personal_info: Dict[str, str]
    summary: str
    skills: SkillSet
    experience: List[ExperienceEntry]
    education: List[str]
    projects: List[ProjectEntry]
    keywords: List[str]
# Agent-ready resume generation function
def generate_resume_json(
    github_data: str,
    portfolio_data: str,
    jd_keywords: List[str],
    old_resume: str,
    user_additions: str,
    user_feedback: str,
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.3
) -> Resume:
    # Setup parser
    parser = JsonOutputParser(pydantic_object=Resume)

    # Setup prompt
    prompt = PromptTemplate.from_template(
        """You are an expert resume writer specializing in ATS-friendly formatting and keyword optimization.

Using the following inputs, generate a complete resume in structured JSON format that matches the schema below. Be concise, impactful, and ensure the resume highlights relevant skills and achievements.

Schema:
{format_instructions}

Inputs:
GitHub Data:
{github_data}

Portfolio Content:
{portfolio_data}

JD Keywords to Highlight:
{jd_keywords}

Old Resume (if any):
{old_resume}

User Additions (manual updates):
{user_additions}

User Feedback or Requested Changes:
{user_feedback}

Respond only with the JSON resume.
"""
    )

    # Setup LLM
    llm = ChatOpenAI(model=model_name, temperature=temperature)

    # Chain
    chain = (
        prompt.partial(format_instructions=parser.get_format_instructions())
        | llm
        | parser
    )

    # Invoke
    return chain.invoke({
        "github_data": github_data,
        "portfolio_data": portfolio_data,
        "jd_keywords": ", ".join(jd_keywords),
        "old_resume": old_resume,
        "user_additions": user_additions,
        "user_feedback": user_feedback
    })
