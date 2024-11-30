# import json
# import csv
# import os
# from collections import defaultdict
# from fantasy_calculator import fantasy_calculator  # Import the fantasy_calculator function

# def process_match_data(json_file, output_folder):
#     # Load JSON data
#     with open(json_file, 'r') as f:
#         data = json.load(f)

#     # Extract match info
#     match_date = data["info"]["dates"][0]
#     venue = data["info"]["venue"]
#     event = data["info"].get("event", {}).get("name", "Unknown Event")
#     match_type = data["info"]["match_type"]
#     total_overs = data["info"]["overs"]
#     toss_winner = data["info"]["toss"]["winner"]
#     toss_decision = data["info"]["toss"]["decision"]
#     teams = data["info"]["teams"]
#     innings_data = data["innings"]

#     # Map player names to player IDs using the 'registry' section
#     player_id_map = {name: str(player_id) for name, player_id in data["info"]["registry"]["people"].items()}
    
#     # Map players to their respective teams
#     player_team_map = {}
#     for team in teams:
#         for player in data["info"]["players"][team]:
#             player_team_map[player] = team

#     # Prepare player stats dictionary
#     player_stats = defaultdict(lambda: {
#         "date": match_date,
#         "venue": venue,
#         "event": event,
#         "match_type": match_type,
#         "total_overs": total_overs,
#         "team": None,
#         "runs_scored": 0,
#         "balls_faced": 0,
#         "boundaries": 0,
#         "sixes": 0,
#         "balls_bowled": 0,
#         "wickets": 0,
#         "runs_given": 0,
#         "bowled_lbw": 0,
#         "maidens": 0,
#         "catches": 0,
#         "stumpings": 0,
#         "run_outs": 0
#     })

#     # Initialize player stats with team information from the rosters
#     for player, team in player_team_map.items():
#         player_stats[player]["team"] = team

#     # Process innings
#     for inning in innings_data:
#         team = inning["team"]
#         overs = inning.get("overs", [])
#         for over in overs:
#             maidens_flag = True  # To track maiden overs
#             for delivery in over["deliveries"]:
#                 # Batting stats
#                 batter = delivery["batter"]
#                 bowler = delivery["bowler"]
#                 runs = delivery["runs"]["batter"]
#                 player_stats[batter]["runs_scored"] += runs
#                 player_stats[batter]["balls_faced"] += 1
#                 if runs == 4:
#                     player_stats[batter]["boundaries"] += 1
#                 if runs == 6:
#                     player_stats[batter]["sixes"] += 1

#                 # Wicket stats
#                 if "wickets" in delivery:
#                     for wicket in delivery["wickets"]:
#                         kind = wicket["kind"]
#                         player_out = wicket["player_out"]

#                         # Increment the bowler's wickets
#                         player_stats[bowler]["wickets"] += 1

#                         if kind in {"bowled", "lbw"}:
#                             player_stats[bowler]["bowled_lbw"] += 1
#                         if kind == "caught":
#                             for fielder in wicket.get("fielders", []):
#                                 player_stats[fielder["name"]]["catches"] += 1
#                         if kind == "stumped":
#                             player_stats[bowler]["stumpings"] += 1
#                         if kind == "run out":
#                             for fielder in wicket.get("fielders", []):
#                                 player_stats[fielder["name"]]["run_outs"] += 1

#                 # Bowling stats
#                 if "extras" not in delivery or "wides" not in delivery["extras"] and "no_balls" not in delivery["extras"]:
#                     player_stats[bowler]["balls_bowled"] += 1  # Count only legitimate balls

#                 player_stats[bowler]["runs_given"] += delivery["runs"]["total"]
#                 if delivery["runs"]["total"] > 0 or "extras" in delivery:
#                     maidens_flag = False

#             # Update maidens if all deliveries in the over were zero runs
#             if maidens_flag:
#                 player_stats[bowler]["maidens"] += 1

#     # Add opponent playing XI
#     for player in player_stats:
#         team = player_stats[player]["team"]
#         opponent_team = teams[1] if teams[0] == team else teams[0]
#         opponent_playing_xi = data["info"]["players"].get(opponent_team, [])
#         for i, opponent_player in enumerate(opponent_playing_xi[:11]):
#             # Validate opponent player and assign default if missing
#             player_stats[player][f"player{i+1}"] = player_id_map.get(opponent_player, "Unknown_Player")

