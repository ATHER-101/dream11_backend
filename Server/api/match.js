const express = require('express');
const pool = require('../db');
const router = express.Router();

// Route to get matches after a specified date
router.get('/matches', async (req, res) => {
    // const { after_date } = req.query;
    const after_date = '2023-08-01';
    const { limit } = req.query;

    // Validate the provided date
    if (!after_date) {
        return res.status(400).json({ error: 'Please provide an "after_date" query parameter in YYYY-MM-DD format.' });
    }

    try {
        // Query to get matches after the specified date
        const query = `
        SELECT * 
        FROM matches
        WHERE date > $1
        ORDER BY date ASC ${limit ? `LIMIT ${limit}` : ``};
      `;
        const result = await pool.query(query, [after_date]);

        res.status(200).json({
            message: `Matches after ${after_date}`,
            matches: result.rows,
        });
    } catch (error) {
        console.error('Error fetching matches:', error.message);
        res.status(500).json({ error: 'An error occurred while fetching matches.' });
    }
});

router.get('/match/:matchId', async (req, res) => {
  const { matchId } = req.params;

  try {
    // Step 1: Fetch match details
    const matchQuery = `
      SELECT 
        match_id, date, venue, event, match_type, team1, team2, team1_players, team2_players 
      FROM matches 
      WHERE match_id = $1;
    `;
    const matchResult = await pool.query(matchQuery, [matchId]);

    if (matchResult.rows.length === 0) {
      return res.status(404).json({ error: 'Match not found' });
    }

    const match = matchResult.rows[0];

    // Step 2: Fetch player details for both teams
    const playersQuery = `
      SELECT 
        player_id, 
        name, 
        role, 
        batting_style, 
        bowling_style, 
        image
      FROM players
      WHERE player_id = ANY($1);
    `;

    const team1PlayerDetails = await pool.query(playersQuery, [match.team1_players]);
    const team2PlayerDetails = await pool.query(playersQuery, [match.team2_players]);

    // Add player details directly to team1_players and team2_players
    const detailedTeam1Players = match.team1_players.map((playerId) =>
      team1PlayerDetails.rows.find((player) => player.player_id === playerId) || { player_id: playerId, name: 'Unknown' }
    );
    const detailedTeam2Players = match.team2_players.map((playerId) =>
      team2PlayerDetails.rows.find((player) => player.player_id === playerId) || { player_id: playerId, name: 'Unknown' }
    );

    // Build the response
    const response = {
      match_details: {
        match_id: match.match_id,
        date: match.date,
        venue: match.venue,
        event: match.event,
        match_type: match.match_type,
        team1: match.team1,
        team2: match.team2,
      },
      team1_players: detailedTeam1Players,
      team2_players: detailedTeam2Players,
    };

    res.json(response);
  } catch (error) {
    console.error('Error fetching match players:', error);
    res.status(500).json({ error: 'An error occurred while fetching match data' });
  }
});



module.exports = router;
