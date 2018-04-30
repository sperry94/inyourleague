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

pgPool.connect();

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

app.get('/exists', async (req, res) => {

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
    queryRes = await pgPool.query('SELECT account_exists($1) as exists',
      [userId]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to check if the account exists.');
    return;
  }

  if(!queryRes || !queryRes.rows || !queryRes.rows[0]) {
    console.log('The account existence check returned invalid data.');
    res.status(500).send('An error occurred when trying to check if the account exists.');
    return;
  }

  if(!queryRes.rows[0].exists) {
    console.log('account',userId, 'does not exist')
    res.status(404).send('The account does not exist.');
    return;
  }

  res.sendStatus(200);
});

app.get('/', async (req, res) => {

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
    queryRes = await pgPool.query('SELECT oauthid, accounttype, firstname, lastname, sharecode FROM get_account($1) as (oauthid TEXT, accounttype INT, firstname TEXT, lastname TEXT, sharecode UUID)',
      [userId]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to lookup the account.');
    return;
  }

  if(!queryRes || !queryRes.rows || !queryRes.rows[0]) {
    console.log('The account lookup returned invalid data.');
    res.status(500).send('An error occurred when trying to lookup the account.');
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

  if(req.body.AccountType == null || !(typeof(req.body.AccountType) === "number")) {
    const msg = 'No account type was specified for the account to save.';
    console.log(msg);
    res.status(400).send(msg);
    return;
  }

  if(req.body.FirstName == null) {
    const msg = 'No first name was specified for the account to save.';
    console.log(msg);
    res.status(400).send(msg);
    return;
  }

  if(req.body.LastName == null) {
    const msg = 'No last name was specified for the account to save.';
    console.log(msg);
    res.status(400).send(msg);
    return;
  }

  let queryRes;
  try {
    queryRes = await pgPool.query('SELECT save_account($1, $2, $3, $4) as success',
      [userId, req.body.AccountType, req.body.FirstName, req.body.LastName]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to save the account.');
    return;
  }

  if(!queryRes || !queryRes.rows || !queryRes.rows[0]
    || !queryRes.rows[0].success) {
    console.log('The save account query returned false.');
    res.status(500).send('An error occurred when trying to save the account.');
    return;
  }

  res.sendStatus(200);
});

app.set('port', process.env.PORT || 8889);

app.listen(app.get('port'), () => { console.log('Application started.'); });

module.exports = app;