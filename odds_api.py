# odds_api.py

import requests

API_KEY = "" 
SPORT = "baseball_mlb"
REGIONS = "us"
MARKETS = "totals"
ODDS_FORMAT = "american"

def get_today_ou_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"[ERROR] Odds API failed: {response.text}")
        return []

    odds_data = response.json()
    games = []
    for game in odds_data:
        if not game.get("bookmakers"):
            continue

        bookmaker = game["bookmakers"][0]
        totals = bookmaker["markets"][0]["outcomes"]

        total_line = None
        for outcome in totals:
            if outcome["name"].lower() == "over":
                total_line = float(outcome["point"])
                break

        games.append({
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "commence_time": game["commence_time"],
            "over_under_line": total_line
        })

    return games
