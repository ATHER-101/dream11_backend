import csv
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re

# Paths for the input CSV and output CSV
csv_file = "players_data.csv"
output_file = "players_data.csv"

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


# Load the existing CSV into a DataFrame
df = pd.read_csv(csv_file)

# Columns to check for missing data
columns_to_check = ["role", "batting_style", "bowling_style", "image"]

# Identify rows with missing data
missing_data = df[df[columns_to_check].isnull().any(axis=1)]

print(f"Found {len(missing_data)} rows with missing data.")

# Retry scraping for rows with missing data
for index, row in missing_data.iterrows():
    player_id = row["player_id"]
    player_names = row["names"]

    # Use the first name from the names list for scraping
    primary_name = player_names.split(",")[0].strip()

    print(f"Retrying scraping for player: {primary_name} (ID: {player_id})")

    retries = 3
    while retries > 0:
        role, batting_style, bowling_style, image = fetch_player_details(primary_name)
        if any([role, batting_style, bowling_style, image]):
            break
        retries -= 1
        print(f"Retrying for {primary_name}... ({3 - retries}/3)")
        time.sleep(2)

    # Update the DataFrame with the newly scraped data
    if role:
        df.loc[index, "role"] = role
    if batting_style:
        df.loc[index, "batting_style"] = batting_style
    if bowling_style:
        df.loc[index, "bowling_style"] = bowling_style
    if image:
        df.loc[index, "image"] = image

    # Delay to avoid getting blocked
    time.sleep(5)

# Save the updated DataFrame to a new CSV file
df.to_csv(output_file, index=False)
print(f"Updated data saved to {output_file}.")
