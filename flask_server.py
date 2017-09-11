"""Door opening server for HJG6"""
import os
import threading
import pickle
from flask import Flask, render_template, redirect, url_for, session, request
from flask_oauthlib.client import OAuth
import control_door
import oauth_id_and_secret

APP = Flask(__name__, static_url_path='/static')
APP.config['GOOGLE_ID'] = oauth_id_and_secret.G_ID
APP.config['GOOGLE_SECRET'] = oauth_id_and_secret.G_SCRT
APP.debug = False
APP.secret_key = 'development'
OAUTH = OAuth(APP)
GOOGLE_AUTH = OAUTH.remote_app(
    'google',
    consumer_key=APP.config.get('GOOGLE_ID'),
    consumer_secret=APP.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

AUTHORIZED_USERS = []


def flask_startup():
    """Starting up flask server"""
    global OAUTH
    OAUTH = OAuth(APP)

    if APP.debug is not True:
        import logging
        from logging.handlers import RotatingFileHandler
        os.remove('python.log')
        file_handler = RotatingFileHandler('python.log', maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        APP.logger.addHandler(file_handler)

@APP.route('/')
def index():
    """Check if user is in google session"""
    if 'google_token' in session:
        google_user = GOOGLE_AUTH.get('userinfo')
        if 'email' in google_user.data.keys():
            return render_template('template.html', email=google_user.data["email"])
    return redirect(url_for('login'))

@APP.route('/login')
def login():
    """Requests that the user logs into google account"""
    return GOOGLE_AUTH.authorize(callback=url_for('authorized', _external=True))

@APP.route('/logout')
def logout():
    """Logs the user out from google account"""
    session.pop('google_token', None)
    return redirect(url_for('index'))

@APP.route('/login/authorized')
def authorized():
    """Tests if the user is authorized"""
    resp = GOOGLE_AUTH.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    google_user = GOOGLE_AUTH.get('userinfo')

    if 'email' in google_user.data.keys():
        if user_index(google_user.data["email"]) > -1:
            return render_template('template.html', email=google_user.data["email"])
        return render_template('denied.html', email=google_user.data["email"])
    return redirect(url_for('login'))

@APP.route('/open-door/')
def door_open_clicked():
    """At button click, open the door"""
    google_user = GOOGLE_AUTH.get('userinfo')
    if 'email' in google_user.data.keys():
        person_index = user_index(google_user.data["email"])
        if person_index > -1:
            control_door.open_door()
            threading.Timer(3, control_door.close_door).start()
            os.system('espeak \"' + AUTHORIZED_USERS[person_index].get_nickname() + '\" 2>/dev/null')
            return redirect('/')
        return render_template('denied.html', email=google_user.data["email"])
    return redirect(url_for('login'))

@GOOGLE_AUTH.tokengetter
def get_google_oauth_token():
    """Returns the session's google token"""
    return session.get('google_token')

def load_pickle():
    """loading authorized users from pickled file"""
    global AUTHORIZED_USERS
    AUTHORIZED_USERS = pickle.load(open("pickled_users.pickle", "rb"))

def user_index(authenticated_mail):
    """Returns list index if authenticated mail has permission"""
    for i in range(0, len(AUTHORIZED_USERS)):
        if AUTHORIZED_USERS[i].get_email() == authenticated_mail:
            return i
    return -1

if __name__ == '__main__':
    control_door.close_door()
    os.system('amixer set PCM 95%')
    flask_startup()
    load_pickle()
    APP.run(host='0.0.0.0', port=80, threaded=True)
