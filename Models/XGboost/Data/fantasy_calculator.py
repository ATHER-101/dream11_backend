def fantasy_calculator(data):
    points = 0
    batting_points = 0
    bowling_points = 0
    fielding_points = 0
    # Batting Points
    runs = data['runs_scored']
    balls_faced = data['balls_faced']
    boundaries = data['boundaries']
    sixes = data['sixes']
    match_type = data['match_type']

    points += runs  # Points for runs
    points += boundaries  # Boundary bonus
    points += sixes * 2  # Six bonus

    # 30/50/100 Run Bonuses
    if runs >= 100 and match_type != "T10":
        points += 16
    elif runs >= 50:
        points += 8
    elif runs >= 30:
        points += 4

    # Duck Penalty
    if runs == 0 and balls_faced > 0:
        points -= 2

    # Strike Rate Points (min 10 balls faced)
    if balls_faced >= 10:
        strike_rate = (runs / balls_faced) * 100
        if strike_rate > 170:
            points += 6
        elif strike_rate > 150:
            points += 4
        elif strike_rate > 130:
            points += 2
        elif strike_rate < 70:
            if strike_rate >= 60:
                points -= 2
            elif strike_rate >= 50:
                points -= 4
            else:
                points -= 6
    batting_points = points
    # Bowling Points
    wickets = data['wickets']
    bowled_lbw = data['bowled_lbw']
    maidens = data['maidens']
    runs_given = data['runs_given']
    balls_bowled = data['balls_bowled']

    points += wickets * 25
    points += bowled_lbw * 8
    points += maidens * 12

    if wickets >= 5:
        points += 16
    elif wickets >= 4:
        points += 8
    elif wickets >= 3:
        points += 4

    # Economy Rate Points (min 2 overs bowled)
    if balls_bowled >= 12:
        overs_bowled = balls_bowled / 6
        economy_rate = runs_given / overs_bowled

        if economy_rate < 5:
            points += 6
        elif economy_rate < 6:
            points += 4
        elif economy_rate < 7:
            points += 2
        elif economy_rate > 12:
            points -= 6
        elif economy_rate > 11:
            points -= 4
        elif economy_rate > 10:
            points -= 2
    bowling_points = points - batting_points
    # Fielding Points
    catches = data['catches']
    stumpings = data['stumpings']
    run_outs = data['run_outs']

    points += catches * 8
    if catches >= 3:
        points += 4  # 3 Catch Bonus, only once
    points += stumpings * 12

    # Run outs (Direct hit vs Not direct hit)
    # run_out_direct = data['run_out_direct']
    # run_out_indirect = run_outs - run_out_direct

    # points += run_out_direct * 12
    points += run_outs * 6
    fielding_points = points - batting_points - bowling_points
    return [batting_points, bowling_points, fielding_points, points]

# # Example usage
# data = {
#     'runs_scored': 75,
#     'match_type': 'ODI',
#     'total_overs': 50,
#     'balls_faced': 50,
#     'boundaries': 8,
#     'sixes': 3,
#     'balls_bowled': 60,
#     'wickets': 3,
#     'runs_given': 45,
#     'bowled_lbw': 2,
#     'maidens': 1,
#     'catches': 2,
#     'stumpings': 1,
#     'run_outs': 3,
#     'run_out_direct': 1
# }

# fantasy_points = fantasy_calculator(data)
# print(f"Fantasy Points: {fantasy_points}")