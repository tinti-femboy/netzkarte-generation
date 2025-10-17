import json


def parse_cell_tower_data(data_string):
    """
    Parses a data dump to extract cell tower JSON objects.

    Args:
        data_string (str): A string containing the raw data dump.

    Returns:
        list: A list of dictionaries, where each dictionary represents a cell tower.
    """
    cell_towers = []
    lines = data_string.strip().split('\n')

    for line in lines:
        # The user noted there is a non-breaking space at the beginning of the json line, we must remove it
        line = line.strip().lstrip('\xa0')

        # Use a try-except block to attempt parsing each line as JSON.
        # This allows us to gracefully skip non-JSON lines (headers, coordinates).
        try:
            # The line contains a JSON array of cell tower objects.
            tower_data_list = json.loads(line)
            # Add all the parsed dictionaries from the current line to our main list.
            cell_towers.extend(tower_data_list)
        except json.JSONDecodeError:
            # If a line is not a valid JSON string, we just ignore it.
            # This handles the headers like "run from..." and "sued:..."
            continue

    return cell_towers


def structure_initial_position_data():
    file_name = "./assets/smallcell-standortdumps.txt"
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data_dump = file.read()
            all_towers = parse_cell_tower_data(data_dump)

            print(f"Successfully parsed {len(all_towers)} cell towers from '{file_name}'.")

            if all_towers:
                print("\nHere are the first 5 entries:")
                for tower in all_towers[:5]:
                    print(tower)
            else:
                print("No cell tower data was found in the file.")

        # Add a new section to save the data to a JSON file
        output_file_name = "./assets/small_cell_towers.json"
        with open(output_file_name, 'w', encoding='utf-8') as json_file:
            json.dump(all_towers, json_file, indent=4)

        print(f"\nAll data has been saved to '{output_file_name}'.")

    except FileNotFoundError:
        print(
            f"Error: The file '{file_name}' was not found. Please make sure it exists in the same directory as the script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    structure_initial_position_data()