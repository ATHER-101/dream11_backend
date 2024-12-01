const fs = require('fs');
const csv = require('csv-parser');
const pool = require('./db');

const BATCH_SIZE = 100; // Number of rows to insert per batch

const insertPlayerNames = async (rows) => {
  const client = await pool.connect();
  try {
    for (let i = 0; i < rows.length; i += BATCH_SIZE) {
      const batch = rows.slice(i, i + BATCH_SIZE);

      const query = `
        INSERT INTO player_names (player_id, name)
        VALUES ${batch
          .map((_, idx) => `($${idx * 2 + 1}, $${idx * 2 + 2})`)
          .join(',')}
        ON CONFLICT DO NOTHING;
      `;

      // Flatten batch data into a single array for parameterized query
      const values = batch.flatMap((row) => [row.player_id, row.name]);

      await client.query(query, values);
      console.log(`Inserted names batch ${i / BATCH_SIZE + 1}`);
    }
  } catch (err) {
    console.error('Error inserting names:', err.message);
  } finally {
    client.release();
  }
};

const readCSV = () => {
  const rows = [];
  fs.createReadStream('../Data/Datasets/names.csv')
    .pipe(csv())
    .on('data', (data) => rows.push(data))
    .on('end', () => {
      console.log('CSV file read successfully. Starting data insertion...');
      insertPlayerNames(rows);
    });
};

readCSV();
