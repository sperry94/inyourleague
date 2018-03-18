from flask import Flask, render_template, request, redirect, session
import requests

event_service_endpoint = 'http://localhost:8888/';

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', submission=session.get('count', ''));

@app.route('/form_post', methods=['POST'])
def form_submission():
    submitted_input = request.form['text']
    res = requests.post(event_service_endpoint, data={'text':submitted_input});
    session['count'] = res.json()['count']
    return redirect('/');

app.secret_key = 'THIS_WILL_BE_SUPER_SECRET_LATER'
