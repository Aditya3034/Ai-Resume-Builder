Got it 👍 I’ll update your **README** so it reflects the **new FastAPI-based structure** you shared. Here’s the revised version you can copy:

````markdown
# 🧠 Intelligent Resume Builder

An open-source, multi-agent system that generates ATS-friendly resumes by intelligently aggregating user data from GitHub, portfolio websites, uploaded resumes, and job descriptions.  

Built with **FastAPI**, **LangChain**, **LangGraph**, and **LLMs**, this tool empowers developers and job seekers to craft optimized, personalized resumes with minimal effort.

---

## 🚀 Features

- 🔍 Extracts data from:
  - GitHub profile
  - Portfolio website
  - Uploaded resume (PDF/DOC)
  - Multiple job descriptions
- 🧠 Multi-agent architecture with specialized agents
- 📄 Generates ATS-optimized JSON resumes
- 🎨 Renders into customizable templates
- 🔁 Supports user feedback loop for iterative refinement
- 🌐 REST API ready (FastAPI)
- ⚡ Modular design for easy extension and integration

---

## 🗂️ Project Structure

### New Structure (FastAPI-based)

```plaintext
resume-builder/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/                 # API routes
│   │   └── resume.py        # Endpoint for collecting user inputs
│   ├── services/            # Business logic (agent orchestration)
│   │   └── resume_service.py
│   ├── agents/              # Your 5 specialized agents
│   │   ├── github_agent.py
│   │   ├── portfolio_agent.py
│   │   ├── jd_keywords_agent.py
│   │   ├── resume_parser_agent.py
│   │   └── content_writer_agent.py
│   ├── graph/               # LangGraph flow logic
│   │   ├── flow.py
│   │   └── nodes.py
│   ├── templates/           # Resume templates
│   │   └── resume_templates.json
│   ├── models/              # Pydantic models
│   │   └── resume_schema.py
│   ├── utils/               # Helper functions
│   │   └── helpers.py
│   └── config.py            # App settings
├── tests/                   # Unit and integration tests
├── requirements.txt
├── README.md
└── .env
````

### Legacy Structure (standalone scripts, optional)

```plaintext
resume-builder/
├── agents/                  # Individual agents for data extraction and generation
├── graph/                   # LangGraph flow and node definitions
├── data/                    # Input/output files
├── templates/               # Resume layout templates
├── utils/                   # Helper functions
├── config/                  # API keys and settings
├── tests/                   # Unit and integration tests
├── ui/                      # Optional frontend
├── main.py                  # Entry point
├── requirements.txt
├── .env
└── README.md
```

---

## 🧩 Agent Overview

| Agent                     | Role                                    | Technology Used  |
| ------------------------- | --------------------------------------- | ---------------- |
| `github_agent.py`         | Extracts repo data from GitHub          | GitHub API       |
| `portfolio_agent.py`      | Scrapes project info from portfolio     | BeautifulSoup    |
| `jd_keywords_agent.py`    | Extracts keywords from job descriptions | spaCy / LLM      |
| `resume_parser_agent.py`  | Parses uploaded resume files            | PDFMiner / LLM   |
| `content_writer_agent.py` | Synthesizes final JSON resume           | Prompt-based LLM |

---

## 🔁 Flow Logic

The system follows a directed flow using **LangGraph**:

```
GitHub → Portfolio → JD Keywords → Resume Parser → Content Writer
```

A shared context object passes data between agents.
Users can provide feedback to refine the resume, which re-triggers the content writer agent with updated instructions.

---

## 🧾 Output Format

```json
{
  "personal_info": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "github": "https://github.com/janedoe",
    "portfolio": "https://janedoe.dev"
  },
  "summary": "Full-stack developer with 5+ years of experience...",
  "skills": ["React", "Node.js", "Docker", "CI/CD"],
  "experience": [...],
  "education": [...],
  "projects": [...],
  "keywords": ["Agile", "REST APIs", "Leadership"]
}
```

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-builder.git
cd resume-builder
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Run the FastAPI App

```bash
uvicorn app.main:app --reload
```

The API will be available at: [http://localhost:8000](http://localhost:8000)
Docs will be auto-generated at: [http://localhost:8000/docs](http://localhost:8000/docs)

---
