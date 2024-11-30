import os
import pandas as pd

# Paths
player_data_folder = "Datasets/ipl_json_processed"
consolidated_file = "avg_new_dataset.csv"
output_file = "avg_updated_consolidated_dataset.csv"

# Preload all player data into a dictionary
def preload_player_data(folder):
    player_data = {}
    for file_name in os.listdir(folder):
        if file_name.endswith(".csv"):
            player_id = os.path.splitext(file_name)[0]  # Use file name (without extension) as player ID
            file_path = os.path.join(folder, file_name)
            df = pd.read_csv(file_path)
            
            # Convert 'date' column to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            player_data[player_id] = df
    return player_data

# Function to calculate the last 5-match averages
def get_last_5_avg(player_id, match_date, score_type, player_data):
    if player_id in player_data:  # Check if player data is preloaded
        player_matches = player_data[player_id]
        # Ensure the 'date' column is in datetime format
        if 'date' in player_matches.columns:
            past_matches = player_matches[player_matches['date'] < match_date]
            last_5_matches = past_matches.tail(5)  # Take only the last 5 matches
            if not last_5_matches.empty:
                return last_5_matches[score_type].mean()
    return 0  # Default to 0 if no match data found

# Update the consolidated dataset with averages
def update_consolidated_averages(consolidated_file, player_data):
    # Load the consolidated dataset
    consolidated_df = pd.read_csv(consolidated_file)
    
    # Convert 'date' column to datetime
    consolidated_df['date'] = pd.to_datetime(consolidated_df['date'], errors='coerce')

    # Add new columns for averages for each player and opponent player
    for prefix in ['player', 'opponentplayer']:
        for i in range(1, 12):  # player1 to player11, opponentPlayer1 to opponentPlayer11
            if i == 11 and prefix == 'player':
                continue
            player_col = f"{prefix}{i}"
            if player_col in consolidated_df.columns:  # Check if the column exists
                # Batting points average
                consolidated_df[f"{player_col}_batting_points"] = consolidated_df.apply(
                    lambda row: get_last_5_avg(row[player_col], row['date'], 'batting_points', player_data)
                    if pd.notna(row[player_col]) else 0,
                    axis=1
                )

                # Bowling points average
                consolidated_df[f"{player_col}_bowling_points"] = consolidated_df.apply(
                    lambda row: get_last_5_avg(row[player_col], row['date'], 'bowling_points', player_data)
                    if pd.notna(row[player_col]) else 0,
                    axis=1
                )

                # Fielding points average
                consolidated_df[f"{player_col}_fielding_points"] = consolidated_df.apply(
                    lambda row: get_last_5_avg(row[player_col], row['date'], 'fielding_points', player_data)
                    if pd.notna(row[player_col]) else 0,
                    axis=1
                )
            else:
                print(f"Column {player_col} is missing in the dataset.")

    # Save the updated consolidated dataset
    consolidated_df.to_csv(output_file, index=False)
    print(f"Updated consolidated dataset with averages saved to {output_file}")

# Preload all player data
player_data = preload_player_data(player_data_folder)

# Update the consolidated dataset with averages
update_consolidated_averages(consolidated_file, player_data)
