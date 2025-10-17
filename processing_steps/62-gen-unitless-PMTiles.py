import subprocess
import sys
from pathlib import Path

DATA_NAME = "unitless_towers"

# --- CONFIGURATION ---
# Make sure these filenames match your actual files.
INPUT_GEOJSON = f"./assets/{DATA_NAME}.geojson"
MBTILES_OUTPUT = f"./assets/{DATA_NAME}.mbtiles"
PMTILES_OUTPUT = f"./serve/data/{DATA_NAME}.pmtiles"

# Name of the data layer inside the tileset. You'll use this in your front-end code.
LAYER_NAME = DATA_NAME

def run_command(command):
    """
    Runs a command in the shell and streams its output.
    Raises an exception if the command fails.
    """
    print(f"\n▶️  Executing command: {' '.join(command)}")

    # Using Popen to stream output in real-time
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Redirect stderr to stdout
        text=True,
        bufsize=1, # Line-buffered
        universal_newlines=True,
    )

    # Read and print output line by line
    for line in process.stdout:
        print(line, end='')

    process.wait() # Wait for the command to complete

    if process.returncode != 0:
        print(f"\n❌ ERROR: Command failed with exit code {process.returncode}")
        raise subprocess.CalledProcessError(process.returncode, command)

    print(f"✅ Command completed successfully.")

def main():
    """
    Main function to orchestrate the tile generation process.
    """
    input_path = Path(INPUT_GEOJSON)
    mbtiles_path = Path(MBTILES_OUTPUT)
    pmtiles_path = Path(PMTILES_OUTPUT)

    # --- 1. Check for the input file ---
    if not input_path.exists():
        print(f"❌ ERROR: Input file not found at '{input_path}'")
        print("Please run the 'generate_sectors_optimized.py' script first.")
        sys.exit(1)

    # --- 2. Construct and run the Tippecanoe command ---
    tippecanoe_command = [
        "tippecanoe",
        "-o", str(mbtiles_path),      # Output file
        "-l", LAYER_NAME,            # Set the layer name
        "--force",                   # Overwrite the output file if it exists
        "-zg",                       # Guess max zoom level automatically
        "--drop-densest-as-needed",  # Crucial for performance
        str(input_path)              # Input file
    ]

    try:
        print("--- Step 1 of 3: Running Tippecanoe to generate MBTiles ---")
        print("This may take a significant amount of time and CPU...")
        run_command(tippecanoe_command)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nAn error occurred while running Tippecanoe.")
        print("Please ensure Tippecanoe is installed and accessible in your WSL environment.")
        sys.exit(1)

    # --- 3. Construct and run the pmtiles conversion command ---
    pmtiles_command = [
        "./bin/pmtiles",
        "convert",
        str(mbtiles_path),
        str(pmtiles_path)
    ]

    try:
        print("\n--- Step 2 of 3: Converting MBTiles to PMTiles ---")
        run_command(pmtiles_command)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nAn error occurred while running pmtiles.")
        print("Please ensure the 'pmtiles' utility is installed (e.g., via npm).")
        sys.exit(1)

    # --- 4. Clean up the intermediate MBTiles file ---
    try:
        print(f"\n--- Step 3 of 3: Cleaning up intermediate file ---")
        mbtiles_path.unlink()
        print(f"✅ Successfully deleted temporary file: '{mbtiles_path}'")
    except OSError as e:
        print(f"⚠️ Warning: Could not delete intermediate file '{mbtiles_path}'. Error: {e}")

    # --- Final Success Message ---
    print("\n🎉 --- Vector Tile Generation Complete! --- 🎉")
    print(f"Your final, web-ready tile file is: {pmtiles_path}")
    print("You can now upload this file to a static web host and use it in your MapLibre GL JS website.")

if __name__ == "__main__":
    main()
