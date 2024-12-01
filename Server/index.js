const express = require('express');
require('dotenv').config();
const cors = require('cors');
const port = process.env.PORT || 4000;

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send("Hello Dream11!")
})

const match = require("./api/match")
const explain = require("./api/explain")

app.use(match);
app.use(explain);

app.listen(port, () => {
  console.log(`Listening on http://localhost:${port}`)
})