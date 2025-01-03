const express = require('express');
require('dotenv').config();
const cors = require('cors');
const port = process.env.PORT || 4000;

const app = express();
app.use(cors());
app.use(express.json());

const chokidar = require('chokidar');
const path = require('path');
const fs = require('fs');
const { addToLog, isFileProcessed } = require('./logUtils');
const processCSV = require('./processCSV');

async function processUnprocessedFiles() {
  const files = fs.readdirSync(path.join(__dirname, '../../out_of_sample_data'));
  for (const file of files) {
    if (!isFileProcessed(file)) {
      const filePath = path.join(__dirname, '../../out_of_sample_data', file);
      try {
        console.log(`Processing unprocessed file: ${file}`);
        await processCSV(filePath);
        addToLog(file); // Log the file after processing
        console.log(`File processed and logged: ${file}`);
      } catch (err) {
        console.error(`Error processing file ${file}:`, err);
      }
    }
  }
}

processUnprocessedFiles();

const watcher = chokidar.watch(path.join(__dirname, "../../out_of_sample_data"), {
  persistent: true,
});

watcher.on('add', async (filePath) => {
  const fileName = path.basename(filePath);
  if (!isFileProcessed(fileName)) {
    try {
      console.log(`New file detected: ${fileName}`);
      await processCSV(filePath);
      addToLog(fileName); // Log the file after processing
      console.log(`File processed and logged: ${fileName}`);
    } catch (err) {
      console.error(`Error processing file ${fileName}:`, err);
    }
  }
});



app.get('/', (req, res) => {
  res.send("Hello Dream11!")
})

const match = require("./api/match")
const explain = require("./api/explain")
const model = require("./api/model")

app.use(match);
app.use(explain);
app.use(model);

app.listen(port, () => {
  console.log(`Listening on http://localhost:${port}`)
})