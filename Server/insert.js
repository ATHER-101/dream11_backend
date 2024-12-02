const fs = require('fs');
const csv = require('csv-parser');
const pool = require('./db'); // Import the database connection pool

const BATCH_SIZE = 100; // Number of rows to insert per batch

const insertData = async (rows) => {
  const client = await pool.connect();
  try {
    for (let i = 0; i < rows.length; i += BATCH_SIZE) {
      const batch = rows.slice(i, i + BATCH_SIZE);

      const query = `
        INSERT INTO players (player_id, name, role, batting_style, bowling_style, image)
        VALUES ${batch
          .map((_, idx) =>
            `($${idx * 6 + 1}, $${idx * 6 + 2}, $${idx * 6 + 3}, $${idx * 6 + 4}, $${idx * 6 + 5}, $${idx * 6 + 6})`
          )
          .join(',')}
        ON CONFLICT (player_id) DO NOTHING;
      `;

      // Flatten batch data into a single array for parameterized query
      const values = batch.flatMap((row) => [
        row.player_id,
        row.names,
        row.role || null,
        row.batting_style || null,
        row.bowling_style || null,
        row.image || null,
      ]);

      await client.query(query, values);
      console.log(`Inserted batch ${i / BATCH_SIZE + 1}`);
    }
  } catch (err) {
    console.error('Error inserting data:', err.message);
  } finally {
    client.release();
  }
};

const readCSV = () => {
  const rows = [];
  fs.createReadStream('../Data/players_data_new.csv') // Path to your CSV file
    .pipe(csv())
    .on('data', (data) => rows.push(data))
    .on('end', () => {
      console.log('CSV file read successfully. Starting data insertion...');
      insertData(rows);
    });
};

readCSV();
