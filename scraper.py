import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def scrape_filgoal_matches(date=None):
    """
    Scrape match data from FilGoal for a specific date.
    Args:
        date: Date in format 'YYYY-MM-DD'. If None, uses today's date.
    Returns:
        List of dictionaries containing match information.
    Raises:
        Exception: If unable to fetch or parse data.
    """
    if date is None:
        date = datetime.utcnow().strftime('%Y-%m-%d')
    url = f'https://www.filgoal.com/matches/?date={date}'

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=15
        )
    except requests.RequestException as e:
        # Network or connection error
        raise Exception(f"Failed to fetch data from FilGoal: {e}")

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    matches_data = []

    # Find all match blocks
    match_blocks = soup.find_all('div', class_='mc-block')

    for block in match_blocks:
        # Get league name
        league_header = block.find('h6')
        if not league_header:
            continue

        league_name = league_header.find('span').text.strip() if league_header.find('span') else 'Unknown League'

        # Find all matches in this league
        matches = block.find_all('div', class_='cin_cntnr')

        for match in matches:
            match_link = match.find('a')
            if not match_link:
                continue

            match_url = 'https://www.filgoal.com' + match_link.get('href', '')

            # Extract match ID from URL
            match_id = re.search(r'/matches/(\d+)', match_url)
            match_id = match_id.group(1) if match_id else None

            # Get teams
            teams_div = match_link.find('div', class_='c-i-next')
            if not teams_div:
                continue

            home_div = teams_div.find('div', class_='f')
            away_div = teams_div.find('div', class_='s')

            home_team = home_div.find('strong').text.strip() if home_div and home_div.find('strong') else 'N/A'
            away_team = away_div.find('strong').text.strip() if away_div and away_div.find('strong') else 'N/A'

            # Get scores/status
            home_score = home_div.find('b').text.strip() if home_div and home_div.find('b') else '-'
            away_score = away_div.find('b').text.strip() if away_div and away_div.find('b') else '-'

            status_span = teams_div.find('span', class_='status')
            status = status_span.text.strip() if status_span else 'N/A'

            # Get extra match info
            match_aux = match_link.find('div', class_='match-aux')
            stadium = None
            match_time = None
            channel = None

            if match_aux:
                spans = match_aux.find_all('span')
                for span in spans:
                    svg = span.find('svg')
                    if svg and svg.find('use'):
                        href = svg.find('use').get('xlink:href', '')
                        text = span.text.strip()

                        if 'fb_field' in href:
                            stadium = text
                        elif 'fb_calendar' in href:
                            match_time = text
                        elif 'fb_screen' in href:
                            channel = text

            match_info = {
                'league': league_name,
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                'stadium': stadium,
                'time': match_time,
                'channel': channel,
                'url': match_url
            }

            matches_data.append(match_info)

    return matches_data

def save_daily_matches_json(date=None, output_path=None):
    """
    Scrape matches for the given date (or today) and save to a JSON file.
    Args:
        date: Date in 'YYYY-MM-DD' format or None for today.
        output_path: Path to save JSON file. Defaults to 'daily-matches.json' in current dir.
    Returns:
        Path to the saved JSON file.
    """
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'daily-matches.json')
    try:
        matches = scrape_filgoal_matches(date)
    except Exception as e:
        matches = []
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    return output_path