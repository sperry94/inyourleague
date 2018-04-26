from flask import Flask, abort, render_template, request, redirect, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from os import environ
from requests import get, post, put
from werkzeug.contrib.fixers import ProxyFix

account_service_endpoint = environ['IYL_ACCOUNT_SVC_ENDPOINT'].rstrip('/')
event_service_endpoint = environ['IYL_EVENT_SVC_ENDPOINT'].rstrip('/')
team_service_endpoint = environ['IYL_TEAM_SVC_ENDPOINT'].rstrip('/')

app = Flask(__name__)
app.secret_key = environ['FLASK_SECRET_KEY']
app.wsgi_app = ProxyFix(app.wsgi_app)
app.register_blueprint(make_google_blueprint(
    client_id=environ['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=environ['GOOGLE_OAUTH_CLIENT_SECRET'],
    redirect_to='home',
    scope=['profile']
), url_prefix='/login')


@app.before_request
def before_request():
    if request.endpoint == 'index' \
    or request.endpoint == 'google.login' \
    or request.endpoint == 'google.authorized' \
    or request.endpoint == 'logout' \
    or request.endpoint == 'static':
        return

    if not google.authorized:
        if request.method == 'GET':
            return redirect(url_for('google.login'))
        else:
            abort(401)

    try:
        resp = google.get('/oauth2/v2/userinfo')
    except Exception as error:
        print(error)
        session.clear()
        if request.method == 'GET':
            return redirect(url_for('google.login'))
        else:
            abort(401)

    if not resp.ok:
        session.clear()
        if request.method == 'GET':
            return redirect(url_for('google.login'))
        else:
            abort(401)

    # add CSRF stuff here

    if request.endpoint == 'account_view' \
    or request.endpoint == 'account_save':
        return

    try:
        oauthToken = session.get('google_oauth_token',{}).get('id_token','')
        account_exists_res = get(account_service_endpoint + '/exists', \
            cookies={'OAuthToken': oauthToken})
    except Exception as error:
        print(error)
        session.clear()
        abort(500)

    if not account_exists_res.ok:
        if request.method == 'GET':
            return redirect(url_for('account_view'))
        else:
            abort(401)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/home', methods=['GET'])
def home():
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    account_res = get(account_service_endpoint, \
        cookies={'OAuthToken': oauthToken})

    if not account_res.ok:
        print('The account lookup was unsuccessful.')
        abort(500)

    account_json = account_res.json()

    if account_json is None or 'accounttype' not in account_json:
        print('The account lookup result did not contain an account type.')
        abort(500)

    if account_json['accounttype'] == 0:
        return render_template('coach_home.html')
    elif account_json['accounttype'] == 1:
        return render_template('parent_home.html')
    else:
        print('The account type was not supported.')
        abort(500)


@app.route('/account', methods=['GET'])
def account_view():
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    account_res = get(account_service_endpoint, \
        cookies={'OAuthToken': oauthToken})

    if not account_res.ok:
        print('The account lookup was unsuccessful.')
        abort(500)

    account_json = account_res.json()

    if account_json is None:
        print('The account lookup result did not contain an account type.')
        abort(500)

    return render_template('account.html', \
        accounttype=account_json.get('accounttype', ''))


@app.route('/account', methods=['POST'])
def account_save():
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')
    accountType = request.form.get('AccountType', None)

    if not accountType:
        print('No account type was provided.')
        abort(500)

    try:
        accountType = int(accountType)
    except Exception as error:
        print(error)
        abort(500)

    save_res = put(account_service_endpoint, \
        cookies={'OAuthToken': oauthToken}, json={'AccountType': accountType})

    if not save_res.ok:
        print('The account save was unsuccessful.')
        abort(500)

    return redirect(url_for('home'))


@app.route('/team', methods=['POST'])
@app.route('/team/<uuid:teamkey>', methods=['POST'])
def team_view(teamkey=None):
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    team_name = request.form.get('name', None)

    res = put(team_service_endpoint, \
        cookies={'OAuthToken': oauthToken}, \
        json={'Key': teamkey, 'Name': team_name})

    if not res.ok:
        print('The team save was unsuccessful.')
        abort(500)

    return redirect(url_for('home'))


@app.route('/team', methods=['POST'])
@app.route('/team/<uuid:teamkey>', methods=['POST'])
def save_team(teamkey=None):
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    team_name = request.form.get('name', None)

    res = put(team_service_endpoint, \
        cookies={'OAuthToken': oauthToken}, \
        json={'Key': teamkey, 'Name': team_name})

    if not res.ok:
        print('The team save was unsuccessful.')
        abort(500)

    return redirect(url_for('home'))
