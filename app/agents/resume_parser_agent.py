from pdfminer.high_level import extract_text

def parse_resume(file) -> dict:
    content = extract_text(file.file)
    lines = content.split('\n')
    education = [line for line in lines if "University" in line or "College" in line]
    experience = [line for line in lines if "Engineer" in line or "Developer" in line]
    skills = [line for line in lines if "Skills" in line]

    return {
        "education": education,
        "experience": experience,
        "skills": skills
    }
