import sqlite3
import os

DATABASE_PATH = './assets/cell_towers.db'

 
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

 
cursor.execute("""
CREATE TABLE IF NOT EXISTS unitless_towers (
    fid INTEGER PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    creation_date TEXT,
    provider_telekom INTEGER NOT NULL DEFAULT 0,
    provider_vodafone INTEGER NOT NULL DEFAULT 0,
    provider_telefonica INTEGER NOT NULL DEFAULT 0,
    provider_1und1 INTEGER NOT NULL DEFAULT 0
);
""")

query = """
SELECT towers.*
FROM towers
LEFT JOIN sending_units ON towers.fid = sending_units.tower_fid
WHERE sending_units.tower_fid IS NULL;
"""
cursor.execute(query)

batch_size = 20000 # batch thing not working yet so just enter a huge number for now
while True:
    rows = cursor.fetchmany(batch_size)
    if not rows:
        break
    cursor.executemany("""
    INSERT OR REPLACE INTO unitless_towers (fid, latitude, longitude, creation_date, provider_telekom, provider_vodafone, provider_telefonica, provider_1und1)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)
    conn.commit()

conn.close()
os.remove("./assets/smallcell-standortdumps.txt")