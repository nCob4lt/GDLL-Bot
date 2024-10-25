import sqlite3
import io
from datetime import datetime

connection = sqlite3.connect("gdll.db")
cursor = connection.cursor()

def initialize_tables():

    cursor.execute(''' CREATE TABLE IF NOT EXISTS competitors (id INTEGER PRIMARY KEY,
                    nickname TEXT,
                    rank TEXT,
                    elo INTEGER,
                    played_games INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    winrate REAL,
                    best_elo INTEGER);''')
    
    cursor.execute(''' CREATE TABLE IF NOT EXISTS matchmaking (id INTEGER PRIMARY KEY,
                    nickname TEXT,
                    tier TEXT,
                    elo INTEGER)''')

    connection.commit()

def register_in_database(uid, nickname):

    cursor.execute(''' INSERT INTO competitors (id, nickname, rank, elo, played_games, wins, losses, winrate, best_elo) VALUES (?,?,?,?,?,?,?,?,?);''',
                    (uid, nickname, "Iron 1", 1000, 0, 0, 0, 0, 1000))
    
    connection.commit()


def get_user_elo(uid):

    cursor.execute(''' SELECT elo FROM competitors WHERE id = ?;''', (uid,))
    l = cursor.fetchall()
    return l
    

def insert_in_matchmaking(uid, nickname, tier, elo):

    cursor.execute('''INSERT INTO matchmaking (id, nickname, tier, elo) VALUES (?,?,?,?);''', 
                    (uid, nickname, tier, elo))
    connection.commit()


def search_matchmaking(ctx, tiers):

    cursor.execute(''' SELECT id, nickname, elo FROM matchmaking WHERE id != ? and tier = ?;''',
                    (ctx.author.id, tiers[ctx.channel.id]))
    l = cursor.fetchall()
    return l

def search_in_matchmaking_by_id(uid):

    cursor.execute(''' SELECT * FROM matchmaking WHERE id = ?;''',
                    (uid,))
    l = cursor.fetchall()
    return l

def delete_from_matchmaking(uid):

    cursor.execute('''DELETE FROM matchmaking WHERE id = ?;''', (uid,))
    connection.commit()


def get_competitor_by_id(uid):

    cursor.execute(''' SELECT * FROM competitors WHERE id = ?;''',
                    (uid,))
    competitor = cursor.fetchall()
    return competitor

def update_competitor(new, competitor, attr):

    match attr:
        case "elo":
            cursor.execute('''UPDATE competitors SET elo = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "played_games":
            cursor.execute('''UPDATE competitors SET played_games = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "wins":
            cursor.execute('''UPDATE competitors SET wins = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "losses":
            cursor.execute('''UPDATE competitors SET losses = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "best_elo":
            cursor.execute('''UPDATE competitors SET best_elo = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "winrate":
            cursor.execute('''UPDATE competitors SET winrate = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case "rank":
            cursor.execute('''UPDATE competitors SET rank = ? WHERE id = ?;''',
                            (new, competitor[0][0]))
            connection.commit()
        case _:
            raise ValueError("The attribute does not exist.")
        
        
def get_best_competitors():

    cursor.execute('''SELECT * FROM competitors ORDER BY elo DESC LIMIT 10;''')
    competitors = cursor.fetchall()

    return competitors

def save_into_file():
    with io.open(f"saves/gdllbackup{datetime.today().strftime('%Y-%m-%d%H%M%S')}.sql", "w") as p:
            for line in connection.iterdump():
                p.write('%s\n' % line)

def retrieve_data_from_file(queries):

    for query in queries:
        cursor.execute(query)

        