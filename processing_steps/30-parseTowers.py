import sqlite3
import json
import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
import multiprocessing
from tqdm import tqdm
# IMPORTANT INSTALL LXML: pip install lxml

# --- Configuration ---
DB_FILE = '../assets/cell_towers.db'
JSON_FILE = '../assets/cell_towers.json'
HTML_DIR = '../assets/httpCellInfoDumps/'

def create_database_schema(db_file):
    """Creates the database and tables if they don't exist."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS towers (
                fid INTEGER PRIMARY KEY, latitude REAL NOT NULL, longitude REAL NOT NULL,
                creation_date TEXT, provider_telekom INTEGER NOT NULL DEFAULT 0,
                provider_vodafone INTEGER NOT NULL DEFAULT 0,
                provider_telefonica INTEGER NOT NULL DEFAULT 0,
                provider_1und1 INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS sending_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tower_fid INTEGER NOT NULL, cell_type TEXT,
                mount_height REAL, mount_direction REAL, safety_distance REAL,
                vertical_safety_distance REAL,
                FOREIGN KEY (tower_fid) REFERENCES towers (fid) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS safety_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tower_fid INTEGER NOT NULL, zone_name TEXT,
                zone_safety_distance REAL, vertical_safety_distance REAL, zone_height REAL,
                FOREIGN KEY (tower_fid) REFERENCES towers (fid) ON DELETE CASCADE
            );
            -- Clear tables to ensure a fresh import
            DELETE FROM towers;
            DELETE FROM sending_units;
            DELETE FROM safety_zones;
        """)
        print(f"Database '{db_file}' schema is ready and tables have been cleared.")

def clean_numeric_value(value_str):
    """Converts a string with a comma decimal separator to a float."""
    if value_str:
        try:
            return float(value_str.strip().replace(',', '.'))
        except (ValueError, AttributeError):
            return None
    return None

def process_tower(tower_data):
    """
    Worker function to parse a single tower's HTML file.
    This function is designed to be run in a separate process.
    """
    fid = int(tower_data.get('fID'))
    if not fid:
        return None

    html_file_path = os.path.join(HTML_DIR, f'tower-{fid}.html')
    if not os.path.exists(html_file_path):
        return None

    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            # Use the faster lxml parser
            soup = BeautifulSoup(f, 'lxml')

        # 1. Extract Creation Date
        date_span = soup.find('span', id='LabelStobDatum')
        creation_date = None
        if date_span and date_span.text:
            date_str = date_span.text.strip()
            creation_date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')

        # 2. Extract Providers
        providers = {'telekom': 0, 'vodafone': 0, 'telefonica': 0, '1und1': 0}
        provider_div = soup.find('div', id='div_mobilfunkanbieter')
        if provider_div:
            for img in provider_div.find_all('img'):
                src = img.get('src', '').lower()
                for provider_name in providers:
                    if provider_name in src:
                        providers[provider_name] = 1

        # 3. Prepare main tower data tuple
        tower_tuple = (
            int(fid), tower_data.get('Lat'), tower_data.get('Lng'), creation_date,
            providers['telekom'], providers['vodafone'], providers['telefonica'], providers['1und1']
        )

        # 4. Extract Sending Units
        sending_units_list = []
        sending_units_table = soup.select_one('#div_sendeantennen table')
        if sending_units_table:
            for row in sending_units_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) == 5:
                    sending_units_list.append((
                        int(fid), cols[0].text.strip(), clean_numeric_value(cols[1].text),
                        clean_numeric_value(cols[2].text), clean_numeric_value(cols[3].text),
                        clean_numeric_value(cols[4].text)
                    ))

        # 5. Extract Safety Zones
        safety_zones_list = []
        safety_zones_table = soup.select_one('#div_sicherheitsabstaende table')
        if safety_zones_table:
            for row in safety_zones_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) == 4:
                    safety_zones_list.append((
                        int(fid), cols[0].text.strip(), clean_numeric_value(cols[1].text),
                        clean_numeric_value(cols[2].text), clean_numeric_value(cols[3].text)
                    ))

        return (tower_tuple, sending_units_list, safety_zones_list)

    except Exception:
        # Return None if any error occurs during parsing for this specific file
        return None

def main():
    """Main function to orchestrate the parsing and database insertion."""
    # 1. Prepare the database
    create_database_schema(DB_FILE)

    # 2. Load the main JSON file
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            towers_json = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return

    # 3. Use a multiprocessing Pool to parse files in parallel
    print(f"Starting parallel processing of {len(towers_json)} towers...")
    all_towers = []
    all_sending_units = []
    all_safety_zones = []

    # The 'with' statement ensures the pool is properly closed
    with multiprocessing.Pool() as pool:
        # tqdm provides a progress bar
        # imap_unordered is memory-efficient and returns results as they are completed
        
        results = list(tqdm(pool.imap_unordered(process_tower, towers_json), total=len(towers_json)))

    # 4. Collect results from all processes
    for result in results:
        if result:
            tower_tuple, sending_units_list, safety_zones_list = result
            all_towers.append(tower_tuple)
            all_sending_units.extend(sending_units_list)
            all_safety_zones.extend(safety_zones_list)

    print(f"\nParsing complete. Found data for {len(all_towers)} towers.")
    print("Starting database insertion...")

    # 5. Connect to DB and insert all data in a single transaction
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            # Use executemany for highly efficient batch inserts
            cursor.executemany("INSERT INTO towers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", all_towers)
            print(f"Inserted {cursor.rowcount} rows into 'towers'.")

            cursor.executemany("INSERT INTO sending_units (tower_fid, cell_type, mount_height, mount_direction, safety_distance, vertical_safety_distance) VALUES (?, ?, ?, ?, ?, ?)", all_sending_units)
            print(f"Inserted {cursor.rowcount} rows into 'sending_units'.")

            cursor.executemany("INSERT INTO safety_zones (tower_fid, zone_name, zone_safety_distance, vertical_safety_distance, zone_height) VALUES (?, ?, ?, ?, ?)", all_safety_zones)
            print(f"Inserted {cursor.rowcount} rows into 'safety_zones'.")

            # The 'with' statement automatically commits on success or rolls back on error
            print("Database transaction committed successfully.")
        except sqlite3.Error as e:
            print(f"Database error during batch insert: {e}")
            print("Transaction will be rolled back.")

    print("\n--- All Done ---")

if __name__ == '__main__':
    main()
