import requests
from bs4 import BeautifulSoup
import random
import json

BASE_URL = "https://www.filgoal.com"

# ✅ Rotating user-agents to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
]

headers = {
    "User-Agent": random.choice(USER_AGENTS)
}

def normalize_img(src):
    """FilGoal sometimes uses // before domain, so convert it"""
    if src.startswith("//"):
        return "https:" + src
    return src

def scrape_filgoal_today():
    url = f"{BASE_URL}/matches/today"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to load page {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    leagues = soup.select(".mc-block")  # كل بطولة

    for league in leagues:
        league_name = league.select_one("h6 span")
        league_name = league_name.get_text(strip=True) if league_name else "غير معروف"

        matches = league.select(".cin_cntnr a")

        for match in matches:
            link = match.get("href")
            match_url = BASE_URL + link if link.startswith("/") else link

            home_team = match.select_one(".f strong")
            away_team = match.select_one(".s strong")

            home_img = match.select_one(".f img")
            away_img = match.select_one(".s img")

            status = match.select_one(".m .status")

            # Extra match info (stadium - channel - date)
            aux = match.select(".match-aux span")

            stadium = channel = date = None
            if len(aux) >= 1:
                stadium = aux[0].get_text(strip=True)
            if len(aux) >= 2:
                channel = aux[1].get_text(strip=True)
            if len(aux) >= 3:
                date = aux[2].get_text(strip=True)

            match_data = {
                "league": league_name,
                "matchUrl": match_url,
                "homeTeam": home_team.get_text(strip=True) if home_team else None,
                "awayTeam": away_team.get_text(strip=True) if away_team else None,
                "status": status.get_text(strip=True) if status else None,
                "homeLogo": normalize_img(home_img["src"]) if home_img else None,
                "awayLogo": normalize_img(away_img["src"]) if away_img else None,
                "stadium": stadium,
                "channel": channel,
                "date": date,
            }

            results.append(match_data)

    return results


if __name__ == "__main__":
    data = scrape_filgoal_today()
    print(json.dumps(data, indent=2, ensure_ascii=False))
