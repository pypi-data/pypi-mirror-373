import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload, MediaIoBaseDownload
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading


try:
    from . import gcp
except ImportError:
    import gcp


def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    # Access Google Drive
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service


class Drive:

    def __init__(self, credentials=None):
        self.session = get_session(credentials)


    # list all drive id, name, parent (shared and not shared) folder by prefix
    def find_folders(self, prefix, exact_match=False, parent_id=None):
        if exact_match:
            q = f"mimeType='application/vnd.google-apps.folder' and name = '{prefix}'"
        else:
            q = f"mimeType='application/vnd.google-apps.folder' and name contains '\"{prefix}\"'"

        if parent_id is not None:
            q += f" and '{parent_id}' in parents"

        # get all pages
        pageToken = None
        result_items = []
        while True:
            results = self.session.files().list(
                q=q,
                spaces='drive',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='nextPageToken, files(id, name, parents)',
                pageToken=pageToken
            ).execute()
            items = results.get('files', [])
            result_items.extend(items)

            pageToken = results.get('nextPageToken', None)
            if pageToken is None:
                break

        return result_items


    def list_folders(self, folder_id):
        pageToken = None
        result_items = []
        while True:
            results = self.session.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=pageToken
            ).execute()
            items = results.get('files', [])
            result_items.extend(items)

            pageToken = results.get('nextPageToken', None)
            if pageToken is None:
                break

        return result_items


    def list_folder_files(self, folder_id):
        pageToken = None
        result_items = []
        while True:
            results = self.session.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='nextPageToken, files(id, name, mimeType, size, md5Checksum)',
                pageToken=pageToken
            ).execute()
            items = results.get('files', [])
            result_items.extend(items)

            pageToken = results.get('nextPageToken', None)
            if pageToken is None:
                break

        return result_items


    def recursive_list_folder_files(self, folder_id):
        out_files = {}
        files = self.list_folder_files(folder_id)
        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                sub_files = self.recursive_list_folder_files(file['id'])
                # add path to sub_files
                for sub_file in sub_files.keys():
                    sub_file_name = os.path.join(file['name'], sub_file)
                    out_files[sub_file_name] = sub_files[sub_file]
            else:
                out_files[file['name']] = file
        return out_files


    def create_folder(self, parent_id, name):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id is not None:
            file_metadata['parents'] = [parent_id]
        file = self.session.files().create(body=file_metadata, supportsAllDrives=True, fields='id').execute()
        return file.get('id')


    def upsert_folder(self, parent_id, name):
        folders = self.find_folders(name, exact_match=True, parent_id=parent_id)
        if len(folders) == 0:
            return self.create_folder(parent_id, name)
        return folders[0]['id']


    def batch_create_folder(self, batch, parent_id, name):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id is not None:
            file_metadata['parents'] = [parent_id]

        batch.append({
            "method": "create",
            "params": {
                "body": file_metadata,
                "supportsAllDrives": True,
                "fields": "id"
            }
        })


    def get_file_meta(self, file_id):
        # get id, name, mimeType, size, parent
        result = self.session.files().get(fileId=file_id, fields='id, name, mimeType, size, parents', supportsAllDrives=True).execute()
        return result


    def get_file_data(self, file_id):
        byte_data = self.session.files().get_media(fileId=file_id, supportsAllDrives=True).execute()
        return byte_data


    def get_raw_file(self, folder_id, file_name):
        files = self.list_folder_files(folder_id)
        for file in files:
            if file['name'] == file_name:
                byte_data = self.get_file_data(file['id'])
                return byte_data
        return None


    def get_json_file(self, folder_id, file_name):
        data = self.get_raw_file(folder_id, file_name)
        if data is None:
            return None
        return pickle.loads(data)


    def create_raw_file(self, folder_id, file_name, data):
        # data is bytes
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaInMemoryUpload(data, resumable=True)
        file = self.session.files().create(body=file_metadata, media_body=media, supportsAllDrives=True, fields='id').execute()
        return file.get('id')


    def create_json_file(self, folder_id, file_name, data):
        # data is a dictionary
        byte_data = pickle.dumps(data)
        return self.create_raw_file(folder_id, file_name, byte_data)


    def update_raw_file(self, folder_id, file_name, data):
        file = self.get_raw_file(folder_id, file_name)
        if file is None:
            return None
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaInMemoryUpload(data, resumable=True)
        file = self.session.files().update(fileId=file['id'], body=file_metadata, media_body=media, supportsAllDrives=True, fields='id').execute()
        return file.get('id')


    def update_json_file(self, folder_id, file_name, data):
        byte_data = pickle.dumps(data)
        return self.update_raw_file(folder_id, file_name, byte_data)
        

    def batch_upload(self, batch, files, local_root, drive_id):
        # first upsert all folders
        # retrieve all folder paths
        directory_to_id = {"" : drive_id}
        directory_structure = {}
        for file in files:
            file_dir = os.path.dirname(file)
            if file_dir == "":
                continue
            parts = file_dir.split(os.path.sep)
            path = ""
            pointer = directory_structure
            parent_drive_id = drive_id
            for i, dirname in enumerate(parts):
                path = os.path.join(path, dirname)
                if dirname not in pointer:
                    pointer[dirname] = {}
                    parent_drive_id = self.upsert_folder(parent_drive_id, dirname)
                    directory_to_id[path] = parent_drive_id
                else:
                    parent_drive_id = directory_to_id[path]
                pointer = pointer[dirname]

        for file in files:
            file_path = os.path.join(local_root, file)
            if os.path.isdir(file_path):
                continue

            filename = os.path.basename(file)
            file_relative_directory = os.path.dirname(file)
            # media = MediaFileUpload(file_path, resumable=True)
            file_metadata = {
                'name': filename,
                'parents': [directory_to_id[file_relative_directory]]
            }

            batch.append({
                "method": "create",
                "file_path": file_path,
                "params": {
                    "body": file_metadata,
                    "supportsAllDrives": True,
                    "fields": "id"
                }
            })


