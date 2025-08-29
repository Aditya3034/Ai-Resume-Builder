import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords(jd_text: str) -> dict:
    doc = nlp(jd_text)
    skills = set()
    verbs = set()

    for token in doc:
        if token.pos_ == "VERB":
            verbs.add(token.lemma_)
        if token.pos_ == "NOUN" and token.ent_type_ == "":
            skills.add(token.text.lower())

    return {
        "skills": list(skills),
        "action_verbs": list(verbs)
    }
