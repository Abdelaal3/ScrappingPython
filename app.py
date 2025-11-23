from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from scraper import scrape_filgoal_matches

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return {
        "message": "✅ FilGoal Matches API is running",
        "endpoints": [
            "/matches",
            "/matches?date=YYYY-MM-DD"
        ]
    }


@app.route("/matches")
def get_matches():
    date = request.args.get("date")

    # لو تاريخ محدد → scrape مرة واحدة
    if date:
        return jsonify(scrape_filgoal_matches(date)), 200

    # لو تاريخ اليوم → اقرأ من الملف
    if os.path.exists("daily_matches.json"):
        with open("daily_matches.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f)), 200

    # fallback — لو الملف مش موجود
    return jsonify(scrape_filgoal_matches()), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
