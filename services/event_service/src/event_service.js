const express = require('express')
const bodyParser = require('body-parser')
const app = express()

app.set('port', process.env.PORT || 8888);

app.use(bodyParser.json());

var count = 0;

app.post('/', (req, res) => {
  count += 1;
  res.send({count: count});
})

app.listen(app.get('port'), () => { console.log('Application started.'); })