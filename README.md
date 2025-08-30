# Intelligent Resume Builder API

An AI-powered FastAPI application that automatically generates ATS-friendly resumes by analyzing GitHub profiles, portfolio websites, and job descriptions using advanced natural language processing.

## 🚀 Features

- **GitHub Integration**: Extracts repository data, commit history, and project information
- **Portfolio Analysis**: Scrapes personal websites and portfolios for additional context
- **Job Description Parsing**: Identifies key skills and technologies from job postings
- **Resume Generation**: Creates structured, ATS-optimized resumes using AI
- **PDF Processing**: Converts existing resumes to text for analysis and improvement
- **RESTful API**: Clean FastAPI interface with comprehensive endpoints

## 🛠️ Technologies

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: OpenAI GPT-3.5-turbo, LangChain
- **Web Scraping**: Playwright (async)
- **Document Processing**: PyPDFLoader, PDFMiner
- **Data Validation**: Pydantic
- **HTTP Client**: Requests
- **Environment**: python-dotenv

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- GitHub Personal Access Token
- Playwright browser dependencies

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd intelligent-resume-builder
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn openai langchain langchain-openai langchain-community
pip install playwright beautifulsoup4 pdfminer.six python-dotenv requests pydantic
```

3. **Install Playwright browsers**
```bash
playwright install chromium
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_personal_access_token
```

## 🚀 Usage

### Starting the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Main Resume Generation
```http
POST /generate-resume
```
**Form Data:**
- `github_url` (optional): GitHub profile URL
- `portfolio_url` (optional): Personal website URL  
- `job_description` (optional): Target job description text
- `old_resume` (optional): Existing resume PDF file
- `user_feedback` (optional): Improvement suggestions
- `user_additions` (optional): Additional information to include

**Response:** Generated resume in structured JSON format

### Testing Endpoints

#### GitHub Data Extraction
```http
GET /test/github?url=https://github.com/username
```

#### Portfolio Scraping
```http
GET /test/portfolio?url=https://yourportfolio.com
```

#### Job Description Keywords
```http
POST /test/jd-keywords
Content-Type: text/plain

[Job description text]
```

#### PDF Text Extraction
```http
POST /test/pdf-to-text
Content-Type: multipart/form-data

file: [PDF file]
```

#### Direct Resume Generation
```http
POST /test/generate-resume
Content-Type: application/json

{
  "github_data": "extracted github data",
  "portfolio_data": "scraped portfolio content", 
  "jd_keywords": ["python", "api", "fastapi"],
  "old_resume": "existing resume text",
  "user_additions": "additional info",
  "user_feedback": "improvement requests"
}
```

## 📁 Project Structure

```
intelligent-resume-builder/
├── main.py              # FastAPI application and route definitions
├── app/
│   ├── utils/
│   │   └── helpers.py   # Core utility functions
│   └── workflow.py      # AI workflow orchestration
├── .env                 # Environment variables (create this)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Core Functions

### `extract_github_data(github_url)`
Fetches repository information, commit counts, and project details from GitHub API.

### `scrape_portfolio(url)`  
Uses Playwright to extract text content from portfolio websites asynchronously.

### `extract_jd_keywords(jd)`
Analyzes job descriptions using GPT-3.5-turbo to identify relevant skills and technologies.

### `pdf_to_text(file)`
Converts uploaded PDF resumes to text using PyPDFLoader for analysis.

### `generate_resume_json(...)`
Creates structured resume JSON using LangChain and OpenAI with proper ATS optimization.

## 📊 Resume Output Schema

The generated resume follows this structured format:

```json
{
  "personal_info": {
    "name": "...",
    "email": "...",
    "phone": "..."
  },
  "summary": "Professional summary...",
  "skills": {
    "frontend": ["React", "Vue.js"],
    "backend": ["Python", "FastAPI"],
    "devops": ["Docker", "AWS"],
    "cloud": ["AWS", "Azure"],
    "ai_ml": ["TensorFlow", "OpenAI"],
    "tools": ["Git", "VS Code"]
  },
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Company Name",
      "duration": "2020-2023",
      "location": "City, State",
      "bullets": ["Achievement 1", "Achievement 2"]
    }
  ],
  "education": ["Degree details"],
  "projects": [
    {
      "name": "Project Name",
      "commits": 45,
      "description": "Project description",
      "bullets": ["Feature 1", "Feature 2"]
    }
  ],
  "keywords": ["extracted", "keywords", "list"]
}
```

## 🔒 Security Notes

- Store API keys securely in environment variables
- GitHub token should have minimal required permissions
- Validate all user inputs before processing
- Consider rate limiting for production deployments

## 🐛 Troubleshooting

**Playwright Issues:**
```bash
# Reinstall browser dependencies
playwright install --force chromium
```

**OpenAI API Errors:**
- Verify API key is valid and has sufficient credits
- Check rate limits and quotas
