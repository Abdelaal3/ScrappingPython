import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import pytz



def scrape_filgoal_matches(date=None):
    """Scrape FilGoal matches by date — default = today"""

    if not date:
        egypt_tz = pytz.timezone("Africa/Cairo")
        date = datetime.now(egypt_tz).strftime("%Y-%m-%d")

    url = f"https://www.filgoal.com/matches/?date={date}"

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        timeout=15
    )

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    matches_data = []
    seen_ids = set()

    match_blocks = soup.find_all("div", class_="mc-block")

    for block in match_blocks:

        matches = block.find_all("div", class_="cin_cntnr")

        for match in matches:
            link = match.find("a")
            if not link:
                continue

            href = link.get("href", "")
            match_url = "https://www.filgoal.com" + href

            # ✅ Extract match ID
            match_id_match = re.search(r"/matches/(\d+)", href)
            match_id = match_id_match.group(1) if match_id_match else None

            if not match_id or match_id in seen_ids:
                continue
            seen_ids.add(match_id)

            # ✅ Extract league name from URL — always correct
            league_name = "غير معروف"
            if "في-" in href:
                league_raw = href.split("في-")[-1]
                league_name = league_raw.replace("-", " ").strip()

            teams = link.find("div", class_="c-i-next")
            if not teams:
                continue

            home_div = teams.find("div", class_="f")
            away_div = teams.find("div", class_="s")

            home = home_div.find("strong").get_text(strip=True) if home_div else None
            away = away_div.find("strong").get_text(strip=True) if away_div else None

            home_score_tag = home_div.find("b") if home_div else None
            away_score_tag = away_div.find("b") if away_div else None

            home_score = home_score_tag.get_text(strip=True) if home_score_tag else "-"
            away_score = away_score_tag.get_text(strip=True) if away_score_tag else "-"

            status_tag = teams.find("span", class_="status")
            status = status_tag.get_text(strip=True) if status_tag else None

            aux = link.find("div", class_="match-aux")
            stadium = time = channel = None

            if aux:
                for span in aux.find_all("span"):
                    icon = span.find("use")
                    if not icon:
                        continue
                    icon_ref = icon.get("xlink:href", "")
                    text = span.get_text(strip=True)

                    if "fb_field" in icon_ref:
                        stadium = text
                    elif "fb_calendar" in icon_ref:
                        time = text
                    elif "fb_screen" in icon_ref:
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
    """Delete old file + save fresh data without duplicates"""

    filename = "daily_matches.json"

    if os.path.exists(filename):
        os.remove(filename)

    matches = scrape_filgoal_matches()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated — {len(matches)} matches saved successfully!")




def scrape_filgoal_article(article_id):
    """Scrape full FilGoal article content"""

    url = f"https://www.filgoal.com/articles/{article_id}"

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        timeout=15
    )

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ get correct title
    title_tag = soup.select_one("div.article div.title h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # ✅ get date
    date_tag = soup.select_one("div.article div.title > p")
    date = date_tag.get_text(strip=True) if date_tag else None

    # ✅ get author
    author_tag = soup.select_one("div.article div.title a.author")
    author = author_tag.get_text(strip=True) if author_tag else None

    # ✅ get main image
    img_tag = soup.select_one("div.details img.responsive-img")
    image = None
    if img_tag:
        image = img_tag.get("data-src") or img_tag.get("src")

    # ✅ extract full content including h2
    content_section = soup.select_one("#details_content")
    content = None

    if content_section:
        # remove related box
        for rel in content_section.select(".related"):
            rel.decompose()

        # allowed content blocks
        blocks = content_section.find_all([
            "h2", "h3", "p", "li", "strong", "span"
        ])

        extracted = []
        for b in blocks:
            text = b.get_text(" ", strip=True)
            if text and text not in extracted:
                extracted.append(text)

        content = "\n\n".join(extracted)

    return {
        "article_id": article_id,
        "title": title,
        "date": date,
        "author": author,
        "image": image,
        "content": content,
        "url": url
    }



def scrape_latest_article_ids(limit=10):
    url = "https://www.filgoal.com/articles"

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=15
    )

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    ids = []
    article_links = soup.find_all("a", href=True)

    for link in article_links:
        href = link["href"]

        match = re.search(r"/articles/(\d+)", href)
        if match:
            article_id = match.group(1)
            if article_id not in ids:
                ids.append(article_id)

        if len(ids) >= limit:
            break

    return ids





if __name__ == "__main__":
    save_daily_matches()


