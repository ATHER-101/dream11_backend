import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

# Paths
ipl_folder = 'C:/Users/itsme/OneDrive/Documents/GitHub/dream11_backend/Data/Datasets/ipl_json_processed'
people_file = 'C:/Users/itsme/OneDrive/Documents/GitHub/dream11_backend/Data/Datasets/people.csv'

# Load people data
people_data = pd.read_csv(people_file)

# Combine all player CSV files
def load_ipl_data(folder):
    data = []
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            player_id = os.path.splitext(file)[0]
            player_data = pd.read_csv(os.path.join(folder, file))
            player_data['player_id'] = player_id
            data.append(player_data)
    return pd.concat(data, ignore_index=True)

ipl_data = load_ipl_data(ipl_folder)
print("loaded_data")
print(ipl_data[:5])

# Feature extraction
def extract_features(row, people_data):
    player_id = row['player_id']
    opponent_ids = row[['player1', 'player2', 'player3', 'player4', 'player5', 
                        'player6', 'player7', 'player8', 'player9', 'player10', 
                        'player11']].dropna().values
    
    # Player features: All batting and bowling averages
    player_stats = people_data[people_data['player_id'] == player_id]
    batting_averages = player_stats[
        ['last_3_batting_avg', 'last_5_batting_avg', 'last_10_batting_avg', 
         'last_20_batting_avg', 'overall_batting_avg']
    ].values.flatten()
    bowling_averages = player_stats[
        ['last_3_bowling_avg', 'last_5_bowling_avg', 'last_10_bowling_avg', 
         'last_20_bowling_avg', 'overall_bowling_avg']
    ].values.flatten()
    
    # Opponent features: All batting and bowling averages
    opponent_data = people_data[people_data['player_id'].isin(opponent_ids)]
    opponent_batting_averages = opponent_data[
        ['last_3_batting_avg', 'last_5_batting_avg', 'last_10_batting_avg', 
         'last_20_batting_avg', 'overall_batting_avg']
    ].values.flatten()
    opponent_bowling_averages = opponent_data[
        ['last_3_bowling_avg', 'last_5_bowling_avg', 'last_10_bowling_avg', 
         'last_20_bowling_avg', 'overall_bowling_avg']
    ].values.flatten()
    
    # Combine features
    return np.concatenate([batting_averages, bowling_averages, opponent_batting_averages, opponent_bowling_averages])


# Prepare dataset
X, y = [], []
for _, row in ipl_data.iterrows():
    features = extract_features(row, people_data)
    X.append(features)
    y.append([row['batting_points'], row['bowling_points'], row['fielding_points']])

X = np.array(X)
y = np.array(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Neural network model
model = Sequential([
    Dense(64, activation='relu', input_dim=X_train.shape[1]),
    Dense(32, activation='relu'),
    Dense(3, activation='linear')  # Outputs: Batting, Bowling, Fielding points
])

model.compile(optimizer='adam', loss='mae')
# model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))
# Train the model
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# Save the trained model
model.save('fantasy_team_model.h5')
print("Model saved as fantasy_team_model.h5")

# Predict fantasy team
def select_fantasy_team(match_data, model, people_data):
    predictions = {}
    
    # Loop through all players in the match
    for player_id in match_data['player_id']:
        # Extract features for the player
        player_row = match_data[match_data['player_id'] == player_id].iloc[0]
        features = extract_features(player_row, people_data)
        
        # Predict total fantasy points
        predictions[player_id] = model.predict(features[np.newaxis, :]).sum()
    
    # Select the top 11 players with the highest predicted points
    return sorted(predictions.keys(), key=lambda x: predictions[x], reverse=True)[:11]



# Load the saved model
model = load_model('fantasy_team_model.h5')

# Define your teams
team1 = ["db584dad","c3a96caf",	"12b610c2",	"99d63244",	"4329fbb5",	"dc9dd038"	,"bd17b45f",	"957532de",	"245c97cb",	"57ee1fde",	"18e6906e"]  # Replace with actual player IDs
team2 = ["dcce6f09",	"0a476045",	"32198ae0"	,"1c914163"	,"73ad96ed",	"2e11c706",	"890946a0","c18496e1"	,"2e81a32d"	,"96fd40ae",	"5f547c8b"]
match_data = pd.DataFrame({
    'player_id': team1 + team2,
    'player_ids': team1 + team2,
})

# Predict the best fantasy team
best_team = select_fantasy_team(match_data, model, people_data)
print("Best Fantasy Team:", best_team)

