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

app.put('/', async (req, res) => {

  if(!req.cookies.OAuthToken) {
    res.status(401).send('No auth token was provided.');
    return;
  }

  let oauthInfo;
  try {
    oauthInfo = await googleOAuthClient.verifyIdToken({
      idToken: req.cookies.OAuthToken,
      audience: process.env.GOOGLE_OAUTH_CLIENT_ID
    });
  } catch(error) {
    console.log(error);
    res.status(401).send('An error occurred when trying to verify the auth token.');
    return;
  }

  if(!oauthInfo){
    console.log('Token verification result was null.');
    res.status(401).send('Token could not be verified.');
    return;
  }

  const oauthInfoPayload = oauthInfo.getPayload()

  if(!oauthInfoPayload || !oauthInfoPayload.sub) {
    console.log('Token verification payload or token ID was null.');
    res.status(401).send('Token could not be verified.');
    return;
  }

  // save the team

  res.sendStatus(200);
});

app.set('port', process.env.PORT || 8890);

app.listen(app.get('port'), () => { console.log('Application started.'); });

module.exports = app;