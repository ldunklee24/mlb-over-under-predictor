from MLBStatsAPI import MLBStatsAPI
import pandas as pd
import time

stats_api = MLBStatsAPI()

def get_pitcher_era(pitcher_id, season):
    try:
        stats = stats_api.get_player_stats(personId=pitcher_id, group='pitching', season=season)
        return float(stats['stats'][0]['splits'][0]['stat']['era'])
    except:
        return None

def get_team_runs_per_game(team_id, season):
    try:
        stats = stats_api.get_team_stats(teamId=team_id, season=season)
        return float(stats['stats'][0]['splits'][0]['stat']['runsPerGame'])
    except:
        return None

def build_dataset(start_date="2023-04-01", end_date="2023-09-30", season=2023, outfile="games.csv"):
    print("Building dataset...")
    results = []

    schedule = stats_api.get_schedule(startDate=start_date, endDate=end_date)
    for date in schedule['dates']:
        for game in date['games']:
            if game['status']['detailedState'] != 'Final':
                continue  # Skip unfinished games

            game_id = game['gamePk']
            home_team = game['teams']['home']['team']
            away_team = game['teams']['away']['team']

            try:
                home_score = game['teams']['home']['score']
                away_score = game['teams']['away']['score']
                total_runs = home_score + away_score
            except:
                continue

            try:
                game_data = stats_api.get_game(game_id)['gameData']
                pitchers = game_data.get('probablePitchers', {})
                home_pitcher_id = pitchers['home']['id']
                away_pitcher_id = pitchers['away']['id']
            except:
                continue

            # Get season stats
            home_rpg = get_team_runs_per_game(home_team['id'], season)
            away_rpg = get_team_runs_per_game(away_team['id'], season)
            home_era = get_pitcher_era(home_pitcher_id, season)
            away_era = get_pitcher_era(away_pitcher_id, season)

            if None in [home_rpg, away_rpg, home_era, away_era]:
                continue  # skip if any value is missing

            # Approximate betting line (you can replace this with real line later)
            betting_line = round((home_rpg + away_rpg) * 0.95, 1)  # Slightly deflated

            results.append({
                "home_team": home_team['name'],
                "away_team": away_team['name'],
                "home_runs": home_rpg,
                "away_runs": away_rpg,
                "home_era": home_era,
                "away_era": away_era,
                "actual_total_runs": total_runs,
                "betting_line": betting_line
            })

            time.sleep(0.5)  # avoid API rate limits

    df = pd.DataFrame(results)
    df.to_csv(outfile, index=False)
    print(f"Saved {len(df)} games to {outfile}")

if __name__ == "__main__":
    build_dataset()
