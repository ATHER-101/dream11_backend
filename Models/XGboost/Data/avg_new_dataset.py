import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv("new_dataset.csv", parse_dates=['date'])

# Ensure data is sorted by player and date
data = data.sort_values(by=['player_id', 'date'])

# List of numeric columns to compute averages
numeric_columns = ['strike_rate', 'wickets', 'maidens', 'economy_rate', 'bowled_lbw', 'catches', 'stumpings']

# Initialize a new DataFrame for results
results = []

# Group data by player
grouped = data.groupby('player_id')

# Compute rolling averages for each player
for player_id, group in grouped:
    # Sort the player's matches by date
    group = group.sort_values(by='date').reset_index(drop=True)
    
    # Loop through each match for the player
    for i, row in group.iterrows():
        # Get matches played before the current match (up to 5)
        previous_matches = group.iloc[max(0, i - 5):i]
        
        # Compute averages for numeric columns
        averages = {col: previous_matches[col].mean() if not previous_matches.empty else np.nan for col in numeric_columns}
        
        # Replace current row's numeric columns with the computed averages
        updated_row = row.to_dict()
        for col, avg_value in averages.items():
            updated_row[col] = avg_value
        
        # Append the updated row to results
        results.append(updated_row)

# Create a DataFrame from the results
averaged_data = pd.DataFrame(results)

# Save the new dataset to a CSV file
averaged_data.to_csv("avg_new_dataset.csv", index=False)

print("Averages computed and dataset saved.")
