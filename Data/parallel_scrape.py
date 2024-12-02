import csv
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# File paths
csv_file = "Datasets/people.csv"
output_file = "players_data_new.csv"

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
        ])

# Read existing data from the output file to avoid duplicates
try:
    existing_data = pd.read_csv(output_file)
    processed_ids = set(existing_data["player_id"].astype(str))
except FileNotFoundError:
    processed_ids = set()

# Function to fetch player details
def fetch_player_details(player_id, player_name):
    try:
        search_url = f"https://www.google.com/search?q={player_name}%20cricbuzz"
        response = requests.get(search_url, timeout=10)
        search_page = BeautifulSoup(response.text, "lxml")
        link_div = search_page.find("div", class_="kCrYT")
        if not link_div:
            return player_id, player_name, None, None, None, None

        link = link_div.find("a", href=re.compile(r"[/]([a-z]|[A-Z])\w+"))
        if not link:
            return player_id, player_name, None, None, None, None

        cricbuzz_url = link["href"][7:]  # Remove '/url?q=' prefix
        cricbuzz_response = requests.get(cricbuzz_url, timeout=10).text
        cricbuzz_page = BeautifulSoup(cricbuzz_response, "lxml")

        profile_section = cricbuzz_page.find("div", class_="cb-col cb-col-100 cb-bg-grey")
        if not profile_section:
            return player_id, player_name, None, None, None, None

        # Extract data
        role = profile_section.find("div", text="Role").find_next_sibling("div").text.strip() if profile_section.find("div", text="Role") else None
        batting_style = profile_section.find("div", text="Batting Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Batting Style") else None
        bowling_style = profile_section.find("div", text="Bowling Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Bowling Style") else None
        image = cricbuzz_page.find("img", {"title": "profile image"})["src"] if cricbuzz_page.find("img", {"title": "profile image"}) else None

        return player_id, player_name, role, batting_style, bowling_style, image
    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
        return player_id, player_name, None, None, None, None

# Function to write results to the output file
def write_to_file(results):
    with open(output_file, mode="a", newline="") as outfile:
        writer = csv.writer(outfile)
        for result in results:
            writer.writerow(result)

# Read input CSV and prepare data
with open(csv_file, mode="r") as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header
    players_to_process = [(player_id, name) for player_id, name in reader if player_id not in processed_ids]

# Parallelize the fetching of player details
results = []
with ThreadPoolExecutor(max_workers=10) as executor:  # Use 10 threads (adjust based on system capability)
    future_to_player = {executor.submit(fetch_player_details, player_id, name): (player_id, name) for player_id, name in players_to_process}
    for future in as_completed(future_to_player):
        result = future.result()
        results.append(result)
        print(f"Processed: {result[1]} (ID: {result[0]})")

        # Write each result to the file immediately to ensure progress is saved
        write_to_file([result])

print("Data collection completed.")
