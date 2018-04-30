from flask import Flask, abort, jsonify, render_template, request, redirect, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from os import environ
from requests import get, post, put
from secrets import token_hex
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


# code from http://flask.pocoo.org/snippets/3/
def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = token_hex(32)
    return session['csrf_token']

# code from http://flask.pocoo.org/snippets/3/
app.jinja_env.globals['csrf_token'] = csrf_token


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

    # based on code from http://flask.pocoo.org/snippets/3/
    if request.method == 'POST' or request.method == 'PUT':
        csrf_tok_form = request.form.get('csrf_token', None)
        csrf_tok_session = session.pop('csrf_token', None)

        if csrf_tok_form is None or csrf_tok_session is None \
        or csrf_tok_form != csrf_tok_session:
            abort(400)

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
        res = get(team_service_endpoint + '/list', \
            cookies={'OAuthToken': oauthToken})

        teams = {}

        if res.ok:
            res_json = res.json()

            if res_json:
                teams = res_json

        return render_template('coach_home.html', \
            teams=res_json.get('teamlist', []))

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


@app.route('/team', methods=['GET'])
@app.route('/team/<uuid:teamkey>', methods=['GET'])
def team_view(teamkey=None):
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    team_name = ''
    if teamkey is not None:
        res = get(team_service_endpoint + '/' + str(teamkey), \
            cookies={'OAuthToken': oauthToken})

        if not res.ok:
            print('The team lookup was unsuccessful.')
            abort(500)

        team = res.json()

        if team is not None:
            team_name = team.get('name', '')

    return render_template('team.html', team_key=teamkey, team_name=team_name)


@app.route('/team', methods=['POST'])
@app.route('/team/<uuid:teamkey>', methods=['POST'])
def save_team(teamkey=None):
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    team_name = request.form.get('name', None)

    save_body = {'Name': team_name}

    if teamkey:
        save_body['Key'] = str(teamkey)

    res = put(team_service_endpoint, \
        cookies={'OAuthToken': oauthToken}, json=save_body)

    if not res.ok:
        print('The team save was unsuccessful.')
        abort(500)

    return redirect(url_for('home'))

@app.route('/events', methods=['GET'])
def events():
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    res = get(event_service_endpoint + '/team/', \
        cookies={'OAuthToken': oauthToken})

    if not res.ok:
        print('The events lookup was unsuccessful.')
        abort(500)

    res_json = res.json()

    if res_json is None:
        print('The events lookup response was empty.')
        abort(500)

    event_list = res_json.get('eventlist', [])

    mapped_event_list = []
    for event in event_list:
        print(event)
        mapped_event_list.append({
            'id': event.get('key', ''),
            'title': event.get('name', ''),
            'allDay': event.get('fullday', ''),
            'start': event.get('starttime', ''),
            'end': event.get('endtime', ''),
        });

    # NOTE LOOK INTO RETURNING LIST VULNERABILITY
    return jsonify(mapped_event_list);

@app.route('/event', methods=['POST'])
@app.route('/event/<uuid:event>', methods=['POST'])
def save_event(eventkey=None):
    oauthToken = session.get('google_oauth_token',{}).get('id_token','')

    event_team = request.form.get('team', None)
    event_name = request.form.get('name', None)
    event_fullday = request.form.get('fullDay', '').lower() == 'true'
    event_start = request.form.get('startTime', None)
    event_end = request.form.get('endTime', None)

    save_body = {
        'TeamKey': event_team,
        'Name': event_name,
        'FullDay': event_fullday,
        'StartTime': event_start,
        'EndTime': event_end
    }

    if eventkey:
        save_body['Key'] = str(eventkey)

    res = put(event_service_endpoint, \
        cookies={'OAuthToken': oauthToken}, json=save_body)

    if not res.ok:
        print('The event save was unsuccessful.')
        abort(500)

    return redirect(url_for('home'))
