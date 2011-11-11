# -*- coding: utf-8 -*-
from flask import Flask, request, session, redirect, url_for, g, \
                  render_template, Response

from functools import wraps
from werkzeug import secure_filename
import dropbox 
import oauth.oauth as oauth
import simplejson as json

env_file_path = '/home/dotcloud/environment.json'
if not os.path.exists(env_file_path):
    env_file_path = '/tmp/environment.json'

with open(env_file_path) as f:
    env = json.load(f)

app = Flask(__name__)
app.secret_key=env['SECRET_KEY']

APP_KEY = env['APP_KEY']
APP_SECRET = env['APP_SECRET']
ACCESS_TYPE = 'app_folder'


def requires_oauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_token = session.get('request_token')
        request_token_secret = session.get('request_token_secret')
        access_token = session.get('access_token')
        access_token_secret = session.get('access_token_secret')

        if request_token is None or request_token_secret is None:
            return redirect_authorize_url(g.sess, request.path)

        elif access_token is None or access_token_secret is None:
            authorized_token = get_access_token(g.sess, request_token, request_token_secret)
            if authorized_token is None:
                return redirect_authorize_url(g.sess, request.path)

        else:
            authorized_token = oauth.OAuthToken(access_token, access_token_secret)
            g.sess.set_token(access_token, access_token_secret)

        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    g.sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/list')
@requires_oauth
def list():
    client = dropbox.client.DropboxClient(g.sess)
    folder_metadata = client.metadata('/')
    return render_template('list.html', items = folder_metadata['contents'])

@app.route('/upload', methods=['GET', 'POST'])
@requires_oauth
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        client = dropbox.client.DropboxClient(g.sess)
        uploadfile = request.files['file']
        filename = secure_filename(uploadfile.filename)
        response = client.put_file('/' + filename, uploadfile.stream.getvalue())
        return redirect(url_for('list'))
        
@app.route('/thumbnail/<path:path>/')
@requires_oauth
def thumbnail(path):
    client = dropbox.client.DropboxClient(g.sess)
    res = client.thumbnail(path)
    return Response(response=res.read(), content_type=res.msg.type)
    
@app.route('/clear')
def clear():
    del session['request_token']
    del session['request_token_secret']
    del session['access_token']
    del session['access_token_secret']
    return 'clear ok'

def get_access_token(sess, request_token, request_token_secret):
    request_token = oauth.OAuthToken(request_token, request_token_secret)
    try:
        access_token = sess.obtain_access_token(request_token)
        session['access_token'] = access_token.key
        session['access_token_secret'] = access_token.secret
    except dropbox.rest.ErrorResponse, r:
        print r

    return access_token

def redirect_authorize_url(sess, callback_url):
    request_token = sess.obtain_request_token()
    session['request_token'] = request_token.key
    session['request_token_secret'] = request_token.secret

    oauth_callback = request.url_root + callback_url[1:]
    authorize_url = sess.build_authorize_url(request_token, oauth_callback=oauth_callback)
    return redirect(authorize_url)



if __name__ == '__main__':
    app.run(debug=True)

