from flask import Flask, render_template, request, redirect, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from os import environ
from requests import post
from werkzeug.contrib.fixers import ProxyFix

event_service_endpoint = environ['IYL_EVENT_SVC_ENDPOINT']

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.register_blueprint(make_google_blueprint(
    client_id=environ['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=environ['GOOGLE_OAUTH_CLIENT_SECRET'],
    scope=['profile']
), url_prefix='/login')

@app.route('/', methods=['GET'])
def index():
    if not google.authorized:
        return redirect(url_for('google.login'))
    return render_template('index.html', submission=session.get('count', ''))

@app.route('/form_post', methods=['POST'])
def form_submission():
    submitted_input = request.form['text']
    res = post(event_service_endpoint, data={'text':submitted_input})
    session['count'] = res.json()['count']
    return redirect('/')

app.secret_key = 'THIS_WILL_BE_SUPER_SECRET_LATER'