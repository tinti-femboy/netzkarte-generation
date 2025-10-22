import subprocess
import logging
from processing_steps.utils.checkDependencies import *

startStep = 0
stopStep = 15

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
    "processing_steps/00-generateSession.py",                     
    "processing_steps/10-getInitialPositionDataDump.py",           
    "processing_steps/11-structureInitialPositionData.py",        
    "processing_steps/20-downloadCellsFromTowers.py",        
    "processing_steps/30-parseTowers.py",                           
    "processing_steps/31-cleanDatabase.py",
    "processing_steps/40-generateGeoJSON_light.py",
    "processing_steps/41-generateVectorTiles.py",
    "processing_steps/50-getSmallCellPosDump.py",
    "processing_steps/51-structSmallCellDump.py",
    "processing_steps/52-addSmallCellToDB.py",
    "processing_steps/53-genSmallCellGeoJSON.py",
    "processing_steps/54-genSmallCellVectorTiles.py",
    "processing_steps/60-identify-unitless-towers.py",
    "processing_steps/61-add-unitless-to-geoJSON.py",
    "processing_steps/62-gen-unitless-PMTiles.py",
]

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