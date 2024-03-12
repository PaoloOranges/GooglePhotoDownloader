
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow

from flask import Flask, redirect, url_for, render_template, request, session


from flask_session import Session               ## pip install Flask-Session
import google.oauth2.credentials                ## Used by Google OAuth
import google_auth_oauthlib.flow                ## Used by Google OAuth
from googleapiclient.discovery import build     ## Used by Google OAuth
from google.auth.transport.requests import AuthorizedSession

SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/photoslibrary.readonly',
        "openid"]

# SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
CLIENT_SECRETS_FILE = 'client_secrets.json'

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'esdirolftjg rdsklthjrm,gme jkm2mw,3 werkj hswedf kdsjkh'
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, "sessions")
app.config['SESSION_FILE_THRESHOLD'] = 1000
Session(app)

@app.route("/")
def main():
    return redirect("home")


def render_home():
    return render_template('home.html', name=session['user']['name'])

@app.route("/home", methods=['GET', 'POST'])
def home():
    if "credentials-dict" not in session:    ## If not logged in
        return redirect("authorize")    ## Start the login process
    elif "user" in session:             ## If we are logged in
                                        ## Return a customised index page
        form=request.form
        if request.method == 'POST':
            print(form)

        return render_template('home.html', name=session['user']['name'])
        

## Used by Google OAuth
def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'id_token': credentials.id_token}

## Used by Google OAuth
@app.route("/login")
def login():
    if "credentials-dict" not in session:
        return redirect("authorize")
    else:
        return redirect("home")

## Used by Google OAuth
@app.route("/authorize")
def authorize():
    # Intiiate login request
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)

## Used by Google OAuth
@app.route("/oauth2callback")
def oauth2callback():
    # Receive an authorisation code from google
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    # Use authorisation code to request credentials from Google
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials
    session['credentials-dict'] = credentials_to_dict(credentials)
    # Use the credentials to obtain user information and save it to the session
    oauth2_client = build('oauth2','v2',credentials=credentials)
    user_info= oauth2_client.userinfo().get().execute()
    session['user'] = user_info
    # Return to main page
    return redirect("home")

@app.route("/list-pics")
def list_pics_route():
    if "credentials" not in session:    ## If not logged in
        return redirect("authorize")    ## Start the login process
    else:
        return list_pics(session['credentials'])

def list_pics(credentials):
    authed_session = AuthorizedSession(credentials)
    nextPageToken = None
    idx = 0
    media_items = []
    while True:
        idx += 1
        print(idx)
        
        response = authed_session.post(
            'https://photoslibrary.googleapis.com/v1/mediaItems:search', 
            headers = { 'content-type': 'application/json' },
            json={ 
                "pageSize": 100,
                "pageToken": nextPageToken,
                "filters": {
                    "dateFilter": {
                        "ranges": [{ 
                            "startDate": {
                                "year": 2023,
                                "month": 1,
                                "day": 1,
                            },
                            "endDate": {
                                "year": 2023,
                                "month": 1,
                                "day": 26,
                            }
                        }]
                    }
                }
            })
        
        response_json = response.json()
        media_items += response_json["mediaItems"]
        
        if not "nextPageToken" in response_json:
            break
            
        nextPageToken = response_json["nextPageToken"]

    return media_items

def main():   
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True) 

if __name__ == "__main__":
    main()