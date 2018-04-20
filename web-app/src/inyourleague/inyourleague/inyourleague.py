from flask import Flask, abort, render_template, request, redirect, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from os import environ
from requests import get, post, put
from werkzeug.contrib.fixers import ProxyFix

account_service_endpoint = environ['IYL_ACCOUNT_SVC_ENDPOINT'].rstrip('/')
event_service_endpoint = environ['IYL_EVENT_SVC_ENDPOINT'].rstrip('/')

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
    print(session)
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
    return render_template('home.html', submission=session.get('count', ''))

@app.route('/account', methods=['GET'])
def account_view():
    return render_template('account.html')

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

@app.route('/form_post', methods=['POST'])
def form_submission():
    submitted_input = request.form['text']
    res = post(event_service_endpoint, data={'text':submitted_input})
    session['count'] = res.json()['count']
    return redirect(url_for('home'))
