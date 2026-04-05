import requests
import json

def fetch_games(username, max_games=50):
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {"Accept": "application/x-ndjson"}
    params = {
        "max": max_games,
        "opening": True,
        "moves": True,
        "clocks": True,
        "evals": False
    }

    response = requests.get(url, headers=headers, params=params, stream=True)
    games = []
    for line in response.iter_lines():
        if line:
            game = json.loads(line)
            games.append(game)

    print(f"Fetched {len(games)} games for {username}")
    return games


if __name__ == "__main__":
    games = fetch_games("DrNykterstein", max_games=5)

    if games:
        first = games[0]
        print("\n--- First game preview ---")
        print(f"Game ID:  {first.get('id')}")
        print(f"Speed:    {first.get('speed')}")
        print(f"Opening:  {first.get('opening', {}).get('name', 'N/A')}")
        print(f"White:    {first.get('players', {}).get('white', {}).get('user', {}).get('name', 'N/A')}")
        print(f"Black:    {first.get('players', {}).get('black', {}).get('user', {}).get('name', 'N/A')}")
        print(f"Result:   {first.get('winner', 'draw')}")
        print(f"\nAll available fields: {list(first.keys())}")
