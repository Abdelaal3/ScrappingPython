# FilGoal Football Matches Scraper API

A simple REST API to scrape football match data from FilGoal.com for any date.

## Features
- Scrapes football matches from FilGoal.com for a given date (default: today)
- REST API with endpoints:
  - `GET /matches` — returns today's matches in JSON
  - `GET /matches?date=YYYY-MM-DD` — returns matches for a specific date
- Returns empty array if no matches exist
- Handles errors (invalid date, site unreachable, etc.)
- CORS enabled for all origins
- Production-ready: proper error handling, readable code, docstrings
- Railway deployment ready (Procfile + cron job)

---

## Installation & Local Usage

1. **Clone the repo & enter the folder:**
   ```sh
   git clone <your-repo-url>
   cd Scrapping/Scrapping
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the API locally:**
   ```sh
   python app.py
   ```
   The API will be available at `http://localhost:8000`.

---

## API Usage Examples

### Get today's matches
```
GET http://localhost:8000/matches
```
**Response:**
```json
[
  {
    "league": "Egyptian Premier League",
    "match_id": "123456",
    "home_team": "Al Ahly",
    "away_team": "Zamalek",
    "home_score": "2",
    "away_score": "1",
    "status": "FT",
    "stadium": "Cairo Stadium",
    "time": "20:00",
    "channel": "ONTime Sports",
    "url": "https://www.filgoal.com/matches/123456"
  },
  ...
]
```

### Get matches for a specific date
```
GET http://localhost:8000/matches?date=2025-11-23
```

### Error: Invalid date
```
GET http://localhost:8000/matches?date=2025-13-01
```
**Response:**
```json
{"error": "Invalid date format. Use YYYY-MM-DD."}
```

---

## Railway Deployment

1. **Push your code to a GitHub repo.**
2. **Create a new Railway project and link your repo.**
3. **Railway will auto-detect the Python app.**
4. **Ensure the following files exist in your project root:**
   - `app.py` (Flask entry point)
   - `scraper.py` (scraping logic)
   - `requirements.txt`
   - `Procfile`
5. **Set the web service to use port 8000.**
6. **Deploy!**

---

## Railway Cron Job (Daily Scrape)

To run the scraper daily at 8:00 AM UTC and save results to `daily-matches.json`, add a Railway Cron Job with the following command:

```
python -c "from scraper import save_daily_matches_json; save_daily_matches_json()"
```

- This will create/update `daily-matches.json` in the project directory every day at 8:00 UTC.

---

## License
MIT
