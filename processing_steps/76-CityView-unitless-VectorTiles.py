import subprocess
import sys
from pathlib import Path

DATA_NAME = "cityview_unitless_towers"

INPUT_GEOJSON = f"./assets/{DATA_NAME}.geojson"
MBTILES_OUTPUT = f"./assets/{DATA_NAME}.mbtiles"
PMTILES_OUTPUT = f"./serve/data/{DATA_NAME}.pmtiles"

LAYER_NAME = DATA_NAME


def run_command(command):
    print(f"\nExecuting command: {' '.join(command)}")
     
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  
        text=True,
        bufsize=1,  
        universal_newlines=True,
    )
     
    for line in process.stdout:
        print(line, end='')
    process.wait()  
    if process.returncode != 0:
        print(f"\nERROR: Command failed with exit code {process.returncode}")
        raise subprocess.CalledProcessError(process.returncode, command)

    print(f"Command completed successfully.")

def main():
    """
    Main function to orchestrate the tile generation process.
    """
    input_path = Path(INPUT_GEOJSON)
    mbtiles_path = Path(MBTILES_OUTPUT)
    pmtiles_path = Path(PMTILES_OUTPUT)
     
    if not input_path.exists():
        print(f"ERROR: Input file not found at '{input_path}'")
        print("Please run the 'generate_sectors_optimized.py' script first.")
        sys.exit(1)
     
    tippecanoe_command = [
        "tippecanoe",
        "-o", str(pmtiles_path),       
        "-l", LAYER_NAME,             
        "--force",                    
        "-zg",                        
        "--drop-densest-as-needed",   
        str(input_path)               
    ]

    try:
        print("Running Tippecanoe to generate PMTiles")
        print("This may take a significant amount of time and CPU...")
        run_command(tippecanoe_command)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nAn error occurred while running Tippecanoe.")
        print("Please ensure Tippecanoe is installed and accessible in your (WS)Linux environment.")
        sys.exit(1)
     

    print("\n--- Vector Tile Generation Complete! --- 🎉")
    print(f"Your final, web-ready tile file is: {pmtiles_path}")
    print("You can now upload this file to a static web host and use it in your MapLibre GL JS website.")

if __name__ == "__main__":
    main()
