from google.cloud import secretmanager
from google.api_core import exceptions as google_api_exceptions

from . import gcp

# Access Cloud Storage

def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    return client


class Secret_Manager:
    def __init__(self, project_id, credentials=None):
        self.session = get_session(credentials)
        self.project_id = project_id

    def create_secret(self, secret_name):
        parent = f"projects/{self.project_id}"
        secret = {"replication": {"automatic": {}}}
        try:
            response = self.session.create_secret(
                request={"parent": parent, "secret_id": secret_name, "secret": secret}
            )
            print(f"Created secret: {response.name}")
            return response
        except google_api_exceptions.AlreadyExists:
            print(f"Secret {secret_name} already exists.")

    def add_secret_version(self, secret_name, payload):
        parent = f"projects/{self.project_id}/secrets/{secret_name}"
        payload = {"data": payload.encode("UTF-8")}
        try:
            response = self.session.add_secret_version(
                request={"parent": parent, "payload": payload}
            )
            print(f"Added secret version: {response.name}")
            return response
        except google_api_exceptions.NotFound:
            print(f"Secret {secret_name} not found.")
        except google_api_exceptions.PermissionDenied:
            print(f"Permission denied to add secret version to {secret_name}.")
        except Exception as e:
            print(f"Error adding secret version: {e}")
        return None
    

    def get_secret(self, secret_name, version="latest"):
        """
        Get the secret value for a specific version.
        If version is "latest", it retrieves the latest version.
        """
        parent = f"projects/{self.project_id}/secrets/{secret_name}"
        if version == "latest":
            version = "latest"
        else:
            version = f"versions/{version}"

        try:
            response = self.session.access_secret_version(
                request={"name": f"{parent}/{version}"}
            )
            secret_value = response.payload.data.decode("UTF-8")
            print(f"Retrieved secret value: {secret_value}")
            return secret_value
        except google_api_exceptions.NotFound:
            print(f"Secret {secret_name} or version {version} not found.")
        except google_api_exceptions.PermissionDenied:
            print(f"Permission denied to access secret {secret_name}.")
        except Exception as e:
            print(f"Error retrieving secret: {e}")
        return None
    
    
    def delete_secret(self, secret_name):
        parent = f"projects/{self.project_id}/secrets/{secret_name}"
        try:
            self.session.delete_secret(request={"name": parent})
            print(f"Deleted secret: {secret_name}")
        except google_api_exceptions.NotFound:
            print(f"Secret {secret_name} not found.")
        except google_api_exceptions.PermissionDenied:
            print(f"Permission denied to delete secret {secret_name}.")
        except Exception as e:
            print(f"Error deleting secret: {e}")