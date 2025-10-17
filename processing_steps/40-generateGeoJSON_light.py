import sqlite3
import pandas as pd
from shapely.geometry import Polygon
from pyproj import Transformer, CRS
import json
from tqdm import tqdm
import math
from multiprocessing import Pool, cpu_count

# --- CONFIGURATION ---
DB_FILE = './assets/cell_towers.db'
OUTPUT_GEOJSON = './assets/all_cells.geojson'
RADIUS_METERS = 200  # 10 km
SECTOR_ANGLE_DEGREES = 30

def create_sector(lon, lat, azimuth_deg, radius_m=RADIUS_METERS, angle_deg=SECTOR_ANGLE_DEGREES):

    crs_wgs84 = CRS("EPSG:4326")
    crs_mercator = CRS("EPSG:3857")
    transformer_to_mercator = Transformer.from_crs(crs_wgs84, crs_mercator, always_xy=True)
    transformer_to_wgs84 = Transformer.from_crs(crs_mercator, crs_wgs84, always_xy=True)

    center_x, center_y = transformer_to_mercator.transform(lon, lat)
    start_angle_rad = math.radians(90 - azimuth_deg - (angle_deg / 2))
    end_angle_rad = math.radians(90 - azimuth_deg + (angle_deg / 2))

    arc_points_mercator = []
    num_arc_points = 50
    for i in range(num_arc_points + 1):
        angle = start_angle_rad + (end_angle_rad - start_angle_rad) * i / num_arc_points
        x = center_x + radius_m * math.cos(angle)
        y = center_y + radius_m * math.sin(angle)
        arc_points_mercator.append((x, y))

    sector_points_mercator = [(center_x, center_y)] + arc_points_mercator
    sector_mercator = Polygon(sector_points_mercator)
    projected_points = [transformer_to_wgs84.transform(px, py) for px, py in sector_mercator.exterior.coords]

    return Polygon(projected_points)

def process_row(row_tuple):
    """
    Worker function to process a single row from the database data.
    (This function also remains the same)
    """
    index, row = row_tuple

    provider_key = ""
    if row['provider_telekom']: provider_key += "t"
    if row['provider_vodafone']: provider_key += "v"
    if row['provider_telefonica']: provider_key += "b" # b for blue

    tower_fid = row.get('tower_fid', None)
    print(f"Processing tower_fid: {tower_fid}")
    # USED TO Skip if no relevant provider is present
    # NOW we don't skip and assume no provider means every/unknown network instead of hiding it
    # if not provider_key:
    #     return None

    try:
        sector_polygon = create_sector(
            lon=row['longitude'],
            lat=row['latitude'],
            azimuth_deg=row['mount_direction']
        )
    except Exception:
        return None

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [list(sector_polygon.exterior.coords)]
        },
        "properties": {
            "provider": provider_key,
            "tower_fid": tower_fid
        }
    }
    return feature

def main():
    """
    Main function with optimized streaming GeoJSON writer.
    """
    print(f"Connecting to database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT towers.longitude AS longitude, towers.latitude AS latitude, mount_direction, provider_telekom, provider_vodafone, provider_telefonica, tower_fid FROM sending_units INNER JOIN towers WHERE towers.fid = sending_units.tower_fid ORDER BY towers.fid ASC", conn)
    conn.close()

    df.dropna(subset=['longitude', 'latitude', 'mount_direction'], inplace=True)
    total_records = len(df)
    print(f"Loaded {total_records} valid cell records from the database.")

    num_processes = cpu_count()
    print(f"Starting parallel processing and streaming write with {num_processes} cores...")

    features_written = 0
    # The 'with' statements ensure everything is closed properly
    with open(OUTPUT_GEOJSON, 'w') as f, Pool(processes=num_processes) as pool:
        # 1. Write the opening part of the GeoJSON file
        f.write('{"type": "FeatureCollection", "features": [')

        # Use pool.imap for memory-efficient iteration. It yields results as they complete.
        # Wrap the iterator with tqdm to create the progress bar.
        results_iterator = pool.imap(process_row, df.iterrows())

        # 2. Iterate through results and write each feature directly to the file
        for feature in tqdm(results_iterator, total=total_records, desc="Processing and Writing Features"):
            if feature is None:
                continue

            # Add a comma before each feature, except for the very first one
            if features_written > 0:
                f.write(',')

            # Use json.dump to write the single feature object. This is fast for small objects.
            json.dump(feature, f)
            features_written += 1

        # 3. Write the closing part of the GeoJSON file
        f.write(']}')

    print(f"\nSuccessfully generated and wrote {features_written} features.")
    print("\n--- All Done ---")
    print(f"Your memory-optimized GeoJSON file is ready at '{OUTPUT_GEOJSON}'.")
    print("You can now run Tippecanoe on this file.")

if __name__ == '__main__':
    main()
