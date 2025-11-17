import sqlite3
import sys

import os

def cleanup_database():
    try:
        os.remove("./assets/standortdumps.txt")
    except FileNotFoundError:
        print("not deleting old standortdumps, because they dont exist")
    try:
        os.rename('./assets/httpCellInfoDumps/', './assets/old-httpCellInfoDumps/')
    except FileNotFoundError:
        print("not deleting old httpCellInfoDumps, because they dont exist")

    """
    1. Deletes towers that ONLY have sending units with the cell_type
       'Sonstige Funkanlage'. The CASCADE constraint deletes their cells.
    2. Deletes any remaining 'Sonstige Funkanlage' cells from towers that
       also contained other cell types.
    """
    db_path = "./assets/cell_towers.db"
    conn = None
    try:
        # Connect to the database, failing if the file does not exist.
        conn = sqlite3.connect(f'file:{db_path}?mode=rw', uri=True)
        cursor = conn.cursor()

        # --- Step 1: Delete towers with ONLY 'Sonstige Funkanlage' cells ---
        print("--- Step 1: Deleting towers with only 'Sonstige Funkanlage' cells ---")

        # This query identifies towers where the "highest" cell_type is not
        # 'Sonstige Funkanlage'. If the MAX() is 0, it means no other types exist.
        find_towers_query = """
            SELECT tower_fid
            FROM sending_units
            GROUP BY tower_fid
            HAVING MAX(cell_type != 'Sonstige Funkanlage') = 0;
        """
        cursor.execute(find_towers_query)
        towers_to_delete = cursor.fetchall()

        if towers_to_delete:
            print(f"Found {len(towers_to_delete)} tower(s) to delete.")
            # 'ON DELETE CASCADE' will handle deleting the associated sending_units
            delete_towers_query = "DELETE FROM towers WHERE fid = ?;"
            cursor.executemany(delete_towers_query, towers_to_delete)
            print(f"Successfully deleted {cursor.rowcount} tower(s).")
        else:
            print("No towers found that match the Step 1 deletion criteria.")

        # --- Step 2: Delete all remaining 'Sonstige Funkanlage' cells ---
        print("\n--- Step 2: Deleting remaining 'Sonstige Funkanlage' cells ---")

        # These cells belong to towers that also have other cell types.
        delete_remaining_cells_query = "DELETE FROM sending_units WHERE cell_type = 'Sonstige Funkanlage';"
        cursor.execute(delete_remaining_cells_query)
        deleted_cells_count = cursor.rowcount

        if deleted_cells_count > 0:
            print(f"Successfully deleted {deleted_cells_count} remaining 'Sonstige Funkanlage' cell(s).")
        else:
            print("No remaining 'Sonstige Funkanlage' cells were found to delete.")

        conn.commit()
        print("\nCleanup complete. All changes have been committed.")

    except sqlite3.OperationalError as e:
        print(f"Error: Could not connect to or operate on the database at '{db_path}'.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("Transaction has been rolled back.", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    cleanup_database()
