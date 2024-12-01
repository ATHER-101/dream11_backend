const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const router = express.Router();

router.get('/explain', async (req, res) => {
    const notebookPath = '../../Explanability/Explainability.ipynb';
    const outputNotebookPath = '../../Explanability/output_notebook.ipynb';
  
    // Run the Jupyter notebook using nbconvert
    const command = `jupyter nbconvert --to notebook --execute --output "${outputNotebookPath}" "${notebookPath}"`;
  
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing notebook: ${stderr}`);
        return res.status(500).send({ error: 'Notebook execution failed', details: stderr });
      }
  
      // Read the executed notebook file
      fs.readFile(outputNotebookPath, 'utf8', (err, data) => {
        if (err) {
          console.error('Error reading output notebook:', err);
          return res.status(500).send({ error: 'Failed to read output notebook' });
        }
  
        try {
          // Parse the executed notebook
          const notebook = JSON.parse(data);
          const lastCell = notebook.cells[notebook.cells.length - 1];
  
          // Ensure the last cell is a code cell and contains outputs
          if (lastCell.cell_type === 'code' && lastCell.outputs) {
            const output = lastCell.outputs.map(output => output.text || output.data['text/plain']).join('\n');
            res.send({ success: true, output });
          } else {
            res.send({ success: false, message: 'Last cell has no output or is not a code cell' });
          }
        } catch (parseError) {
          console.error('Error parsing notebook:', parseError);
          res.status(500).send({ error: 'Error parsing executed notebook' });
        }
      });
    });
  });
    

module.exports = router;
