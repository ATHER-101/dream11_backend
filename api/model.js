const express = require('express');
const { exec } = require('child_process');
const pool = require('../db');
const fs = require('fs'); // For file operations
const csvParser = require('csv-parser');
const { parse } = require('json2csv');
const router = express.Router();

// Middleware to parse JSON body
router.use(express.json());

router.post('/model', (req, res) => {
  const { rows } = req.body; // Expecting rows in the request body

  if (!rows || !Array.isArray(rows) || rows.length === 0) {
    return res.status(400).send({ error: 'Invalid data format. "rows" must be a non-empty array.' });
  }

  // Path to the Python script
  const pythonScript = `python ../../model/pred_product_ui.py ${rows[0].Format} ${rows.map(row => row.id).join(" ")}`;

  console.log(pythonScript)

  // Execute the Python script
  exec(pythonScript, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${stderr}`);
      return res.status(500).send({ error: 'Script execution failed', details: stderr });
    }

    try {
      // Parse the JSON output from the Python script
      console.log(stdout)
      const output = JSON.parse(stdout);

      console.log(output)

      res.send({ success: true, output: output });
    } catch (parseError) {
      console.error('Error parsing script output:', parseError);
      res.status(500).send({ error: 'Failed to parse script output', details: parseError.message });
    }
  });
});

// Endpoint: POST /train
router.post('/train', async (req, res) => {
  const { train_start_date, train_end_date, test_start_date, test_end_date } = req.body;

  const pythonScript = `python ../../model/train_model_ui.py ${train_start_date} ${train_end_date} ${test_start_date} ${test_end_date}`;
  const csvFilePath = `../../data/processed/test_results_${test_end_date}.csv`;

  exec(pythonScript, async (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${stderr}`);
      return res.status(500).send({ error: 'Script execution failed', details: stderr });
    }

    if (!fs.existsSync(csvFilePath)) {
      return res.status(500).send({ error: 'CSV file not generated' });
    }

    res.download(csvFilePath);
  });
});

module.exports = router;
