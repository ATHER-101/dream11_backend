import csv
import os
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re

# File paths
csv_file = "Datasets/names.csv"
output_file = "players_data.csv"
player_data_folder = "Datasets/ipl_json_processed"

# Check if the output file already exists
if not os.path.exists(output_file):
    # Create the file and write the header if it doesn't exist
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "player_id",
            "names",
            "role",
            "batting_style",
            "bowling_style",
            "image",
            "batting_last_3_avg",
            "batting_last_5_avg",
            "batting_last_10_avg",
            "batting_last_20_avg",
            "batting_all_matches_avg",
            "bowling_last_3_avg",
            "bowling_last_5_avg",
            "bowling_last_10_avg",
            "bowling_last_20_avg",
            "bowling_all_matches_avg",
            "fielding_last_3_avg",
            "fielding_last_5_avg",
            "fielding_last_10_avg",
            "fielding_last_20_avg",
            "fielding_all_matches_avg",
        ])

# Read existing data from the output file to avoid duplicates
try:
    existing_data = pd.read_csv(output_file)
    processed_ids = set(existing_data["player_id"].astype(str))
except FileNotFoundError:
    processed_ids = set()

# Function to fetch player details
def fetch_player_details(player_name):
    try:
        search_url = f"https://www.google.com/search?q={player_name}%20cricbuzz"
        response = requests.get(search_url, timeout=10)
        search_page = BeautifulSoup(response.text, "lxml")
        link_div = search_page.find("div", class_="kCrYT")
        if not link_div:
            return None, None, None, None

        link = link_div.find("a", href=re.compile(r"[/]([a-z]|[A-Z])\w+"))
        if not link:
            return None, None, None, None

        cricbuzz_url = link["href"][7:]  # Remove '/url?q=' prefix
        cricbuzz_response = requests.get(cricbuzz_url, timeout=10).text
        cricbuzz_page = BeautifulSoup(cricbuzz_response, "lxml")

        profile_section = cricbuzz_page.find("div", class_="cb-col cb-col-100 cb-bg-grey")
        if not profile_section:
            return None, None, None, None

        # Extract data
        role = profile_section.find("div", text="Role").find_next_sibling("div").text.strip() if profile_section.find("div", text="Role") else None
        batting_style = profile_section.find("div", text="Batting Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Batting Style") else None
        bowling_style = profile_section.find("div", text="Bowling Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Bowling Style") else None
        image = cricbuzz_page.find("img", {"title": "profile image"})["src"] if cricbuzz_page.find("img", {"title": "profile image"}) else None

        return role, batting_style, bowling_style, image
    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
        return None, None, None, None

# Function to calculate averages
def calculate_player_averages(player_id):
    file_path = os.path.join(player_data_folder, player_id + ".csv")
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by='date', inplace=True)
    except Exception as e:
        print(f"Error calculating averages for player {player_id}: {e}")
        return {}

    averages = {}
    for column in ['batting_points', 'bowling_points', 'fielding_points']:
        averages[column] = {
            f"last_{n}_avg": df[column].tail(n).mean()
            for n in [3, 5, 10, 20]
        }
        averages[column]["all_matches_avg"] = df[column].mean()

    return averages

# Read input CSV and process players
with open(csv_file, mode="r") as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header
    for player_id, name in reader:
        if player_id in processed_ids:
            continue

        print(f"Processing player: {name} (ID: {player_id})")
        role, batting_style, bowling_style, image = fetch_player_details(name)

        averages = calculate_player_averages(player_id)

        row = {
            "player_id": player_id,
            "names": name,
            "role": role,
            "batting_style": batting_style,
            "bowling_style": bowling_style,
            "image": image,
            **{
                f"batting_{key}": averages.get("batting_points", {}).get(key)
                for key in ["last_3_avg", "last_5_avg", "last_10_avg", "last_20_avg", "all_matches_avg"]
            },
            **{
                f"bowling_{key}": averages.get("bowling_points", {}).get(key)
                for key in ["last_3_avg", "last_5_avg", "last_10_avg", "last_20_avg", "all_matches_avg"]
            },
            **{
                f"fielding_{key}": averages.get("fielding_points", {}).get(key)
                for key in ["last_3_avg", "last_5_avg", "last_10_avg", "last_20_avg", "all_matches_avg"]
            },
        }

        # Append the new data to the output file
        with open(output_file, mode="a", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=row.keys())
            writer.writerow(row)

        # Delay to prevent rate-limiting
        time.sleep(5)

print("Data collection completed.")