#         # Validate opponent player columns before writing
#         for i in range(11):
#             col_name = f"player{i+1}"
#             if not isinstance(player_stats[player][col_name], str):
#                 player_stats[player][col_name] = "Unknown_Player"

#     # Create 'player_data' folder if it does not exist
#     os.makedirs(output_folder, exist_ok=True)

#     # Write to individual player CSV files
#     for player, stats in player_stats.items():
#         # Get player ID from the map
#         player_id = player_id_map.get(player, player)  # Fallback to player name if ID is not found

#         # Define player file path
#         player_file = os.path.join(output_folder, f"{player_id}.csv")
        
#         # Check if file exists, if not create it with header
#         file_exists = os.path.isfile(player_file)
        
#         header = [
#             "date", "venue", "event", "match_type", "total_overs", "player_id", "team",
#             "runs_scored", "balls_faced", "boundaries", 
#             "sixes", "balls_bowled", "wickets", "runs_given", "bowled_lbw", 
#             "maidens", "catches", "stumpings", "run_outs", 
#             "batting_points", "bowling_points", "fielding_points", "total_fantasy_points",
#             "player1", "player2", "player3", "player4", "player5", "player6", 
#             "player7", "player8", "player9", "player10", "player11"
#         ]
        
#         # Open the player CSV file
#         with open(player_file, 'a', newline='') as f:
#             writer = csv.writer(f)
#             # Write the header if the file does not exist
#             if not file_exists:
#                 writer.writerow(header)
            
#             # Calculate fantasy points
#             batting_points, bowling_points, fielding_points, total_fantasy_points = fantasy_calculator(stats)
            
#             # Prepare data for this row
#             row = [stats[col] if col in stats else 0 for col in header[:-15]]  # Exclude fantasy point and opponent columns
#             row[5] = player_id  # Replace with player_id (instead of player name)
#             row.extend([batting_points, bowling_points, fielding_points, total_fantasy_points])
#             row.extend([stats.get(f"player{i+1}", "Unknown_Player") for i in range(11)])  # Add opponent columns
#             writer.writerow(row)

# # Usage example
# # process_match_data("./ipl_json/335985.json", "player_data")

import json
import csv
import os
from collections import defaultdict
from fantasy_calculator import fantasy_calculator  # Import the fantasy_calculator function

