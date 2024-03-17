import pickle
import os
import inquirer
import requests

from datetime import date, timedelta
from halo import Halo

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession

from googleapiclient.discovery import build
#from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


class GooglePhotosApi:
    def __init__(self,
                 api_name = 'photoslibrary',
                 client_secret_file= r'./client_secrets.json',
                 api_version = 'v1',
                 scopes = ['https://www.googleapis.com/auth/photoslibrary']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api

        Return:
            service:
        '''

        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./sessions/token_{self.api_name}_{self.api_version}.pickle'

        self.cred = None

    def run_local_server(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server(port=5000, bind_host="0.0.0.0" )

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)
        
        return self.cred

google_credentials=None

def authorize_google():
    # initialize photos api and create service
    global google_credentials
    google_photos_api = GooglePhotosApi()
    google_credentials = google_photos_api.run_local_server()    

def has_auth():
    return google_credentials != None

def init_google_auth():
    if not has_auth():
        authorize_google()

list_questions = [
    inquirer.Text(
            "From Year",
            message="Provide the starting YEAR to process"
            ),
    inquirer.List(
            "From Month",
            message="Provide the starting MONTH to process",
            choices=list(range(1,13))
            ),
    inquirer.Text(
            "To Year",
            message="Provide the ending YEAR to process",
            ),
    inquirer.List(
            "To Month",
            message="Provide the ending MONTH [NOT INCLUDED] to process",
            choices=list(range(1,13))
        ),
    ]

def download_media():
    print("Download")

def list_media():
    answers = inquirer.prompt(list_questions)
    from_year = answers.get("From Year")
    from_month = answers.get("From Month")
    to_year = answers.get("To Year")
    to_month = answers.get("To Month")

    from_date = date(int(from_year), int(from_month), 1)
    to_date = date(int(to_year), int(to_month), 1) - timedelta(days=1)

    print(str(from_date) + " " + str(to_date))

    if to_date < from_date:
        print("ERROR To Date shoult be later than from date")
        return
    
    if google_credentials == None:
        print("ERROR Google Credentials not set")
        return
    
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start()

    authed_session = AuthorizedSession(google_credentials)
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
    
    spinner.stop()
    for media_item in media_items:
        print(media_item['filename'])


LIST_MEDIA_ACTION = "List Media" 
DOWNLOAD_MEDIA_ACTION = "Download Media"
EXIT_ACTION = "Exit"

main_questions = [
        inquirer.List(
            "Action",
            message="Please select an action",
            choices=[LIST_MEDIA_ACTION, DOWNLOAD_MEDIA_ACTION, EXIT_ACTION],
        ),
        # inquirer.Text("user", message="Please enter your github username", validate=lambda _, x: x != "."),
        # inquirer.Password("password", message="Please enter your password"),
        # inquirer.Text("repo", message="Please enter the repo name", default="default"),
        # inquirer.Checkbox(
        #     "topics",
        #     message="Please define your type of project?",
        #     choices=["common", "backend", "frontend"],
        # ),
        # inquirer.Text(
        #     "organization",
        #     message=(
        #         "If this is a repo from a organization please enter the organization name,"
        #         " if not just leave this blank"
        #     ),
        # ),
        # inquirer.Confirm(
        #     "correct",
        #     message="This will delete all your current labels and create a new ones. Continue?",
        #     default=False,
        # ),
    ]

def main():
    init_google_auth()
    running = True
    while running:
        answers = inquirer.prompt(main_questions)
        action = answers.get("Action")

        if action == EXIT_ACTION:
            print("Exiting")
            running = False
        elif action==LIST_MEDIA_ACTION:
            list_media()
        elif action==DOWNLOAD_MEDIA_ACTION:
            download_media()

if __name__ == "__main__":
    main()