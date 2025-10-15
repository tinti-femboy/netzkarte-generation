import json
import sqlite3
import sys

def load_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        # If the JSON is a list without enclosing [], add them
        content = f.read().strip()
        if not content.startswith('['):
            content = '[' + content
        if not content.endswith(']'):
            content = content + ']'
        return json.loads(content)

def insert_data(db_file, data):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    # Create table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS small_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Lat REAL,
            Lng REAL   

        )
    ''')
    for entry in data:
        cur.execute('''
            INSERT INTO small_cells (Lat, Lng)
            VALUES (?, ?)
        ''', (

            entry.get('Lat'),
            entry.get('Lng'),
        ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    json_file = "../assets/small_cell_towers.json"
    db_file = "../assets/cell_towers.db"
    data = load_json(json_file)
    insert_data(db_file, data)
    print("Data imported successfully.")