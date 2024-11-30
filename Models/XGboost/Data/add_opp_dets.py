import os
import pandas as pd

# Paths
player_data_folder = "Datasets/ipl_json_processed"
consolidated_file = "new_dataset.csv"
output_file = "updated_consolidated_dataset.csv"

# Preload all player data into a dictionary
def preload_player_data(folder):
    player_data = {}
    for file_name in os.listdir(folder):
        if file_name.endswith(".csv"):
            player_id = os.path.splitext(file_name)[0]  # Use file name (without extension) as player ID
            file_path = os.path.join(folder, file_name)
            player_data[player_id] = pd.read_csv(file_path)
    return player_data

# Function to get player scores
def get_player_scores(player_id, match_id, score_type, player_data):
    if player_id in player_data:  # Check if player data is preloaded
        match_data = player_data[player_id]
        match_scores = match_data[match_data['match_id'] == match_id]
        if not match_scores.empty:
            return match_scores[score_type].iloc[0]
    return 0  # Default to 0 if no match data found

# Update the consolidated dataset
def update_consolidated_data(consolidated_file, player_data):
    # Load the consolidated dataset
    consolidated_df = pd.read_csv(consolidated_file)

    # Add new columns for each player and opponent player
    for prefix in ['player', 'opponentplayer']:
        for i in range(1, 12):  # player1 to player11, opponentPlayer1 to opponentPlayer11
            if i==11 and prefix=='player':
                continue
            player_col = f"{prefix}{i}"
            match_id_col = 'match_id'

            if player_col in consolidated_df.columns:  # Check if the column exists
                # Bowling points
                consolidated_df[f"{player_col}_bowling_points"] = consolidated_df.apply(
                    lambda row: get_player_scores(row[player_col], row[match_id_col], 'bowling_points', player_data)
                    if not pd.isna(row[player_col]) else 0,
                    axis=1
                )

                # Fielding points
                consolidated_df[f"{player_col}_fielding_points"] = consolidated_df.apply(
                    lambda row: get_player_scores(row[player_col], row[match_id_col], 'fielding_points', player_data)
                    if not pd.isna(row[player_col]) else 0,
                    axis=1
                )

                # Batting points
                consolidated_df[f"{player_col}_batting_points"] = consolidated_df.apply(
                    lambda row: get_player_scores(row[player_col], row[match_id_col], 'batting_points', player_data)
                    if not pd.isna(row[player_col]) else 0,
                    axis=1
                )
            else:
                print(f"Column {player_col} is missing in the dataset.")

    # Save the updated consolidated dataset
    consolidated_df.to_csv(output_file, index=False)
    print(f"Updated consolidated dataset saved to {output_file}")

# Preload all player data
player_data = preload_player_data(player_data_folder)

# Update the consolidated dataset
update_consolidated_data(consolidated_file, player_data)
