const express = require('express');
const { exec } = require('child_process');
const router = express.Router();

router.get('/explain', (req, res) => {
  const pythonScript = 'python ../Explanability/explain.py';

  // Execute the Python script
  exec(pythonScript, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${stderr}`);
      return res.status(500).send({ error: 'Script execution failed', details: stderr });
    }

    // Send the script's output as the API response
    res.send({ success: true, output: stdout });
  });
});
    
module.exports = router;
