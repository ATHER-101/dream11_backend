const fs = require('fs');
const path = require('path');

const logFilePath = path.join(__dirname, 'processedFiles.json');

// Read the log file
function readLog() {
  if (!fs.existsSync(logFilePath)) {
    fs.writeFileSync(logFilePath, JSON.stringify([])); // Create the file if it doesn't exist
  }
  const data = fs.readFileSync(logFilePath, 'utf8');
  return JSON.parse(data);
}

// Add a file to the log
function addToLog(filename) {
  const log = readLog();
  if (!log.includes(filename)) {
    log.push(filename);
    fs.writeFileSync(logFilePath, JSON.stringify(log, null, 2)); // Pretty-print JSON
  }
}

// Check if a file is already in the log
function isFileProcessed(filename) {
  const log = readLog();
  return log.includes(filename);
}

function removeFromLog(filename) {
  const log = readLog();
  const updatedLog = log.filter((loggedFile) => loggedFile !== filename);

  fs.writeFileSync(logFilePath, JSON.stringify(updatedLog, null, 2));
  console.log(`Removed ${filename} from processed files log.`);
}


module.exports = { readLog, addToLog, isFileProcessed, removeFromLog };
