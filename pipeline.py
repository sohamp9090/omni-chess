from lichess_api import fetch_games
from db import insert_player, insert_game, insert_player_game

def run_pipeline(username, max_games=50):
    print(f"\nStarting pipeline for: {username}")
    
    # Step 1: Add player to database
    player_id = insert_player(username)
    print(f"Player ID in database: {player_id}")
    
    # Step 2: Fetch games from Lichess
    games = fetch_games(username, max_games=max_games)
    print(f"Fetched {len(games)} games from Lichess")
    
    # Step 3: Insert each game into database
    saved = 0
    for game in games:
        insert_game(game)
        
        # Figure out what color this player was
        players = game.get("players", {})
        white = players.get("white", {}).get("user", {}).get("name", "")
        color = "white" if white.lower() == username.lower() else "black"
        
        insert_player_game(player_id, game["id"], color)
        saved += 1
    
    print(f"Saved {saved} games to database successfully!")

if __name__ == "__main__":
    # Test with your own Lichess username if you have one, or use this one
    run_pipeline("sojam9090", max_games=500)
