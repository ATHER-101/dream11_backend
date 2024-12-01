const fs = require('fs');
const csv = require('csv-parser');
const pool = require('./db');

const BATCH_SIZE = 50; // Number of rows to insert per batch

const insertMatches = async (rows) => {
  const client = await pool.connect();
  try {
    for (let i = 0; i < rows.length; i += BATCH_SIZE) {
      const batch = rows.slice(i, i + BATCH_SIZE);

      const query = `
        INSERT INTO matches (
          match_id, date, venue, event, match_type, team1, team2,
          team1_players, team2_players
        )
        VALUES ${batch.map(
          (_, idx) =>
            `($${idx * 9 + 1}, $${idx * 9 + 2}, $${idx * 9 + 3}, $${idx * 9 + 4}, $${idx * 9 + 5}, $${idx * 9 + 6}, $${idx * 9 + 7}, $${idx * 9 + 8}, $${idx * 9 + 9})`
        ).join(',')}
        ON CONFLICT (match_id) DO NOTHING;
      `;

      // Flatten batch data into a single array for parameterized query
      const values = batch.flatMap((row) => [
        row.match_id,
        row.date,
        row.venue,
        row.event,
        row.match_type,
        row.team1,
        row.team2,
        `{${[
          row.player1_1,
          row.player1_2,
          row.player1_3,
          row.player1_4,
          row.player1_5,
          row.player1_6,
          row.player1_7,
          row.player1_8,
          row.player1_9,
          row.player1_10,
          row.player1_11,
        ].join(',')}}`, // Team1 players as an array
        `{${[
          row.player2_1,
          row.player2_2,
          row.player2_3,
          row.player2_4,
          row.player2_5,
          row.player2_6,
          row.player2_7,
          row.player2_8,
          row.player2_9,
          row.player2_10,
          row.player2_11,
        ].join(',')}}` // Team2 players as an array
      ]);

      await client.query(query, values);
      console.log(`Inserted matches batch ${i / BATCH_SIZE + 1}`);
    }
  } catch (err) {
    console.error('Error inserting matches:', err.message);
  } finally {
    client.release();
  }
};

const readCSV = () => {
  const rows = [];
  fs.createReadStream('../Data/matches_data.csv') // Path to your matches CSV file
    .pipe(csv())
    .on('data', (data) => rows.push(data))
    .on('end', () => {
      console.log('CSV file read successfully. Starting data insertion...');
      insertMatches(rows);
    });
};

readCSV();