def process_match_data(json_file, output_folder):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract match info
    match_date = data["info"]["dates"][0]
    venue = data["info"]["venue"]
    event = data["info"].get("event", {}).get("name", "Unknown Event")
    match_type = data["info"]["match_type"]
    total_overs = data["info"]["overs"]
    toss_winner = data["info"]["toss"]["winner"]
    toss_decision = data["info"]["toss"]["decision"]
    teams = data["info"]["teams"]
    innings_data = data["innings"]

    # Map player names to player IDs using the 'registry' section
    player_id_map = {name: str(player_id) for name, player_id in data["info"]["registry"]["people"].items()}
    
    # Map players to their respective teams
    player_team_map = {}
    for team in teams:
        for player in data["info"]["players"][team]:
            player_team_map[player] = team

    # Prepare player stats dictionary
    player_stats = defaultdict(lambda: {
        "date": match_date,
        "venue": venue,
        "event": event,
        "match_type": match_type,
        "total_overs": total_overs,
        "team": None,
        "runs_scored": 0,
        "balls_faced": 0,
        "boundaries": 0,
        "sixes": 0,
        "balls_bowled": 0,
        "wickets": 0,
        "runs_given": 0,
        "bowled_lbw": 0,
        "maidens": 0,
        "catches": 0,
        "stumpings": 0,
        "run_outs": 0
    })

    # Initialize player stats with team information from the rosters
    for player, team in player_team_map.items():
        player_stats[player]["team"] = team

    # Process innings
    for inning in innings_data:
        team = inning["team"]
        overs = inning.get("overs", [])
        for over in overs:
            maidens_flag = True  # To track maiden overs
            for delivery in over["deliveries"]:
                # Batting stats
                batter = delivery["batter"]
                bowler = delivery["bowler"]
                runs = delivery["runs"]["batter"]
                player_stats[batter]["runs_scored"] += runs
                player_stats[batter]["balls_faced"] += 1
                if runs == 4:
                    player_stats[batter]["boundaries"] += 1
                if runs == 6:
                    player_stats[batter]["sixes"] += 1

                # Wicket stats
                if "wickets" in delivery:
                    for wicket in delivery["wickets"]:
                        kind = wicket["kind"]
                        player_out = wicket["player_out"]

                        # Increment the bowler's wickets
                        player_stats[bowler]["wickets"] += 1

                        if kind in {"bowled", "lbw"}:
                            player_stats[bowler]["bowled_lbw"] += 1
                        if kind == "caught":
                            for fielder in wicket.get("fielders", []):
                                player_stats[fielder["name"]]["catches"] += 1
                        if kind == "stumped":
                            player_stats[bowler]["stumpings"] += 1
                        if kind == "run out":
                            for fielder in wicket.get("fielders", []):
                                player_stats[fielder["name"]]["run_outs"] += 1

                # Bowling stats
                if "extras" not in delivery or "wides" not in delivery["extras"] and "no_balls" not in delivery["extras"]:
                    player_stats[bowler]["balls_bowled"] += 1  # Count only legitimate balls

                player_stats[bowler]["runs_given"] += delivery["runs"]["total"]
                if delivery["runs"]["total"] > 0 or "extras" in delivery:
                    maidens_flag = False

            # Update maidens if all deliveries in the over were zero runs
            if maidens_flag:
                player_stats[bowler]["maidens"] += 1

    # Add opponent playing XI
    for player in player_stats:
        team = player_stats[player]["team"]
        opponent_team = teams[1] if teams[0] == team else teams[0]
        opponent_playing_xi = data["info"]["players"].get(opponent_team, [])
        
        for i, opponent_player in enumerate(opponent_playing_xi[:11]):
            # Validate opponent player and assign default if missing
            player_stats[player][f"player{i+1}"] = str(player_id_map.get(opponent_player, "Unknown_Player"))

        # Validate opponent player columns before writing
        for i in range(11):
            col_name = f"player{i+1}"
            if not isinstance(player_stats[player][col_name], str):
                player_stats[player][col_name] = "Unknown_Player"

    # Create 'player_data' folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Write to individual player CSV files
    for player, stats in player_stats.items():
        # Get player ID from the map
        player_id = str(player_id_map.get(player, f"Unknown_{player}"))  # Fallback to player name if ID is not found
        player_file = os.path.join(output_folder, f"{player_id}.csv")
        
        print(f"Processing player: {player}, Player ID: {player_id}, File: {player_file}")  # Debugging statement
        
        # Check if file exists, if not create it with header
        file_exists = os.path.isfile(player_file)
        
        header = [
            "date", "venue", "event", "match_type", "total_overs", "player_id", "team",
            "runs_scored", "balls_faced", "boundaries", 
            "sixes", "balls_bowled", "wickets", "runs_given", "bowled_lbw", 
            "maidens", "catches", "stumpings", "run_outs", 
            "batting_points", "bowling_points", "fielding_points", "total_fantasy_points",
            "player1", "player2", "player3", "player4", "player5", "player6", 
            "player7", "player8", "player9", "player10", "player11"
        ]
        
        # Open the player CSV file
        with open(player_file, 'a', newline='') as f:
            writer = csv.writer(f)
            # Write the header if the file does not exist
            if not file_exists:
                writer.writerow(header)
            
            # Calculate fantasy points
            batting_points, bowling_points, fielding_points, total_fantasy_points = fantasy_calculator(stats)
            
            # Prepare data for this row
            row = [str(stats[col]) if col in stats else "0" for col in header[:-15]]  # Ensure string type for all stats
            row[5] = player_id  # Replace with player_id (instead of player name)
            row.extend([batting_points, bowling_points, fielding_points, total_fantasy_points])
            row.extend([str(stats.get(f"player{i+1}", "Unknown_Player")) for i in range(11)])  # Add opponent columns
            writer.writerow(row)

# Usage example
# process_match_data("./ipl_json/335985.json", "player_data")
