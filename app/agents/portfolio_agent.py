import requests
from bs4 import BeautifulSoup

def extract_portfolio_data(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    projects = []

    for section in soup.find_all("section", class_="project"):
        title = section.find("h2").text
        description = section.find("p").text
        tech = [li.text for li in section.find_all("li")]
        projects.append({"title": title, "description": description, "tech_stack": tech})

    return projects
