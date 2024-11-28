import csv
import json
import requests
from bs4 import BeautifulSoup
import re
import time

# Input CSV file and output JSON file
csv_file = "test.csv"
output_file = "players_data.json"

# Dictionary to store player data
players_data = {}

# Read the CSV file
with open(csv_file, mode="r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header if present
    for row in reader:
        identifier, name = row

        # Check if the player identifier is already processed
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


# Iterate through players and fetch details
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

    # Sleep to avoid getting blocked
    time.sleep(5)

# Convert sets of names to lists and save to JSON
for player in players_data.values():
    player["names"] = list(player["names"])

with open(output_file, "w") as json_file:
    json.dump(players_data, json_file, indent=4)

print(f"Data saved to {output_file}")
