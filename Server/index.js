const express = require('express');
require('dotenv').config();

// Access environment variables using process.env
const port = process.env.PORT || 3000;

const app = express();
app.use(express.json());

app.get('/',(req,res)=>{
    res.send("Hello Dream11!")
})

app.listen(port,()=>{
    console.log(`Listening on http://localhost:${port}`)
})