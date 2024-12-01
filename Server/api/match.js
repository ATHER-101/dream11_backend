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
        ORDER BY date ASC ${limit?`LIMIT ${limit}`:``};
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
  
  router.get('/match/:match_id', async (req, res) => {
    const { match_id } = req.params;
  
    try {
      // Query to fetch match details
      const matchQuery = `
        SELECT 
          match_id, date, venue, event, match_type, team1, team2, team1_players, team2_players
        FROM matches
        WHERE match_id = $1;
      `;
      const matchResult = await pool.query(matchQuery, [match_id]);
  
      if (matchResult.rows.length === 0) {
        return res.status(404).json({ error: 'Match not found' });
      }
  
      const match = matchResult.rows[0];
  
      // Combine all player IDs from team1 and team2
      const playerIds = [...match.team1_players, ...match.team2_players];
  
      // Query to fetch player details along with longest names
      const playersQuery = `
        SELECT 
          p.player_id,
          pn.name, -- Fetch the longest name
          p.role,
          p.batting_style,
          p.bowling_style,
          p.image
        FROM players p
        JOIN (
          SELECT DISTINCT ON (player_id) 
            player_id, 
            name
          FROM player_names
          ORDER BY player_id, LENGTH(name) DESC -- Select the longest name per player_id
        ) pn ON p.player_id = pn.player_id
        WHERE p.player_id = ANY($1);
      `;
      const playersResult = await pool.query(playersQuery, [playerIds]);
  
      res.status(200).json({
        match_details: {
          match_id: match.match_id,
          date: match.date,
          venue: match.venue,
          event: match.event,
          match_type: match.match_type,
          team1: match.team1,
          team2: match.team2,
        },
        players: playersResult.rows, // All 22 players' details with longest names
      });
    } catch (error) {
      console.error('Error fetching match details:', error.message);
      res.status(500).json({ error: 'An error occurred while fetching match details.' });
    }
  });

module.exports = router;
