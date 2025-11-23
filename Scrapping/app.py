from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import scrape_filgoal_matches
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/matches', methods=['GET'])
def get_matches():
    """
    GET /matches
    Optional query param: date=YYYY-MM-DD
    Returns today's matches or matches for the given date as JSON.
    """
    date = request.args.get('date')
    if date:
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    else:
        date = None  # Will use today's date in scraper
    try:
        matches = scrape_filgoal_matches(date)
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
