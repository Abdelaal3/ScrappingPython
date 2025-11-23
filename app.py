from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import random
import os


app = Flask(__name__)

BASE_URL = "https://www.filgoal.com"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
]


def normalize_img(src):
    if src.startswith("//"):
        return "https:" + src
    return src


def scrape_filgoal_today():
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    url = f"{BASE_URL}/matches/today"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    leagues = soup.select(".mc-block")

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

            aux = match.select(".match-aux span")

            stadium = channel = date = None
            if len(aux) >= 1:
                stadium = aux[0].get_text(strip=True)
            if len(aux) >= 2:
                channel = aux[1].get_text(strip=True)
            if len(aux) >= 3:
                date = aux[2].get_text(strip=True)

            results.append({
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
            })

    return results


@app.get("/")
def home():
    return jsonify({"status": "running ✅"})


@app.get("/matches")
def matches():
    data = scrape_filgoal_today()
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
