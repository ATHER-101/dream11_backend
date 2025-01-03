const fs = require('fs');
const csvParser = require('csv-parser');
const pool = require('./db'); // PostgreSQL connection pool

async function processCSV(filePath) {
  const rows = [];

  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csvParser())
      .on('data', (row) => {
        rows.push(row);
      })
      .on('end', async () => {
        try {
          // Extract match-level metadata and players
          const matchData = await transformToMatchData(rows);

          // Insert match data into the database
          await insertMatchData(matchData);

          resolve();
        } catch (err) {
          reject(err);
        }
      })
      .on('error', (err) => {
        reject(err);
      });
  });
}

// Transform CSV rows into match-level data with player IDs
async function transformToMatchData(rows) {
  const matchDate = rows[0]['Match Date'];
  const matchType = rows[0]['Format'];

  // Group players by team
  const teams = {};
  rows.forEach((row) => {
    const team = row['Squad'];
    if (!teams[team]) {
      teams[team] = [];
    }
    teams[team].push(row['Player Name']);
  });

  const [team1, team2] = Object.keys(teams);
  const team1Players = await getPlayerIds(teams[team1]);
  const team2Players = await getPlayerIds(teams[team2]);

  return {
    date: matchDate,
    venue: null, // Set venue manually or from additional data
    event: null, // Set event manually or from additional data
    matchType,
    team1,
    team2,
    team1Players,
    team2Players,
    matchId: generateMatchId(matchDate, team1, team2), // Generate a unique match ID
  };
}

// Generate a unique match ID
function generateMatchId(date, team1, team2) {
  return `${date}-${team1.replace(/\s+/g, '_')}-vs-${team2.replace(/\s+/g, '_')}`;
}

// Get player IDs for an array of player names
async function getPlayerIds(playerNames) {
  const playerIds = [];

  for (const name of playerNames) {
    let playerId = await getPlayerIdFromPlayers(name);
    if (!playerId) {
      playerId = await getPlayerIdFromNames(name);
    }

    if (!playerId) {
      throw new Error(`Player ID not found for name: ${name}`);
    }

    playerIds.push(playerId);
  }

  return playerIds;
}

// Query the `players` table for a player's ID
async function getPlayerIdFromPlayers(name) {
  const query = 'SELECT player_id FROM players WHERE name = $1';
  const result = await pool.query(query, [name]);

  return result.rows.length > 0 ? result.rows[0].player_id : null;
}

// Query the `names` table for a player's ID
async function getPlayerIdFromNames(name) {
  const query = 'SELECT player_id FROM names WHERE name = $1';
  const result = await pool.query(query, [name]);

  return result.rows.length > 0 ? result.rows[0].player_id : null;
}

// Insert match data into PostgreSQL
async function insertMatchData(matchData) {
  const query = `
    INSERT INTO matches (
      date,
      venue,
      event,
      match_type,
      team1,
      team2,
      team1_players,
      match_id,
      team2_players
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (match_id) DO NOTHING;
  `;

  const values = [
    matchData.date,
    matchData.venue,
    matchData.event,
    matchData.matchType,
    matchData.team1,
    matchData.team2,
    matchData.team1Players,
    matchData.matchId,
    matchData.team2Players,
  ];

  await pool.query(query, values);
}

module.exports = processCSV;
