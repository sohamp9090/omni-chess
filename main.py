from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
import pickle
import sys
sys.path.append('/Users/sohampatel/Desktop/omni-chess')
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        dbname="omni_chess",
        user="sohampatel",
        host="localhost",
        port="5432"
    )

@app.get("/")
def root():
    return {"message": "Omni-Chess API is running!"}

@app.get("/analyze/{username}")
def analyze_player(username: str):
    # Step 1: Fetch and store their games
    run_pipeline(username, max_games=30)

    # Step 2: Load their games from database
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT g.speed, g.opening_eco, g.opening_name,
               pg.color, g.winner, g.status
        FROM games g
        JOIN player_games pg ON g.id = pg.game_id
        JOIN players p ON pg.player_id = p.id
        WHERE p.username = '{username}'
    """, conn)
    conn.close()

    if len(df) == 0:
        return {"error": "No games found for this username"}

    # Step 3: Calculate stats
    def get_result(row):
        if row['winner'] == 'draw': return 'draw'
        elif row['color'] == row['winner']: return 'win'
        else: return 'loss'

    df['result'] = df.apply(get_result, axis=1)

    total = len(df)
    wins = len(df[df['result'] == 'win'])
    losses = len(df[df['result'] == 'loss'])
    draws = len(df[df['result'] == 'draw'])

    top_openings = df['opening_name'].value_counts().head(5).to_dict()

    opening_winrates = {}
    for opening in df['opening_name'].unique():
        subset = df[df['opening_name'] == opening]
        if len(subset) >= 2:
            wr = round(len(subset[subset['result']=='win']) / len(subset) * 100, 1)
            opening_winrates[opening] = wr

    return {
        "username": username,
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": round(wins / total * 100, 1),
        "favorite_color": df['color'].value_counts().index[0],
        "most_played_speed": df['speed'].value_counts().index[0],
        "top_openings": top_openings,
        "opening_win_rates": opening_winrates
    }