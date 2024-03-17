import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests

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

def main():
    # initialize photos api and create service
    google_photos_api = GooglePhotosApi()
    creds = google_photos_api.run_local_server()

if __name__ == "__main__":
    main()