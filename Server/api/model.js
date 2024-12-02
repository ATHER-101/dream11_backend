const express = require('express');
const { exec } = require('child_process');
const fs = require('fs'); // For file operations
const router = express.Router();

// Middleware to parse JSON body
router.use(express.json());

router.post('/model', (req, res) => {
  const { rows } = req.body; // Expecting rows in the request body
  
  if (!rows || !Array.isArray(rows) || rows.length === 0) {
    return res.status(400).send({ error: 'Invalid data format. "rows" must be a non-empty array.' });
  }

  // Path to the CSV file
  const csvFilePath = 'api/test.csv';

  // Generate the CSV content
  const csvHeader = 'Player Name,Squad,Match Date,Format\n';
  const csvContent = rows
    .map(row => `${row["Player Name"]},${row.Squad},${row["Match Date"]},${row.Format}`)
    .join('\n');

  // Write the CSV file
  fs.writeFile(csvFilePath, csvHeader + csvContent, (err) => {
    if (err) {
      console.error('Error writing CSV file:', err);
      return res.status(500).send({ error: 'Failed to create CSV file', details: err.message });
    }

    console.log('CSV file created successfully.');

    // Path to the Python script
    const pythonScript = 'python api/predict.py';

    // Execute the Python script
    exec(pythonScript, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing script: ${stderr}`);
        return res.status(500).send({ error: 'Script execution failed', details: stderr });
      }

      try {
        // Parse the JSON output from the Python script
        const output = JSON.parse(stdout);
        res.send({ success: true, output });
      } catch (parseError) {
        console.error('Error parsing script output:', parseError);
        res.status(500).send({ error: 'Failed to parse script output', details: parseError.message });
      }
    });
  });
});

module.exports = router;
