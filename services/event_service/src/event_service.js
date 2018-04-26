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

app.get('/team/:teamkey?', async (req, res) => {
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
    queryRes = await pgPool.query('SELECT key, teamkey, name, fullDay, startTime, endTime FROM get_eventlist($1, $2)',
      [userId, req.params.teamkey]);
  } catch(error) {
    console.log(error);
    res.status(500).send('An error occurred when trying to lookup the event list.');
    return;
  }

  if(!queryRes || !queryRes.rows) {
    console.log('The lookup event list query returned null.');
    res.status(500).send('An error occurred when trying to lookup the event list.');
    return;
  }

  res.status(200).send({
    eventlist: queryRes.rows
  });
});

app.set('port', process.env.PORT || 8888);

app.listen(app.get('port'), () => { console.log('Application started.'); });

module.exports = app;