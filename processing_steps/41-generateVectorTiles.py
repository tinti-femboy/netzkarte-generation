import subprocess
import sys
import os
from pathlib import Path


INPUT_GEOJSON = "./assets/all_cells.geojson"
PMTILES_OUTPUT = "./serve/data/all_cells.pmtiles"

LAYER_NAME = "cells"

def run_command(command):

    print(f"\n Executing command: {' '.join(command)}")


    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Redirect stderr to stdout
        text=True,
        bufsize=1, # Line-buffered
        universal_newlines=True,
    )


    for line in process.stdout:
        print(line, end='')

    process.wait() # Wait for the command to complete

    if process.returncode != 0:
        print(f"\nERROR: Command failed with exit code {process.returncode}")
        raise subprocess.CalledProcessError(process.returncode, command)

    print(f"Command completed successfully.")

def main():
    input_path = Path(INPUT_GEOJSON)
    pmtiles_path = Path(PMTILES_OUTPUT)
    os.makedirs(pmtiles_path.parent, exist_ok=True)

    if not input_path.exists():
        print(f"❌ ERROR: Input file not found at '{input_path}'")
        print("Please run the 40 script first.")
        sys.exit(1)


    tippecanoe_command = [
        "tippecanoe",
        "-o", str(pmtiles_path),     # Output file
        "-l", LAYER_NAME,            # layer name
        "--force",                   # Overwrite the output file if it exists
        "-zg",                       # Guess max zoom level automatically
        "--drop-densest-as-needed",  # for performance
        str(input_path)              # Input file
    ]

    try:
        print("Running Tippecanoe to generate MBTiles")
        print("This may take a significant amount of time and CPU...")
        run_command(tippecanoe_command)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nAn error occurred while running Tippecanoe.")
        print("Please ensure Tippecanoe is installed and accessible in your (WS)Linux environment.")
        sys.exit(1)


    # pmtiles_command = [
    #     "bin/pmtiles",  # Adjust this path if pmtiles is installed elsewhere
    #     "convert",
    #     str(mbtiles_path),
    #     str(pmtiles_path)
    # ]

    # try:
    #     print("\n--- Step 2 of 3: Converting MBTiles to PMTiles ---")
    #     run_command(pmtiles_command)
    # except (subprocess.CalledProcessError, FileNotFoundError):
    #     print("\nAn error occurred while running pmtiles.")
    #     print("Please ensure the 'pmtiles' utility is installed (e.g., via npm).")
    #     sys.exit(1)

    # try:
    #     print(f"\n--- Step 3 of 3: Cleaning up intermediate file ---")
    #     mbtiles_path.unlink()
    #     print(f"✅ Successfully deleted temporary file: '{mbtiles_path}'")
    # except OSError as e:
    #     print(f"⚠️ Warning: Could not delete intermediate file '{mbtiles_path}'. Error: {e}")

    print("\n🎉 --- Vector Tile Generation Complete! --- 🎉")
    print(f"Your final, web-ready tile file is: {pmtiles_path}")
    print("You can now upload this file to a static web host and use it in your MapLibre GL JS website.")

if __name__ == "__main__":
    main()
