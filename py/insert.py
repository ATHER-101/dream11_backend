import pandas as pd

# Load the CSV file into a DataFrame
file_path = "../Data/players_data.csv"  # Replace with your CSV file path
df = pd.read_csv(file_path)

# Define the important fields to prioritize
important_fields = ["role", "batting_style", "bowling_style", "image"]

# Group by 'player_id' and pick the row with the most fields filled (including prioritization)
filtered_df = (
    df.groupby("player_id", group_keys=False)
    .apply(lambda group: group.loc[group[important_fields].notna().sum(axis=1).idxmax()])
)

# Select only the required columns
filtered_df = filtered_df[["player_id", "role", "batting_style", "bowling_style", "image"]]

# Reset index to make it a clean DataFrame
filtered_df.reset_index(drop=True, inplace=True)

# Save the filtered data back to a new CSV file
output_file = "filtered_players.csv"
filtered_df.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