thread_local = threading.local()

def process_request(request):
    if not hasattr(thread_local, "drive_session"):
        thread_local.drive_session = get_session()
    drive_session = thread_local.drive_session

    if request["method"] == "create":
        params = request["params"]
        media = MediaFileUpload(request["file_path"], resumable=True)
        params["media_body"] = media
        try:
            file = drive_session.files().create(**params).execute()
        except Exception as e:
            logging.error(f"Failed to upload file: {request['file_path']}")
            logging.error(e)
            return {
                "success": False,
                "error": e,
                "file_path": request["file_path"]
            }
        return {
            "success": True,
            "file": file
        }
    elif request["method"] == "update":
        params = request["params"]
        media = MediaFileUpload(request["file_path"], resumable=True)
        params["media_body"] = media
        try:
            file = drive_session.files().update(**params).execute()
        except Exception as e:
            logging.error(f"Failed to update file: {request['file_path']}")
            logging.error(e)
            return {
                "success": False,
                "error": e,
                "file_path": request["file_path"]
            }
        return {
            "success": True,
            "file": file
        }
    elif request["method"] == "delete":
        params = request["params"]
        try:
            drive_session.files().delete(**params).execute()
        except Exception as e:
            logging.error(f"Failed to delete file: {request['file_path']}")
            logging.error(e)
            return {
                "success": False,
                "error": e,
                "file_path": request["file_path"]
            }
        return {
            "success": True
        }
    elif request["method"] == "download":
        params = request["params"]
        try:
            r_object = drive_session.files().get_media(**params)
            with open(request["file_path"], 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, r_object)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logging.info(f"Download {int(status.progress() * 100)}.")
        except Exception as e:
            logging.error(f"Failed to download file: {request['file_path']}")
            logging.error(e)
            return {
                "success": False,
                "error": e,
                "file_path": request["file_path"]
            }
        return {
            "success": True
        }


