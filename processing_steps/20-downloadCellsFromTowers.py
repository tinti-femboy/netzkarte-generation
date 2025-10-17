from utils.cookieManager import *
import asyncio
import httpx
import json
import os
from typing import Any, Optional, Iterable, Tuple, List

# --- Constants ---
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Referer": "https://www.bundesnetzagentur.de/DE/Vportal/TK/Funktechnik/EMF/start.html",
    "X-Requested-With": "XMLHttpRequest"
}
OUTPUT_DIR = "./assets/httpCellInfoDumps/"
JSON_FILE_PATH = "./assets/cell_towers.json"
BASE_URL = "https://www.bundesnetzagentur.de/emf-karte/hf.aspx?fid="
# --- Async Network Functions ---
async def send_netz_request(client: httpx.AsyncClient, url: str, payload: Any) -> Optional[str]:
    """Sends a single GET request and saves the response, skipping if the file already exists."""
    fid = payload.get("fid", "unknown")
    file_path = os.path.join(OUTPUT_DIR, f"tower-{fid}.html")

    # --- Check if file already exists before making a request ---
    if os.path.exists(file_path):
        return "skipped"
    # --- End of check ---

    try:
        resp = await client.get(url)
        # Removed the successful status print to keep the progress bar clean

        if resp.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            return resp.text  # Return content to signify a successful download
        else:
            # Print errors on a new line to not interfere with the progress bar
            print(f"\nRequest failed for {url} with status code: {resp.status_code}")
            return None
    except httpx.RequestError as e:
        print(f"\nAn error occurred while requesting {e.request.url!r}: {e}")
        return None


async def run_many(requests: Iterable[Tuple[str, Any]], concurrency: int = 50):
    """Runs a series of requests concurrently, showing progress and skipping existing files."""
    cookies = load_cookies_from_file()
    if not cookies:
        print("No cookies loaded; aborting requests.")
        return

    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(http2=True, headers=HEADERS, cookies=cookies, timeout=200.0) as client:
        async def worker(url: str, payload: Any):
            async with sem:
                return await send_netz_request(client, url, payload)

        tasks = [asyncio.create_task(worker(url, payload)) for url, payload in requests]

        results = []
        total_requests = len(tasks)
        if total_requests == 0:
            print("No requests to process.")
            return []

        for i, future in enumerate(asyncio.as_completed(tasks), 1):
            result = await future
            results.append(result)
            percent_complete = (i / total_requests) * 100
            print(f"Progress: {percent_complete:.2f}% ({i}/{total_requests})", end='\r')

        print()  # Print a final newline after the progress indicator

        # --- Updated Summary Logic ---
        downloaded_count = sum(1 for r in results if r and r != "skipped" and isinstance(r, str))
        skipped_count = results.count("skipped")
        failure_count = len(results) - downloaded_count - skipped_count

        print(f"\n--- Summary ---")
        print(f"Total towers processed: {len(results)}")
        print(f"  - Newly downloaded:   {downloaded_count}")
        print(f"  - Already existed (skipped): {skipped_count}")
        print(f"  - Failed requests:    {failure_count}")
        print(f"---------------")
        return results


# --- Data Loading Function ---
def build_request_pairs_from_file(file_path: str) -> List[Tuple[str, Any]]:
    """Loads tower data from the JSON file and prepares the (url, payload) pairs."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            towers = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Check its format.")
        return []

    pairs = []
    for tower in towers:
        # Ensure the tower entry has a valid 'fID'
        if 'fID' in tower and tower['fID'] is not None:
            fid = tower['fID']
            url = f"{BASE_URL}{fid}"
            payload = {"fid": fid}
            pairs.append((url, payload))
    return pairs


# --- Main Execution Block ---
def download_cells_from_towers():
    # 1. Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. Build the list of (url, payload) pairs from cell_towers.json
    request_pairs = build_request_pairs_from_file(JSON_FILE_PATH)

    # 3. Run the requests only if pairs were successfully created
    if request_pairs:
        print(f"Loaded {len(request_pairs)} tower locations. Starting download...")
        asyncio.run(run_many(request_pairs, concurrency=50))
        print("\nDownload process finished.")
    else:
        print("No requests to process. Please check your JSON file.")

if __name__ == "__main__":
    download_cells_from_towers()