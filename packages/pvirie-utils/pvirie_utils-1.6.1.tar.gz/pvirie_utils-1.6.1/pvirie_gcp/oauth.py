import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests
from datetime import datetime, timedelta


class OAuth2_Service:

    def __init__(self, scopes, redirect_url):
        scopes = set(scopes)
        scopes.add('openid')
        scopes.add('https://www.googleapis.com/auth/userinfo.email')
        self.scopes = list(scopes)

        self.redirect_url = redirect_url


    def get_login_url(self):

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            os.getenv("GCP_SECRET_FILE"), 
            scopes=self.scopes,
        )

        flow.redirect_uri = self.redirect_url

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Recommended, enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Optional, if your application knows which user is trying to authenticate, it can use this
            # parameter to provide a hint to the Google Authentication Server.
            login_hint='hint@example.com',
            # Optional, set prompt to 'consent' will prompt the user for consent
            prompt='consent')
        
        return authorization_url, state


    def get_email(self, credentials):
        request = Request()
        id_info = id_token.verify_oauth2_token(credentials.id_token, request, credentials.client_id)
        return id_info['email']
        

    def exchange_credentials(self, code, state):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            os.getenv("GCP_SECRET_FILE"),
            scopes=self.scopes,
            state=state)
        flow.redirect_uri = self.redirect_url
        flow.fetch_token(code=code)
        credentials = flow.credentials
        return credentials
    

    def serialize_credentials(self, credentials):
        return {
            "token": credentials.token,
            "id_token": credentials.id_token,
            "expires_in": credentials.expiry.isoformat(),
            "refresh_token": credentials.refresh_token,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "token_uri": credentials.token_uri,
            "scopes": credentials.scopes
        }


    def deserialize_credentials(self, json_data):
        expiry = None
        if json_data['expires_in']:
            expiry = datetime.fromisoformat(json_data['expires_in'])
        return google.oauth2.credentials.Credentials(
            token=json_data['token'],
            id_token=json_data['id_token'] if 'id_token' in json_data else None,
            expiry=expiry,
            refresh_token=json_data['refresh_token'] if 'refresh_token' in json_data else None,
            client_id=json_data['client_id'] if 'client_id' in json_data else None,
            client_secret=json_data['client_secret'] if 'client_secret' in json_data else None,
            token_uri=json_data['token_uri'] if 'token_uri' in json_data else None,
            scopes=json_data['scopes'] if 'scopes' in json_data else None
        )
    

    def refresh_credentials(self, credentials):
        r = requests.post('https://oauth2.googleapis.com/token',
                        data={
                            'client_id': credentials.client_id,
                            'client_secret': credentials.client_secret,
                            'refresh_token': credentials.refresh_token,
                            'grant_type': 'refresh_token'
                        })
        if r.status_code != 200:
            return None
        response_json = r.json()
        expire_stamp = datetime.now() + timedelta(seconds=response_json['expires_in'])
        return self.deserialize_credentials({
            "token": response_json['access_token'],
            "id_token": response_json['id_token'],
            "expires_in": expire_stamp.isoformat(),
            "refresh_token": credentials.refresh_token,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "token_uri": credentials.token_uri,
            "scopes": response_json['scope'].split(' ')
        })
        
    
    def revoke_credentials(self, credentials):
        r = requests.post('https://oauth2.googleapis.com/revoke',
                        params={'token': credentials.token},
                        headers={'content-type': 'application/x-www-form-urlencoded'})
        if r.status_code != 200:
            return False
        return True