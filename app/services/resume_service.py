from app.agents.github_agent import extract_github_data
from app.agents.portfolio_agent import extract_portfolio_data
from app.agents.jd_keywords_agent import extract_keywords
from app.agents.resume_parser_agent import parse_resume
from app.agents.content_writer_agent import generate_json_resume

async def generate_resume(github_url, portfolio_url, jd_text, resume_file):
    context = {
        "github_data": extract_github_data(github_url),
        "portfolio_data": extract_portfolio_data(portfolio_url),
        "jd_keywords": extract_keywords(jd_text),
        "resume_data": parse_resume(resume_file),
        "user_feedback": None
    }
    final_json = generate_json_resume(context)
    return final_json
