const express = require('express')
const bodyParser = require('body-parser')
const app = express()

app.use(bodyParser.json());

var count = 0;

app.post('/', (req, res) => {
  count += 1;
  res.send({count: count});
})

app.listen(8888, () => { console.log('Application started.'); })