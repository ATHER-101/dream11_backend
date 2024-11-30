import os
import pandas as pd
import numpy as np

# Path to the directory containing the CSV files
data_dir = "Datasets/ipl_json_processed"

# List all the CSV files in the directory
files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

# Initialize an empty DataFrame to store consolidated data
consolidated_data = []

# Function to calculate strike rate
def calculate_strike_rate(runs, balls):
    return (runs / balls * 100) if balls > 0 else 0

# Function to calculate economy rate
def calculate_economy_rate(runs_given, balls_bowled):
    overs = balls_bowled / 6
    return (runs_given / overs) if overs > 0 else 10000000000000

# Process each player's file
for file in files:
    file_path = os.path.join(data_dir, file)

    # Read the CSV file
    player_data = pd.read_csv(file_path,parse_dates=['date'], quotechar='"', sep=',')

    # Sort by date to ensure chronological order
    player_data['date'] = pd.to_datetime(player_data['date'])
    player_data = player_data.sort_values(by='date')

    # Initialize a list for storing computed rows
    computed_rows = []

    # Loop through each row in the player's dataset
    for i in range(len(player_data)):
        row = player_data.iloc[i]

        # Calculate metrics
        strike_rate = calculate_strike_rate(row['runs_scored'], row['balls_faced'])
        economy_rate = calculate_economy_rate(row['runs_given'], row['balls_bowled'])

        # Compute averages for the last 5 matches
        if i >= 1:
            last_5_matches = player_data.iloc[max(0, i-5):i]
        else:
            last_5_matches = pd.DataFrame()

        batting_points_avg = last_5_matches['batting_points'].mean() if not last_5_matches.empty else 0
        bowling_points_avg = last_5_matches['bowling_points'].mean() if not last_5_matches.empty else 0
        fielding_points_avg = last_5_matches['fielding_points'].mean() if not last_5_matches.empty else 0

        # Venue average before the current match
        venue_matches = player_data[(player_data['venue'] == row['venue']) & (player_data['date'] <= row['date'])]
        venue_avg = venue_matches['total_fantasy_points'].mean() if not venue_matches.empty else 0

        # Variance in total fantasy points before the current match
        variance = venue_matches['total_fantasy_points'].var() if not venue_matches.empty else 0

        # Append computed metrics
        computed_row = {
            'match_id': row['match_id'],
            'player_id':row['player_id'],
            'date': row['date'],
            'venue': row['venue'],
            'strike_rate': strike_rate,
            'wickets': row['wickets'],
            'maidens': row['maidens'],
            'economy_rate': economy_rate,
            'bowled_lbw': row['bowled_lbw'],
            'catches': row['catches'],
            'stumpings': row['stumpings'],
            'batting_points_avg': batting_points_avg,
            'bowling_points_avg': bowling_points_avg,
            'fielding_points_avg': fielding_points_avg,
            'venue_avg': venue_avg,
            'variance': variance,
            "player1":row['player1'],
            "player2":row['player2'],
            "player3":row['player3'],
            "player4":row['player4'],
            "player5":row['player5'],
            "player6":row['player6'],
            "player7":row['player7'],
            "player8":row['player8'],
            "player9":row['player9'],
            "player10":row['player10'],
            "opponentplayer1":row['opponentplayer1'],
            "opponentplayer2":row['opponentplayer2'],
            "opponentplayer3":row['opponentplayer3'],
            "opponentplayer4":row['opponentplayer4'],
            "opponentplayer5":row['opponentplayer5'],
            "opponentplayer6":row['opponentplayer6'],
            "opponentplayer7":row['opponentplayer7'],
            "opponentplayer8":row['opponentplayer8'],
            "opponentplayer9":row['opponentplayer9'],
            "opponentplayer10":row['opponentplayer10'],
            "opponentplayer11":row['opponentplayer11'],
            "batting_points":row['batting_points'],
            "bowling_points": row['bowling_points'],
            "fielding_points": row['fielding_points'],
            "total_fantasy_points": row['total_fantasy_points']

            
        }
        computed_rows.append(computed_row)

    # Add computed rows to the consolidated dataset
    consolidated_data.extend(computed_rows)

# Create a DataFrame from the consolidated data
consolidated_df = pd.DataFrame(consolidated_data)

# Save the consolidated dataset to a CSV file
consolidated_df.to_csv("new_dataset.csv", index=False)