def execute_batch_threaded(batch, num_workers=10):
    if len(batch) == 0:
        return 0, []
    
    failed = []
    success_count = 0
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(process_request, batch)
        for result in results:
            if result["success"]:
                success_count += 1
            else:
                failed.append(result)

    logging.info(f"Failed: {len(failed)}")

    return success_count, failed


def calculate_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Sync_Session:
    def __init__(self, local_folder_path, uplink_folder_id):
        self.drive_service = Drive()
        self.local_folder_path = local_folder_path
        self.uplink_folder_id = uplink_folder_id

        self.marks = {
            "upload": set(),
            "replace": set(),
            "download": set(),
            "delete": set()
        }


    def __enter__(self):
        if not os.path.exists(self.local_folder_path):
            os.makedirs(self.local_folder_path)

        # list all files in the uplink
        self.uplink_files = set()
        self.uplink_file_hash = {}
        self.uplink_files_metadata = self.drive_service.recursive_list_folder_files(self.uplink_folder_id)
        for file in self.uplink_files_metadata.keys():
            metadata = self.uplink_files_metadata[file]
            if 'md5Checksum' not in metadata:
                continue
            self.uplink_files.add(file)
            self.uplink_file_hash[file] = self.uplink_files_metadata[file]['md5Checksum']

        # list all files in the local, use relative path to the local_folder_path
        self.local_files = set()
        self.local_file_hash = {}
        for root, dirs, files in os.walk(self.local_folder_path):
            for file in files:
                file_id = os.path.relpath(os.path.join(root, file), self.local_folder_path)
                self.local_files.add(file_id)
                self.local_file_hash[file_id] = calculate_md5(os.path.join(root, file))

        return self
 

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # perform marks

        batch = []
        
        if len(self.marks["upload"]) > 0:
            self.drive_service.batch_upload(batch, self.marks["upload"], self.local_folder_path, self.uplink_folder_id)

        for file in self.marks["replace"]:
            # full filepath
            file_metadata = self.uplink_files_metadata[file]
            batch.append({
                "method": "update",
                "file_path": os.path.join(self.local_folder_path, file),
                "params": {
                    "fileId": file_metadata['id'],
                    "supportsAllDrives": True
                }
            })


        for file in self.marks["download"]:
            # full filepath
            file_metadata = self.uplink_files_metadata[file]
            # make dirs
            os.makedirs(os.path.dirname(os.path.join(self.local_folder_path, file)), exist_ok=True)
            batch.append({
                "method": "download",
                "file_path": os.path.join(self.local_folder_path, file),
                "params": {
                    "fileId": file_metadata['id'],
                    "supportsAllDrives": True
                }
            })


        for file in self.marks["delete"]:
            # delete uplink file
            file_metadata = self.uplink_files_metadata[file]
            batch.append({
                "method": "delete",
                "params": {
                    "fileId": file_metadata['id'],
                    "supportsAllDrives": True
                }
            })


        logging.info(f"Total batch requests: {len(batch)}")
        success_count, failed = execute_batch_threaded(batch, num_workers=10)

        # clear marks
        self.marks = {
            "upload": set(),
            "replace": set(),
            "download": set(),
            "delete": set()
        }


    def get_drive_name(self):
        return self.drive_service.get_file_meta(self.uplink_folder_id)['name']
    

    def get_uplink_missing_files(self):
        return self.local_files - self.uplink_files


    def get_local_missing_files(self):
        return self.uplink_files - self.local_files


    def get_diff_files(self):
        # get intersect files
        intersect = self.local_files & self.uplink_files
        # check md5 hash
        diff_files = []
        for file in intersect:
            if self.local_file_hash[file] != self.uplink_file_hash[file]:
                diff_files.append(file)
        return diff_files


    def mark_for_upload_files(self, files):
        self.marks["upload"].update(files)

    def mark_for_replace_uplink(self, files):
        self.marks["replace"].update(files)

    def mark_for_download_files(self, files):
        self.marks["download"].update(files)

    def mark_for_delete_files(self, files):
        self.marks["delete"].update(files)


if __name__ == '__main__':
    # set print info
    logging.basicConfig(level=logging.INFO)

