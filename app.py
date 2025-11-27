from flask import Flask, jsonify, request
from flask_cors import CORS

from scraper import (
    scrape_filgoal_matches,
    scrape_filgoal_article
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {
        "message": "✅ FilGoal API is running",
        "endpoints": [
            "/matches",
            "/matches?date=YYYY-MM-DD",
            "/article?id=ARTICLE_ID"
        ]
    }

@app.route("/matches")
def get_matches():
    date = request.args.get("date")
    return jsonify(scrape_filgoal_matches(date)), 200

@app.route("/article")
def get_single_article():
    article_id = request.args.get("id")
    if not article_id:
        return jsonify({"error": "Missing article ID"}), 400

    return jsonify(scrape_filgoal_article(article_id)), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
