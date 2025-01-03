const fs = require('fs');
const csv = require('csv-parser');
const pool = require('../db'); // Ensure your `db` file is correctly configured for your database connection

const BATCH_SIZE = 100; // Number of rows to insert per batch

// Function to insert data into the "names" table
const insertNames = async (rows) => {
  const client = await pool.connect();
  try {
    for (let i = 0; i < rows.length; i += BATCH_SIZE) {
      const batch = rows.slice(i, i + BATCH_SIZE);

      // Build the parameterized query
      const query = `
        INSERT INTO names (player_id, name)
        VALUES ${batch
          .map((_, idx) => `($${idx * 2 + 1}, $${idx * 2 + 2})`)
          .join(', ')}
        ON CONFLICT DO NOTHING;
      `;

      // Flatten the batch data for parameterized query
      const values = batch.flatMap((row) => [row.player_id, row.name]);

      // Execute the query
      await client.query(query, values);
      console.log(`Inserted batch ${i / BATCH_SIZE + 1}`);
    }
  } catch (err) {
    console.error('Error inserting data:', err.message);
  } finally {
    client.release();
  }
};

// Function to read the CSV and process the data
const readCSV = () => {
  const rows = [];
  fs.createReadStream('./names.csv') // Path to your CSV file
    .pipe(csv()) // Parse the CSV file
    .on('data', (data) => rows.push(data)) // Collect each row
    .on('end', () => {
      console.log('CSV file read successfully. Starting data insertion...');
      insertNames(rows); // Insert the collected rows into the database
    });
};

// Call the function to start reading and inserting
readCSV();
