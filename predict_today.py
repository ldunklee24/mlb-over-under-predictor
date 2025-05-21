import joblib
import pandas as pd
from odds_api import get_today_ou_odds
from MLBStatsAPI import MLBStatsAPI
from mlb_data import (
    get_team_hitting_stats,
    get_team_bullpen_stats,
    get_pitcher_stats,
    get_probable_pitchers
)

stats_api = MLBStatsAPI()
model = joblib.load('model.pkl')

odds = get_today_ou_odds()

def get_odds_for_game(home, away):
    for o in odds:
        if home.lower() in o['home_team'].lower() and away.lower() in o['away_team'].lower():
            return o['over_under_line']
    return 8.5  # fallback default

def get_game_features(game):
    home_id = game['teams']['home']['team']['id']
    away_id = game['teams']['away']['team']['id']
    home_team = game['teams']['home']['team']['name']
    away_team = game['teams']['away']['team']['name']
    game_id = game['gamePk']

    try:
        home_hitting = get_team_hitting_stats(home_id, SEASON)
        away_hitting = get_team_hitting_stats(away_id, SEASON)
        pitchers = get_probable_pitchers(game_id)
        home_pitcher = get_pitcher_stats(pitchers['home'], SEASON)
        away_pitcher = get_pitcher_stats(pitchers['away'], SEASON)

        line = get_odds_for_game(home_team, away_team)

        return [
            home_hitting['runs_per_game'],
            away_hitting['runs_per_game'],
            home_pitcher['era'],
            away_pitcher['era'],
            line
        ]
    except Exception as e:
        print(f"[WARN] Failed to fetch features for {away_team} @ {home_team}: {e}")
        return None

def predict_today():
    games = stats_api.get_schedule()  # today's games
    print("Predicting Over/Under for today's games:")

    for g in games['dates'][0]['games']:
        game_id = g['gamePk']
        home_team = g['teams']['home']['team']['name']
        away_team = g['teams']['away']['team']['name']

        features = get_game_features(g)
        if features is None:
            continue
        prediction = model.predict([features])[0]
        prob = model.predict_proba([features])[0][prediction]

        verdict = 'Over' if prediction == 1 else 'Under'
        print(f"{away_team} @ {home_team} — Prediction: {verdict} ({prob:.2f} confidence)")

if __name__ == "__main__":
    predict_today()
