import os
import json
import csv

# Function to process a single JSON file and extract match details with player IDs
def process_match_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    match_id = os.path.basename(filepath).replace('.json', '')
    match_date = data["info"]["dates"][0]
    venue = data["info"]["venue"]
    event = data["info"].get("event", {}).get("name", "Unknown Event")
    match_type = data["info"]["match_type"]

    # Get team names
    teams = data["info"]["teams"]
    team1 = teams[0]
    team2 = teams[1]

    # Get player registry for IDs
    player_id_map = data["info"]["registry"]["people"]

    # Get players for each team and map them to IDs
    team1_players = [
        player_id_map.get(player, "Unknown_Player")
        for player in data["info"]["players"].get(team1, [])[:11]
    ]
    team2_players = [
        player_id_map.get(player, "Unknown_Player")
        for player in data["info"]["players"].get(team2, [])[:11]
    ]

    # Pad player lists with "Unknown_Player" if fewer than 11 players are present
    team1_players.extend(["Unknown_Player"] * (11 - len(team1_players)))
    team2_players.extend(["Unknown_Player"] * (11 - len(team2_players)))

    # Prepare the row data
    row = {
        "match_id": match_id,
        "date": match_date,
        "venue": venue,
        "event": event,
        "match_type": match_type,
        "team1": team1,
        "team2": team2,
        **{f"player1_{i+1}": team1_players[i] for i in range(11)},
        **{f"player2_{i+1}": team2_players[i] for i in range(11)},
    }
    return row

# Function to process all JSON files in a folder and generate a CSV
def generate_csv_from_json(folder_path, output_csv):
    rows = []

    # Loop through all JSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            filepath = os.path.join(folder_path, filename)
            row = process_match_file(filepath)
            rows.append(row)

    # Write data to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = (
            ["match_id", "date", "venue", "event", "match_type", "team1", "team2"] +
            [f"player1_{i+1}" for i in range(11)] +
            [f"player2_{i+1}" for i in range(11)]
        )
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV file generated successfully: {output_csv}")

# Specify folder containing JSON files and the output CSV file name
input_folder = "./Datasets/ipl_json"  # Replace with your folder path
output_csv_file = "matches_data.csv"  # Replace with desired CSV output file name

# Run the script
generate_csv_from_json(input_folder, output_csv_file)
