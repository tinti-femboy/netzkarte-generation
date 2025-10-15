import sqlite3

# --- Configuration ---
DB_FILE = 'cell_towers.db'

def add_coordinates_to_units():
    """
    Adds latitude and longitude columns to the sending_units table
    and populates them with data from the towers table.
    """
    print(f"Connecting to database '{DB_FILE}'...")
    try:
        # The 'with' statement handles connection closing and transactions
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            print("Connection successful.")

            # --- Step 1: Alter the table schema ---
            # Check if columns already exist to make the script re-runnable
            cursor.execute("PRAGMA table_info(sending_units)")
            existing_columns = [info[1] for info in cursor.fetchall()]

            if 'latitude' not in existing_columns:
                print("Adding 'latitude' column to sending_units table...")
                cursor.execute("ALTER TABLE sending_units ADD COLUMN latitude REAL")
            else:
                print("'latitude' column already exists.")

            if 'longitude' not in existing_columns:
                print("Adding 'longitude' column to sending_units table...")
                cursor.execute("ALTER TABLE sending_units ADD COLUMN longitude REAL")
            else:
                print("'longitude' column already exists.")

            # --- Step 2: Update the data using a single SQL statement ---
            # This is far more efficient than looping in Python.
            # It updates each row in sending_units by looking up the corresponding
            # lat/lon from the towers table using a correlated subquery.
            print("\nPopulating new columns with coordinate data. This may take a moment...")

            sql_update_statement = """
            UPDATE sending_units
            SET
                latitude = (SELECT latitude FROM towers WHERE towers.fid = sending_units.tower_fid),
                longitude = (SELECT longitude FROM towers WHERE towers.fid = sending_units.tower_fid)
            WHERE
                -- Only update rows that haven't been populated yet
                latitude IS NULL OR longitude IS NULL;
            """

            cursor.execute(sql_update_statement)

            # The 'with' block will automatically commit the transaction here

            print(f"Successfully updated {cursor.rowcount} rows in the 'sending_units' table.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        print("The operation was rolled back.")

    print("\n--- Enrichment Complete ---")

if __name__ == '__main__':
    add_coordinates_to_units()
