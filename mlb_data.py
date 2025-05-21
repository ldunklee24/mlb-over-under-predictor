from MLBStatsAPI import MLBStatsAPI

stats_api = MLBStatsAPI()

# In-memory cache dictionaries
TEAM_HITTING_CACHE = {}
TEAM_BULLPEN_CACHE = {}
PITCHER_CACHE = {}

def get_team_hitting_stats(team_id: int, season: int) -> dict:
    cache_key = f"{team_id}_{season}"
    if cache_key in TEAM_HITTING_CACHE:
        return TEAM_HITTING_CACHE[cache_key]

    try:
        stats = stats_api.get_team_stats(teamId=team_id, season=season)
        hitting = stats['stats'][0]['splits'][0]['stat']
        result = {
            'runs_per_game': float(hitting.get('runsPerGame', 0)),
            'avg': float(hitting.get('avg', 0)),
            'ops': float(hitting.get('ops', 0)),
            'obp': float(hitting.get('obp', 0)),
            'slg': float(hitting.get('slg', 0)),
            'home_runs': float(hitting.get('homeRuns', 0)),
        }
        TEAM_HITTING_CACHE[cache_key] = result
        return result
    except Exception as e:
        print(f"[ERROR] get_team_hitting_stats failed: {e}")
        return {}

def get_team_bullpen_stats(team_id: int, season: int) -> dict:
    cache_key = f"{team_id}_{season}"
    if cache_key in TEAM_BULLPEN_CACHE:
        return TEAM_BULLPEN_CACHE[cache_key]

    try:
        stats = stats_api.get_team_stats(
            teamId=team_id,
            season=season,
            stats='season',
            group='pitching',
            params={'position': 'relief'}
        )
        pitching = stats['stats'][0]['splits'][0]['stat']
        result = {
            'bullpen_era': float(pitching.get('era', 0)),
            'bullpen_whip': float(pitching.get('whip', 0)),
            'bullpen_innings': float(pitching.get('inningsPitched', 0)),
        }
        TEAM_BULLPEN_CACHE[cache_key] = result
        return result
    except Exception as e:
        print(f"[ERROR] get_team_bullpen_stats failed: {e}")
        return {}

def get_pitcher_stats(pitcher_id: int, season: int) -> dict:
    cache_key = f"{pitcher_id}_{season}"
    if cache_key in PITCHER_CACHE:
        return PITCHER_CACHE[cache_key]

    try:
        stats = stats_api.get_player_stats(personId=pitcher_id, group='pitching', season=season)
        if not stats['stats'][0]['splits']:
            return {}
        s = stats['stats'][0]['splits'][0]['stat']
        result = {
            'era': float(s.get('era', 0)),
            'whip': float(s.get('whip', 0)),
            'strikeouts': int(s.get('strikeOuts', 0)),
            'walks': int(s.get('baseOnBalls', 0)),
            'innings_pitched': float(s.get('inningsPitched', 0)),
            'batting_average_against': float(s.get('avg', 0)),
        }
        PITCHER_CACHE[cache_key] = result
        return result
    except Exception as e:
        print(f"[ERROR] get_pitcher_stats failed: {e}")
        return {}

def get_games_today() -> list:
    try:
        games = stats_api.get_schedule(date=None)
        games_today = []
        for g in games['dates'][0]['games']:
            games_today.append({
                'game_id': g['gamePk'],
                'home_team': g['teams']['home']['team']['name'],
                'home_team_id': g['teams']['home']['team']['id'],
                'away_team': g['teams']['away']['team']['name'],
                'away_team_id': g['teams']['away']['team']['id'],
            })
        return games_today
    except Exception as e:
        print(f"[ERROR] get_games_today failed: {e}")
        return []

def get_probable_pitchers(game_id: int) -> dict:
    try:
        lineup = stats_api.get_game(game_id)['gameData'].get('probablePitchers', {})
        return {
            'home': lineup.get('home', {}).get('id'),
            'away': lineup.get('away', {}).get('id')
        }
    except Exception as e:
        print(f"[ERROR] get_probable_pitchers failed: {e}")
        return {}
