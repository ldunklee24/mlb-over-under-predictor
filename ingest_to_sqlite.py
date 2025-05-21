import sqlite3
from datetime import datetime
import time

from mlb_data import (
    get_games_today,
    get_team_hitting_stats,
    get_team_bullpen_stats,
    get_pitcher_stats,
    get_probable_pitchers
)
from MLBStatsAPI import MLBStatsAPI

DB_FILE = "mlb_games.db"
SEASON = 2024
api = MLBStatsAPI()

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_features (
        game_id INTEGER PRIMARY KEY,
        date TEXT,
        home_team TEXT,
        away_team TEXT,
        home_runs_pg REAL,
        away_runs_pg REAL,
        home_era REAL,
        away_era REAL,
        home_bullpen_era REAL,
        away_bullpen_era REAL,
        actual_total_runs REAL,
        stadium TEXT,
        temperature REAL,
        wind_speed REAL,
        wind_dir TEXT
    )
    ''')
    conn.commit()

def insert_game_data(conn, row):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO game_features (
        game_id, date, home_team, away_team,
        home_runs_pg, away_runs_pg,
        home_era, away_era,
        home_bullpen_era, away_bullpen_era,
        actual_total_runs,
        stadium, temperature, wind_speed, wind_dir
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)
    conn.commit()

def main():
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    games = get_games_today()

    for game in games:
        print(f"Processing: {game['away_team']} @ {game['home_team']}")
        game_id = game['game_id']
        today = datetime.today().strftime('%Y-%m-%d')

        home_hitting = get_team_hitting_stats(game['home_team_id'], SEASON)
        away_hitting = get_team_hitting_stats(game['away_team_id'], SEASON)
        home_bullpen = get_team_bullpen_stats(game['home_team_id'], SEASON)
        away_bullpen = get_team_bullpen_stats(game['away_team_id'], SEASON)
        pitchers = get_probable_pitchers(game_id)
        home_pitcher = get_pitcher_stats(pitchers['home'], SEASON)
        away_pitcher = get_pitcher_stats(pitchers['away'], SEASON)

        # Game summary for actual runs, weather, and stadium
        try:
            game_data = api.get_game(game_id)
            game_status = game_data['gameData']['status']['detailedState']
            if game_status == "Final":
                box = api.get_boxscore(game_id)
                home_score = box['teams']['home']['teamStats']['batting']['runs']
                away_score = box['teams']['away']['teamStats']['batting']['runs']
                actual_total_runs = home_score + away_score
            else:
                actual_total_runs = None

            stadium = game_data['gameData']['venue']['name']
            weather_data = game_data['gameData'].get('weather', {})
            temperature = float(weather_data.get('temp', 0))
            wind_speed = float(weather_data.get('windSpeed', 0))
            wind_dir = weather_data.get('windDirection', None)
        except Exception as e:
            print(f"[WARN] Game data missing for {game_id}: {e}")
            stadium, temperature, wind_speed, wind_dir = None, None, None, None
            actual_total_runs = None

        if any(d is None for d in [
            home_hitting, away_hitting, home_pitcher, away_pitcher,
            home_bullpen, away_bullpen
        ]):
            print(f"Skipping {game_id} due to missing core stats.")
            continue

        row = (
            game_id,
            today,
            game['home_team'],
            game['away_team'],
            home_hitting['runs_per_game'],
            away_hitting['runs_per_game'],
            home_pitcher['era'],
            away_pitcher['era'],
            home_bullpen['bullpen_era'],
            away_bullpen['bullpen_era'],
            actual_total_runs,
            stadium,
            temperature,
            wind_speed,
            wind_dir
        )

        insert_game_data(conn, row)
        time.sleep(0.5)  # avoid rate limits

    conn.close()
    print("Ingestion complete with weather and stadium!")

if __name__ == "__main__":
    main()
