import sqlite3
import json
import sys

from shapely.geometry import Point, mapping
from shapely.ops import transform
import pyproj

PROJ_WGS84 = pyproj.CRS('EPSG:4326')


def create_circle(lon, lat, radius_m=50):
    """
    Creates a GeoJSON polygon for a circle with a given radius in meters.
    """
     
    aeqd_proj = f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
    proj_aeqd = pyproj.CRS(aeqd_proj)
     
    transformer_to_aeqd = pyproj.Transformer.from_crs(PROJ_WGS84, proj_aeqd, always_xy=True)
    transformer_to_wgs84 = pyproj.Transformer.from_crs(proj_aeqd, PROJ_WGS84, always_xy=True)
     
    point = Point(lon, lat)
    point_in_aeqd = transform(transformer_to_aeqd.transform, point)
    buffer_in_aeqd = point_in_aeqd.buffer(radius_m)
    buffer_in_wgs84 = transform(transformer_to_wgs84.transform, buffer_in_aeqd)

    return mapping(buffer_in_wgs84)


def read_from_db(db_file):
     
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT Latitude, Longitude, provider_telekom, provider_vodafone, provider_telefonica, fid FROM unitless_towers")
        rows = cur.fetchall()
    return rows


def print_progress(current, total, bar_length=40):
    percent = float(current) / total
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f'\rProgress: [{arrow}{spaces}] {int(percent*100)}%')
    sys.stdout.flush()
    if current == total:
        print()


if __name__ == "__main__":
    db_file = "./assets/cell_towers.db"
    geojson_file = "./assets/unitless_towers.geojson"
    print(f"Reading coordinates from {db_file}...")
    db_rows = read_from_db(db_file)
    total = len(db_rows)
    print(f"Found {total} coordinates. Generating features...")

    features = []
    for i, (lat, lon, provider_telekom, provider_vodafone, provider_telefonica, fid) in enumerate(db_rows, 1):
        circle_geom = create_circle(lon, lat)

        provider_key = ""
        if provider_telekom: provider_key += "t"
        if provider_vodafone: provider_key += "v"
        if provider_telefonica: provider_key += "b"

        # fid = row.get('fid', None)
        print(f"Processing fid: {fid}")

        feature = {
            "type": "Feature",
            "geometry": circle_geom,
            "properties": {
                "provider": provider_key,
                "tower_fid": fid
            }  
        }
        features.append(feature)
        print_progress(i, total)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    print(f"Writing GeoJSON to {geojson_file}...")
    with open(geojson_file, 'w', encoding='utf-8') as f:
        json.dump(feature_collection, f)

    print("GeoJSON file created successfully.")
