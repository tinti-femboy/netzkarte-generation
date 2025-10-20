# pip install pyrosm geopandas pyproj shapely
from pyrosm import OSM
import geopandas as gpd
import pyproj

PBF   = "E:\osmdata\germany-buildings.osm.pbf"
CRS_M = "EPSG:3857"          # metric projection for quick area calc

# 1)  Load only buildings (stream-oriented, very memory‐friendly)

osm = OSM(PBF)
print("loading buildings into RAM now....")
buildings = osm.get_buildings()
print("DONE loading buildings into RAM")
print(f"Reprojecting to {CRS_M}....")
buildings = buildings.to_crs(CRS_M)
print(f"DONE Reprojecting to {CRS_M}")
# 3)  Iterate row-by-row
for row in buildings.itertuples():
    tags     = row.tags or {}           # extra OSM tags
    b_type   = tags.get("building", "yes")
    levels   = tags.get("building:levels")
    height_m = float(tags["height"][:-1]) if "height" in tags else (
               float(levels)*3 if levels else None)
    footprint = row.geometry.area        # m² in EPSG:3857

    print(f"{row.id}: {b_type:12}  "
          f"height={height_m or 'n/a':>6} m  "
          f"area={footprint:8.0f} m²")
