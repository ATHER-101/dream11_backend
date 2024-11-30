import pandas as pd
import os

# Path to the folder containing player CSV files
player_data_folder = "C:/Users/itsme/OneDrive/Documents/GitHub/dream11_backend/Data/Datasets/ipl_json_processed"

# Load the people(1).csv file
people_file_path = "C:/Users/itsme/OneDrive/Documents/GitHub/dream11_backend/Data/Datasets/people (1).csv"
people_df = pd.read_csv(people_file_path)

# Ensure 'player_id' is treated as a string in both datasets
people_df['player_id'] = people_df['player_id'].astype(str)

# Function to calculate rolling averages based on the latest matches
def compute_rolling_averages(player_df, num_games, point_type):
    # Sort the data by date to ensure calculations use the latest games
    player_df['date'] = pd.to_datetime(player_df['date'])
    player_df = player_df.sort_values('date', ascending=False)
    
    # Select the latest 'num_games' rows
    recent_games = player_df.head(num_games)
    
    # Compute the average for the specified point type
    return recent_games[point_type].mean()

# Initialize a list to track players whose data is updated
updated_players = []

# Process each player's file
for file_name in os.listdir(player_data_folder):
    if file_name.endswith('.csv'):
        # Extract player_id from the filename
        player_id = file_name.split('.')[0]  # Keep player_id as a string
        
        # Load the player's data
        player_file_path = os.path.join(player_data_folder, file_name)
        player_df = pd.read_csv(player_file_path)
        
        # Check if the player exists in the people dataframe
        if player_id in people_df['player_id'].values:
            # Calculate averages
            averages = {
                'last_3_batting_avg': compute_rolling_averages(player_df, 3, 'batting_points'),
                'last_3_bowling_avg': compute_rolling_averages(player_df, 3, 'bowling_points'),
                'last_3_fielding_avg': compute_rolling_averages(player_df, 3, 'fielding_points'),
                'last_5_batting_avg': compute_rolling_averages(player_df, 5, 'batting_points'),
                'last_5_bowling_avg': compute_rolling_averages(player_df, 5, 'bowling_points'),
                'last_5_fielding_avg': compute_rolling_averages(player_df, 5, 'fielding_points'),
                'last_10_batting_avg': compute_rolling_averages(player_df, 10, 'batting_points'),
                'last_10_bowling_avg': compute_rolling_averages(player_df, 10, 'bowling_points'),
                'last_10_fielding_avg': compute_rolling_averages(player_df, 10, 'fielding_points'),
                'last_20_batting_avg': compute_rolling_averages(player_df, 20, 'batting_points'),
                'last_20_bowling_avg': compute_rolling_averages(player_df, 20, 'bowling_points'),
                'last_20_fielding_avg': compute_rolling_averages(player_df, 20, 'fielding_points'),
                'overall_batting_avg': player_df['batting_points'].mean(),
                'overall_bowling_avg': player_df['bowling_points'].mean(),
                'overall_fielding_avg': player_df['fielding_points'].mean(),
            }
            
            # Update the respective row in people_df
            for col, value in averages.items():
                people_df.loc[people_df['player_id'] == player_id, col] = value  # Compare as string
            
            # Track updated players
            updated_players.append(player_id)
        else:
            print(f"Player ID {player_id} not found in people_df. Skipping...")

# Fill empty cells with 0
people_df.fillna(0, inplace=True)

# Save the updated people(1).csv file
people_df.to_csv(people_file_path, index=False)

# Log the results
print(f"Updated averages for {len(updated_players)} players.")
if len(updated_players) < len(os.listdir(player_data_folder)):
    print(f"Some players in {player_data_folder} did not match with people_df.")
