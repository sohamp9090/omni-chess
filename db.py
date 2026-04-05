import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="omni_chess",
        user="sohampatel",
        host="localhost",
        port="5432"
    )

def insert_player(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO players (username)
        VALUES (%s)
        ON CONFLICT (username) DO NOTHING
        RETURNING id
    """, (username,))
    
    result = cur.fetchone()
    if result is None:
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        result = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    return result[0]

def insert_game(game):
    conn = get_connection()
    cur = conn.cursor()
    
    players = game.get("players", {})
    white = players.get("white", {}).get("user", {}).get("name", "unknown")
    black = players.get("black", {}).get("user", {}).get("name", "unknown")
    opening = game.get("opening", {})
    
    cur.execute("""
        INSERT INTO games (
            id, white_username, black_username, winner,
            speed, opening_name, opening_eco, rated,
            created_at, moves, status
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """, (
        game.get("id"),
        white,
        black,
        game.get("winner", "draw"),
        game.get("speed"),
        opening.get("name"),
        opening.get("eco"),
        game.get("rated"),
        game.get("createdAt"),
        game.get("moves"),
        game.get("status")
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def insert_player_game(player_id, game_id, color):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO player_games (player_id, game_id, color)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (player_id, game_id, color))
    conn.commit()
    cur.close()
    conn.close()