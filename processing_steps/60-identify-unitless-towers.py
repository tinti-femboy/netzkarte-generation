import sqlite3

DATABASE_PATH = '../assets/cell_towers.db'

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Create the new table (adjust columns as needed)
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

# Query to find db1 rows without db2 matches
query = """
SELECT towers.*
FROM towers
LEFT JOIN sending_units ON towers.fid = sending_units.tower_fid
WHERE sending_units.tower_fid IS NULL;
"""
cursor.execute(query)

# Fetch and insert in batches
batch_size = 20000
while True:
    rows = cursor.fetchmany(batch_size)
    if not rows:
        break  # No more rows
    cursor.executemany("""
    INSERT INTO unitless_towers (fid, latitude, longitude, creation_date, provider_telekom, provider_vodafone, provider_telefonica, provider_1und1)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)
    conn.commit()  # Commit after each batch

# Close the connection
conn.close()
