import csv
import requests
from bs4 import BeautifulSoup
import re
import time
import os
import pandas as pd

# Input and output file paths
csv_file = "test.csv"
output_file = "players_data_with_averages.csv"
player_data_folder = "Datasets/ipl_json_processed"  # Folder containing player-specific CSV files

# Dictionary to store player data
players_data = {}


# Read the input CSV file
with open(csv_file, mode="r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header if present
    for row in reader:
        identifier, name = row

        if identifier not in players_data:
            players_data[identifier] = {
                "identifier": identifier,
                "names": set(),  # Use a set to avoid duplicate names
                "role": None,
                "batting_style": None,
                "bowling_style": None,
                "image": None,
            }

        players_data[identifier]["names"].add(name)


# Function to scrape player details
def fetch_player_details(player_name):
    try:
        search_url = f"https://www.google.com/search?q={player_name}%20cricbuzz"
        search_response = requests.get(search_url, timeout=10).text
        search_page = BeautifulSoup(search_response, "lxml")
        link_div = search_page.find("div", class_="kCrYT")

        if not link_div:
            print(f"No link found for {player_name}")
            return None, None, None, None

        link = link_div.find("a", href=re.compile(r"[/]([a-z]|[A-Z])\w+"))
        if not link:
            print(f"No valid Cricbuzz link found for {player_name}")
            return None, None, None, None

        cricbuzz_url = link["href"][7:]  # Remove '/url?q=' prefix
        cricbuzz_response = requests.get(cricbuzz_url, timeout=10).text
        cricbuzz_page = BeautifulSoup(cricbuzz_response, "lxml")

        profile_section = cricbuzz_page.find("div", class_="cb-col cb-col-100 cb-bg-grey")
        if not profile_section:
            print(f"Profile section not found for {player_name}")
            return None, None, None, None

        # Extract role
        role_div = profile_section.find("div", text="Role")
        role = role_div.find_next_sibling("div").text.strip() if role_div else None

        # Extract batting style
        batting_style_div = profile_section.find("div", text="Batting Style")
        batting_style = batting_style_div.find_next_sibling("div").text.strip() if batting_style_div else None

        # Extract bowling style
        bowling_style_div = profile_section.find("div", text="Bowling Style")
        bowling_style = bowling_style_div.find_next_sibling("div").text.strip() if bowling_style_div else None

        # Extract image URL
        image_tag = cricbuzz_page.find("img", {"title": "profile image"})
        image_url = image_tag["src"] if image_tag else None

        return role, batting_style, bowling_style, image_url

    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
        return None, None, None, None


# Function to calculate player averages
def calculate_player_averages(player_id):
    """
    Calculate averages of batting, bowling, and fielding points for a player.
    """
    file_path = os.path.join(player_data_folder, player_id + ".csv")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {
            "batting_avg": {},
            "bowling_avg": {},
            "fielding_avg": {},
            "error": f"File for player_id {player_id} not found at {file_path}",
        }

    # Sort data by date
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date', inplace=True)

    # Columns of interest
    point_columns = ['batting_points', 'bowling_points', 'fielding_points']
    averages = {}

    for column in point_columns:
        averages[column] = {}
        for n in [3, 5, 10, 20]:
            averages[column][f"last_{n}_avg"] = df[column].tail(n).mean()
        averages[column]["all_matches_avg"] = df[column].mean()

    return averages


# Process each player and fetch data
for identifier, data in players_data.items():
    primary_name = next(iter(data["names"]))  # Use the first name as the primary search term
    print(f"Fetching data for {primary_name}...")
    retries = 3
    while retries > 0:
        role, batting_style, bowling_style, image = fetch_player_details(primary_name)
        if any([role, batting_style, bowling_style, image]):
            break
        retries -= 1
        print(f"Retrying for {primary_name}...")
        time.sleep(2)  # Brief delay before retrying

    # Update player data
    players_data[identifier].update({
        "role": role,
        "batting_style": batting_style,
        "bowling_style": bowling_style,
        "image": image,
    })

    # Fetch player averages
    averages = calculate_player_averages(identifier)
    players_data[identifier].update(averages)

    # Sleep to avoid getting blocked
    time.sleep(5)

# Write data to a new CSV file
with open(output_file, mode="w", newline="") as csvfile:
    fieldnames = [
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
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for player in players_data.values():
        row = {
            "player_id": player["identifier"],
            "names": ", ".join(player["names"]),
            "role": player["role"],
            "batting_style": player["batting_style"],
            "bowling_style": player["bowling_style"],
            "image": player["image"],
        }

        # Add averages to the row
        for column in ["batting_points", "bowling_points", "fielding_points"]:
            averages = player.get(column, {})
            row[f"{column.split('_')[0]}_last_3_avg"] = averages.get("last_3_avg", None)
            row[f"{column.split('_')[0]}_last_5_avg"] = averages.get("last_5_avg", None)
            row[f"{column.split('_')[0]}_last_10_avg"] = averages.get("last_10_avg", None)
            row[f"{column.split('_')[0]}_last_20_avg"] = averages.get("last_20_avg", None)
            row[f"{column.split('_')[0]}_all_matches_avg"] = averages.get("all_matches_avg", None)

        writer.writerow(row)

print(f"Data saved to {output_file}")
