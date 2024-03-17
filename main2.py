
import os
import requests
import re

from pathlib import Path

from flask import Flask, redirect, url_for, render_template, request, session

from flask_session import Session               ## pip install Flask-Session
import google.oauth2.credentials                ## Used by Google OAuth
import google_auth_oauthlib.flow                ## Used by Google OAuth
from googleapiclient.discovery import build     ## Used by Google OAuth
from google.auth.transport.requests import AuthorizedSession

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

CLIENT_SECRETS_FILE = 'client_secrets.json'

PICS_DOWNLOAD_FOLDER='DownloadedPics'

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'esdirolftjg rdsklthjrm,gme jkm2mw,3 werkj hswedf kdsjkh'
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, "sessions")
app.config['SESSION_FILE_THRESHOLD'] = 1000
Session(app)

@app.route("/")
def main():
    return redirect("home")

@app.route("/home")
def home():
    if "credentials-dict" not in session:    ## If not logged in
        return redirect("authorize")    ## Start the login process
    elif "user" in session:             ## If we are logged in
                                        ## Return a customised index page
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

def format_media_items(media_items):
    return media_items

def list_pics(credentials, from_year, from_month, to_year, to_month):
    if to_year < from_year:
        return "ERROR From Year must be lower or equal than To Year"
    
    authed_session = AuthorizedSession(credentials)
    nextPageToken = None
    idx = 0
    media_items = []
    while True:
        idx += 1

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
                                "year": from_year,
                                "month": from_month,
                                "day": 1,
                            },
                            "endDate": {
                                "year": to_year,
                                "month": to_month,
                                "day": 1,
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

def download_image(item, download_folder):
    width=item['mediaMetadata']['width']
    height=item['mediaMetadata']['height']
    base_url = item['baseUrl']
    file_name = item['filename']

    image_url=base_url + "=w" + width + "-h" + height + "-d" #-d download description

    local_filename = os.path.join(download_folder, file_name)
    img_data = requests.get(image_url).content
    with open(local_filename, 'wb') as f:
        f.write(img_data)
        f.close()

def download_video(item, download_folder):
    width=item['mediaMetadata']['width']
    height=item['mediaMetadata']['height']
    base_url = item['baseUrl']
    file_name = item['filename']
    
    video_url=base_url + '=dv' #-d download description

    local_filename = os.path.join(download_folder, file_name)

    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
            f.close()

def download_pics(credentials, from_year, from_month, to_year, to_month):    
    media_items = list_pics(credentials, from_year, from_month, to_year, to_month)    

    Path(PICS_DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    image_regex = r'image\/[\w\d]*'
    video_regex = r'video\/[\w\d]*'

    for item in media_items:
        mime_type = item['mimeType']
        if re.match(image_regex, mime_type):
            download_image(item, PICS_DOWNLOAD_FOLDER)
        elif re.match(video_regex, mime_type):
            download_video(item, PICS_DOWNLOAD_FOLDER)
        else:
            print("error mimetype " + mime_type + " not recognized")

    return media_items


@app.route("/list-pics", methods=['GET', 'POST'])
def list_pics_route():
    if "credentials" not in session:    ## If not logged in
        return redirect("authorize")    ## Start the login process
    else:
        form=request.form
        credentials=session['credentials']
        if request.method == 'POST':
            print(form)
            from_year=form['from_year']
            from_month=form['from_month']
            to_year=form['to_year']
            to_month=form['to_month']
            if request.form['submit_button'] == "List":
                return list_pics(credentials, from_year, from_month, to_year, to_month)
            elif request.form['submit_button'] == "Download":
                return download_pics(credentials, from_year, from_month, to_year, to_month)            
        
    
def main():   
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True) 

if __name__ == "__main__":
    main()