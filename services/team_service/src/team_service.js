const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const express = require('express');
const googleAuth = require('google-auth-library');
const pg = require('pg');

const googleOAuthClient = new googleAuth.OAuth2Client(process.env.GOOGLE_OAUTH_CLIENT_ID);

const app = express();
app.use(bodyParser.json());
app.use(cookieParser());

const pgPool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: true
});

const getGoogleIdFromToken = async (token) => {
  const oauthInfo = await googleOAuthClient.verifyIdToken({
    idToken: token,
    audience: process.env.GOOGLE_OAUTH_CLIENT_ID
  });

  if(!oauthInfo){
    console.log('Token verification result was null.');
    return;
  }

  const oauthInfoPayload = oauthInfo.getPayload()

  if(!oauthInfoPayload || !oauthInfoPayload.sub) {
    console.log('Token verification payload or token ID was null.');
    return;
  }

  return oauthInfoPayload.sub;
}

pgPool.connect();

app.get('/list', async (req, res) => {

  if(!req.cookies.OAuthToken) {
    res.status(401).send('No auth token was provided.');
    return;
  }

  let userId;
  try {
    userId = await getGoogleIdFromToken(req.cookies.OAuthToken);
  } catch(error) {
    console.log(error);
    res.status(401).send('An error occurred when trying to verify the auth token.');
    return;
  }

  if(!userId) {
    res.status(401).send('Token could not be verified.');
    return;
  }

  let queryRes;
  try {
    queryRes = await pgPool.query('SELECT key, name FROM get_teamlist($1)',
      [userId]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to lookup the team list.');
    return;
  }

  if(!queryRes || !queryRes.rows) {
    console.log('The lookup team list query returned null.');
    res.status(500).send('An error occurred when trying to lookup the team list.');
    return;
  }

  res.status(200).send({
    teamlist: queryRes.rows
  });
});

app.get('/:key', async (req, res) => {

  if(!req.cookies.OAuthToken) {
    res.status(401).send('No auth token was provided.');
    return;
  }

  let userId;
  try {
    userId = await getGoogleIdFromToken(req.cookies.OAuthToken);
  } catch(error) {
    console.log(error);
    res.status(401).send('An error occurred when trying to verify the auth token.');
    return;
  }

  if(!userId) {
    res.status(401).send('Token could not be verified.');
    return;
  }

  if(req.params.key == null || !(typeof(req.params.key) === "string")) {
    const msg = 'No key was specified for the team to lookup.';
    console.log(msg);
    res.status(400).send(msg);
    return;
  }

  let queryRes;
  try {
    queryRes = await pgPool.query('SELECT key, userid, name FROM get_team($1, $2) as (key UUID, userid TEXT, name TEXT)',
      [userId, req.params.key]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to lookup the team.');
    return;
  }

  if(!queryRes || !queryRes.rows || !queryRes.rows[0]) {
    console.log('The lookup team query returned null.');
    res.status(500).send('An error occurred when trying to lookup the team.');
    return;
  }

  res.status(200).send(queryRes.rows[0]);
});

app.put('/', async (req, res) => {

  if(!req.cookies.OAuthToken) {
    res.status(401).send('No auth token was provided.');
    return;
  }

  let userId;
  try {
    userId = await getGoogleIdFromToken(req.cookies.OAuthToken);
  } catch(error) {
    console.log(error);
    res.status(401).send('An error occurred when trying to verify the auth token.');
    return;
  }

  if(!userId) {
    res.status(401).send('Token could not be verified.');
    return;
  }

  if(req.body.Name == null || !(typeof(req.body.Name) === "string")) {
    const msg = 'No team name was specified for the team to save.';
    console.log(msg);
    res.status(400).send(msg);
    return;
  }

  let queryRes;
  try {
    queryRes = await pgPool.query('SELECT save_team($1, $2, $3) as teamkey',
      [req.body.Key, userId, req.body.Name]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to save the team.');
    return;
  }

  if(!queryRes || !queryRes.rows || !queryRes.rows[0]
    || !queryRes.rows[0].teamkey) {
    console.log('The save team query returned null.');
    res.status(500).send('An error occurred when trying to save the team.');
    return;
  }

  res.status(200).send({
    key: queryRes.rows[0].teamkey
  });
});

app.set('port', process.env.PORT || 8890);

app.listen(app.get('port'), () => { console.log('Application started.'); });

module.exports = app;