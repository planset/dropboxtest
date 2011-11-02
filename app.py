# -*- coding: utf-8 -*-
from flask import Flask, request, session, redirect, url_for, \
                  render_template

import dropbox 
import oauth.oauth as oauth
from functools import wraps
from werkzeug import secure_filename

app = Flask(__name__)
app.secret_key='SECRET_KEY'

APP_KEY = 'YOUR_APP_KEY'
APP_SECRET = 'YOUR_APP_SECRET'
ACCESS_TYPE = 'app_folder'

sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@app.route('/')
def index():
    return render_template('index.html')
        
@app.route('/list')
def list():
    request_token = session.get('request_token')
    request_token_secret = session.get('request_token_secret')
    access_token = session.get('access_token')
    access_token_secret = session.get('access_token_secret')

    if request_token is None or request_token_secret is None:
        return redirect_authorize_url(url_for('list'))

    elif access_token is None or access_token_secret is None:
        authorized_token = get_access_token(request_token, request_token_secret)
        if authorized_token is None:
            return redirect_authorize_url(url_for('list'))
            
    else:
        authorized_token = oauth.OAuthToken(access_token, access_token_secret)
        sess.set_token(authorized_token.key, authorized_token.secret)

    client = dropbox.client.DropboxClient(sess)
    folder_metadata = client.metadata('/')

    return render_template('list.html', items = folder_metadata['contents'])

def get_access_token(request_token, request_token_secret):
    access_token = None
    
    if access_token is None:
        request_token = oauth.OAuthToken(request_token, request_token_secret)
        try:
            access_token = sess.obtain_access_token(request_token)
            session['access_token'] = access_token.key
            session['access_token_secret'] = access_token.secret
        except dropbox.rest.ErrorResponse, r:
            print r
            
    return access_token
    
def redirect_authorize_url(url):
    request_token = sess.obtain_request_token()
    session['request_token'] = request_token.key
    session['request_token_secret'] = request_token.secret

    callback_url = request.url_root + url
    url = sess.build_authorize_url(request_token, oauth_callback=callback_url)
    return redirect(url)

def requires_oauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_token = session.get('request_token')
        request_token_secret = session.get('request_token_secret')
        access_token = session.get('access_token')
        access_token_secret = session.get('access_token_secret')

        if request_token is None or request_token_secret is None:
            return redirect_authorize_url(request.path)

        elif access_token is None or access_token_secret is None:
            authorized_token = get_access_token(request_token, request_token_secret)
            if authorized_token is None:
                return redirect_authorize_url(request.path)

        else:
            authorized_token = oauth.OAuthToken(access_token, access_token_secret)
            sess.set_token(authorized_token.key, authorized_token.secret)

        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload', methods=['GET', 'POST'])
@requires_oauth
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
        
    else:
        sess.set_token(session.get('access_token'), 
                       session.get('access_token_secret'))

        client = dropbox.client.DropboxClient(sess)
                
        uploadfile = request.files['file']
        filename = secure_filename(uploadfile.filename)
        response = client.put_file('/' + filename, uploadfile.stream.getvalue())
        return redirect(url_for('list'))

@app.route('/clear')
def clear():
    del session['request_token']
    del session['request_token_secret']
    del session['access_token']
    del session['access_token_secret']
    return 'clear ok'

if __name__ == '__main__':
    app.run(debug=True)

