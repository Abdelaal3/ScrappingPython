import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def scrape_filgoal_matches(date=None):
    """Scrape FilGoal matches by date — default = today"""

    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    url = f"https://www.filgoal.com/matches/?date={date}"

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
    except Exception as e:
        print("❌ Request error:", e)
        return []

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches_data = []
    seen = set()  # ✅ prevent duplicates

    match_blocks = soup.find_all("div", class_="mc-block")

    for block in match_blocks:
        league_header = block.find("h6")
        if not league_header:
            continue

        league_name = league_header.get_text(separator=" ", strip=True).split(" - ")[0]


        matches = block.find_all("div", class_="cin_cntnr")

        for match in matches:
            link = match.find("a")
            if not link:
                continue

            match_url = "https://www.filgoal.com" + link.get("href", "")

            match_id = re.search(r"/matches/(\d+)", match_url)
            match_id = match_id.group(1) if match_id else None

            if not match_id or match_id in seen:
                continue

            seen.add(match_id)

            teams = link.find("div", class_="c-i-next")
            if not teams:
                continue

            home_div = teams.find("div", class_="f")
            away_div = teams.find("div", class_="s")

            home = home_div.find("strong").text.strip() if home_div else None
            away = away_div.find("strong").text.strip() if away_div else None

            home_score = home_div.find("b").text.strip() if home_div and home_div.find("b") else "-"
            away_score = away_div.find("b").text.strip() if away_div and away_div.find("b") else "-"

            status = teams.find("span", class_="status")
            status = status.text.strip() if status else "N/A"

            aux = link.find("div", class_="match-aux")
            stadium = time = channel = None

            if aux:
                for span in aux.find_all("span"):
                    svg = span.find("svg")
                    if not svg:
                        continue

                    icon = svg.find("use").get("xlink:href", "")

                    text = span.text.strip()

                    if "fb_field" in icon:
                        stadium = text
                    elif "fb_calendar" in icon:
                        time = text
                    elif "fb_screen" in icon:
                        channel = text

            matches_data.append({
                "match_id": match_id,
                "league": league_name,
                "home_team": home,
                "away_team": away,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "time": time,
                "stadium": stadium,
                "channel": channel,
                "url": match_url
            })

    return matches_data


def save_daily_matches():
    """Scrape today & save into JSON file"""
    matches = scrape_filgoal_matches()
    with open("daily_matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print("✅ daily_matches.json updated successfully!")


if __name__ == "__main__":
    save_daily_matches()
