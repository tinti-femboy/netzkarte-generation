import subprocess
import logging
from processing_steps.utils.checkDependencies import *

# start from 0 for full code
startStep = 16
stopStep = 17

processing_range = range(startStep, stopStep+1)



required_packages = [
    "requests",
    "tqdm",
    "pycryptodome",
    "httpx",
    "beautifulsoup4",
    "shapely",
    "pyproj",
    "lxml",
]
check_dependencies(required_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define script order
scripts = [
    "processing_steps/00-generateSession.py",                   # step 0   
    "processing_steps/10-getInitialPositionDataDump.py",        # step 1
    "processing_steps/11-structureInitialPositionData.py",      # step 2
    "processing_steps/20-downloadCellsFromTowers.py",           # step 3
    "processing_steps/30-parseTowers.py",                       # step 4
    "processing_steps/31-cleanDatabase.py",                     # step 5
    "processing_steps/40-generateGeoJSON.py",                   # step 6
    "processing_steps/41-generateVectorTiles.py",
    "processing_steps/50-getSmallCellPosDump.py",
    "processing_steps/51-structSmallCellDump.py",
    "processing_steps/52-addSmallCellToDB.py",                  # step 10
    "processing_steps/53-genSmallCellGeoJSON.py",
    "processing_steps/54-genSmallCellVectorTiles.py",
    "processing_steps/60-identify-unitless-towers.py",
    "processing_steps/61-add-unitless-to-geoJSON.py",
    "processing_steps/62-gen-unitless-PMTiles.py",
    "processing_steps/70-CityView-generateGeoJSON.py",
    "processing_steps/71-CityView-generateVectorTiles.py",
]

subprocess.run(["mkdir", "assets"])

i = 0
for script in scripts:
    if not i in processing_range:
        print(f"Skipping item {i} because not selected")
        i += 1
        continue
    i += 1

    logging.info(f"Running {script}...")
    try:
        subprocess.run([".venv/bin/python3", f"{script}"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in {script}: {e}")
        break
