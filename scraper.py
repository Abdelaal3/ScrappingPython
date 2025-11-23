import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def scrape_filgoal_matches(date=None):
    """Scrape FilGoal matches by date, default = today"""
    
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    url = f"https://www.filgoal.com/matches/?date={date}"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )

    if response.status_code != 200:
        print(f"Request failed: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches_data = []

    # Select all leagues/competitions
    match_blocks = soup.select("div.mc-block")

    for block in match_blocks:
        league = block.select_one("h6")
        if not league:
            continue
        league_name = league.get_text(strip=True)

        # select all matches inside this league block
        matches = block.select("div.cin_cntnr")

        for match in matches:
            link = match.select_one("a")
            if not link:
                continue

            match_url = "https://www.filgoal.com" + link.get("href", "")

            match_id = re.search(r"/matches/(\d+)", match_url)
            match_id = match_id.group(1) if match_id else None

            # extract team and match info with selectors
            home = link.select_one(".c-i-next .f strong")
            away = link.select_one(".c-i-next .s strong")

            home_score = link.select_one(".c-i-next .f b")
            away_score = link.select_one(".c-i-next .s b")

            status = link.select_one(".c-i-next .status")

            # Extract stadium, time & channel icons
            aux_spans = link.select(".match-aux span")
            stadium = time = channel = None

            for span in aux_spans:
                icon = span.select_one("svg use")
                if not icon:
                    continue

                href = icon.get("xlink:href", "")
                text = span.get_text(strip=True)

                if "fb_field" in href:
                    stadium = text
                elif "fb_calendar" in href:
                    time = text
                elif "fb_screen" in href:
                    channel = text

            matches_data.append({
                "match_id": match_id,
                "league": league_name,
                "home_team": home.get_text(strip=True) if home else None,
                "away_team": away.get_text(strip=True) if away else None,
                "home_score": home_score.get_text(strip=True) if home_score else "-",
                "away_score": away_score.get_text(strip=True) if away_score else "-",
                "status": status.get_text(strip=True) if status else None,
                "time": time,
                "stadium": stadium,
                "channel": channel,
                "url": match_url
            })

    return matches_data


def save_daily_matches():
    """Scrape today's matches + save into JSON file"""
    matches = scrape_filgoal_matches()
    with open("daily_matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print("✅ daily_matches.json updated successfully!")


if __name__ == "__main__":
    save_daily_matches()
