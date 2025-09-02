from . import gcp
from google.cloud import storage
from datetime import timedelta

# Access Cloud Storage

def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    storage_client = storage.Client(credentials=credentials)
    return storage_client


def process_blob(blob):
    # Check if the blob is a directory metadata file
    parts = blob.name.split('/')
    if len(parts) >= 1 and parts[-1].startswith('#directory#'):
        parts[-1] = parts[-1][11:] + ".dir"
    return '/'.join(parts)


class GCS:
    def __init__(self, bucket_name, credentials=None):
        self.session = get_session(credentials)
        self.bucket_name = bucket_name
        self.bucket = self.session.bucket(bucket_name)


    def enable_cors(self, allowed_origins, allowed_methods=["GET", "POST"], max_age_seconds=3600):
        try:
            # Define the CORS rules - this is a list of rule dictionaries
            cors_rules = [
                {
                    "origin": allowed_origins,
                    "method": allowed_methods,
                    "maxAgeSeconds": max_age_seconds
                }
                # You can add more rule dictionaries here for different origin/method combos if needed
            ]

            # Set the CORS configuration on the bucket object
            self.bucket.cors = cors_rules

            # Save the changes to the bucket's metadata
            # patch() is generally preferred as it only sends fields that changed.
            print(f"Setting CORS configuration for bucket gs://{self.bucket_name}...")
            self.bucket.patch()
            # Alternatively, use bucket.update() which sends all metadata fields

            print("Successfully updated CORS configuration.")
            print(f" Allowed Origins: {allowed_origins}")
            print(f" Allowed Methods: {allowed_methods}")
            print(f" Max Age (seconds): {max_age_seconds}")
            return True

        except Exception as e:
            print(f"An error occurred updating CORS configuration: {e}")
            # Common errors:
            # - Forbidden: Credentials lack storage.buckets.update permission.
            # - NotFound: Bucket doesn't exist.
            return False


    def upload_file(self, local_file_path, gcs_blob_name):
        """
        Upload a file to Google Cloud Storage.
        """
        blob = self.bucket.blob(gcs_blob_name)
        blob.upload_from_filename(local_file_path)
        print(f"Uploaded {local_file_path} to {gcs_blob_name} in bucket {self.bucket_name}")


    def upload_bytes(self, data: bytes, gcs_blob_name):
        """
        Upload bytes to Google Cloud Storage.
        """
        blob = self.bucket.blob(gcs_blob_name)
        blob.upload_from_string(data)
        print(f"Uploaded bytes to {gcs_blob_name} in bucket {self.bucket_name}")


    def download_file(self, gcs_blob_name, local_file_path):
        """
        Download a file from Google Cloud Storage.
        """
        blob = self.bucket.blob(gcs_blob_name)
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {gcs_blob_name} from bucket {self.bucket_name} to {local_file_path}")


    def download_bytes(self, gcs_blob_name):
        """
        Download bytes from Google Cloud Storage.
        """
        blob = self.bucket.blob(gcs_blob_name)
        data = blob.download_as_bytes()
        print(f"Downloaded bytes from {gcs_blob_name} in bucket {self.bucket_name}")
        return data


    def list_blobs(self, prefix=None, limit=None, page=None, search=None, limit_to_cwd=False):
        """
        List blobs in the bucket with an optional prefix.
        when limit_to_cwd is True, it will only list blobs in the prefix directory, the prefix must end with a /.
        """
        blob_iterator = self.bucket.list_blobs(prefix=prefix, page_size=limit, match_glob=search, delimiter='/' if limit_to_cwd else None)
        if page is not None:
            for i, p in enumerate(blob_iterator.pages):
                if i == page - 1:
                    for blob in p:
                        yield process_blob(blob)
                    break
        else:
            for blob in blob_iterator:
                yield process_blob(blob)


    def list_directories(self, prefix=None, limit=None, page=None, limit_to_cwd=False):
        """
        List directories in the bucket with an optional prefix.
        Directories are identified by the presence of a '#directory#' metadata file.
        when limit_to_cwd is True, it will only list blobs in the prefix directory, the prefix must end with a /.
        """
        blob_iterator = self.bucket.list_blobs(prefix=prefix, page_size=limit, match_glob='**/#directory#*', delimiter='/' if limit_to_cwd else None)
        if page is not None:
            for i, p in enumerate(blob_iterator.pages):
                if i == page - 1:
                    for blob in p:
                        yield process_blob(blob)
                    break
        else:
            for blob in blob_iterator:
                yield process_blob(blob)


    def mkdir(self, gcs_blob_name):
        """
        Create a directory metadata file in the prefix directory.
        """
        parts = gcs_blob_name.split('/')
        # append __directory__ to the last part of the path
        parts[-1] = "#directory#" + parts[-1]
        potential_dir_path = '/'.join(parts)
        # check existence of the blob
        blob = self.bucket.blob(potential_dir_path)
        if blob.exists():
            print(f"Directory {gcs_blob_name} already exists in bucket {self.bucket_name}")
            return
        # create a metadata file in the prefix directory
        blob = self.bucket.blob(potential_dir_path)
        blob.upload_from_string('')
        print(f"Created directory {gcs_blob_name} in bucket {self.bucket_name}")
    

    def probe_size(self, prefix=None):
        """
        Calculate the total size of blobs in the bucket with an optional prefix.
        """
        total_size = 0
        blobs = self.bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            yield blob.name, blob.size


    def generate_presigned_url(self, gcs_blob_name, expiration=3600):
        """
        Generate a presigned URL for a blob in the bucket.
        """
        blob = self.bucket.blob(gcs_blob_name)
        expiration_delta = timedelta(seconds=expiration)
        url = blob.generate_signed_url(expiration=expiration_delta)
        return url
    

    def delete_blob(self, gcs_blob_name):
        """
        Delete a blob from the bucket.
        """
        blob = self.bucket.blob(gcs_blob_name)
        blob.delete()
        print(f"Deleted {gcs_blob_name} from bucket {self.bucket_name}")


    def delete_prefix(self, prefix):
        """
        Delete all blobs in a directory (prefix) in the bucket.
        """
        blobs = self.bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            blob.delete()
            print(f"Deleted {blob.name} from bucket {self.bucket_name}")


    def delete_blobs(self, blob_names):
        """
        Delete multiple blobs from the bucket.
        """
        for blob_name in blob_names:
            self.delete_blob(blob_name)
