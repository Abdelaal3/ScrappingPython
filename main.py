from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.get("/matches")
def get_matches():
    url = "https://www.filgoal.com/matches"
    headers = {"User-Agent": "Mozilla/5.0"}

    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    matches = []

    for m in soup.select(".cin_cntnr"):
        home = m.select_one(".f strong")
        away = m.select_one(".s strong")
        status = m.select_one(".status")
        time = m.select_one(".match-aux span:last-child")
        home_logo = m.select_one(".f img")
        away_logo = m.select_one(".s img")

        matches.append({
            "homeTeam": home.text.strip() if home else "",
            "awayTeam": away.text.strip() if away else "",
            "status": status.text.strip() if status else "",
            "time": time.text.strip() if time else "",
            "homeLogo": ("https:" + home_logo["src"]) if home_logo else "",
            "awayLogo": ("https:" + away_logo["src"]) if away_logo else "",
        })

    return jsonify(matches)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
