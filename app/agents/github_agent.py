import requests

def extract_github_data(profile_url: str) -> dict:
    username = profile_url.rstrip('/').split('/')[-1]
    api_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(api_url)
    repos = response.json()

    return [
        {
            "name": repo["name"],
            "description": repo.get("description"),
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "language": repo["language"]
        }
        for repo in repos
    ]
