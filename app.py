from flask import Flask, jsonify, request
from flask_cors import CORS
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
        return jsonify(scrape_filgoal_matches(date)), 200


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
