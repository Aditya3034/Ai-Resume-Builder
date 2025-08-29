def generate_json_resume(context: dict) -> dict:
    return {
        "personal_info": {
            "github": context.get("github_data"),
            "portfolio": context.get("portfolio_data")
        },
        "summary": "Experienced developer with a strong background in full-stack development.",
        "skills": context["jd_keywords"]["skills"],
        "experience": context["resume_data"]["experience"],
        "education": context["resume_data"]["education"],
        "projects": context["portfolio_data"],
        "keywords": context["jd_keywords"]["action_verbs"]
    }
