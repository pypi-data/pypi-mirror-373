import os
import logging
import subprocess
from google.oauth2 import service_account


def get_credentials():
    # Load credentials from the key file
    gcp_file = os.getenv('GCP_CREDENTIALS', None)
    if gcp_file is None:
        return None
    credentials = service_account.Credentials.from_service_account_file(
        gcp_file,
        scopes=[
            'https://www.googleapis.com/auth/drive', # For Google Drive
            'https://www.googleapis.com/auth/spreadsheets',  # For Google Sheets
            'https://www.googleapis.com/auth/cloud-platform',  # For Vertex AI and Cloud Storage
        ]
    )
    return credentials


def find_gcloud():
    if os.name == 'posix':
        # check if gcloud is in PATH
        gcloud_path = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if gcloud_path.returncode == 0:
            gcloud_path = gcloud_path.stdout.strip()
            if os.path.exists(gcloud_path):
                return gcloud_path
        # macOS specific path
        username = os.getlogin()
        local_gcloud = f"/Users/{username}/google-cloud-sdk/bin/gcloud"
        if os.path.exists(local_gcloud):
            return local_gcloud
        # get from /usr/local/bin
        global_gcloud = "/usr/local/bin/gcloud"
        if os.path.exists(global_gcloud):
            return global_gcloud
    else:
        # polyfill for Windows
        username = os.getlogin()
        local_gcloud = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"
        if os.path.exists(local_gcloud):
            return local_gcloud
        # get from Program Files
        global_gcloud = "C:\\Program Files\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"
        if os.path.exists(global_gcloud):
            return global_gcloud
    return None


def ensure_console_login(use_persistent=True):
    gcloud_path = find_gcloud()
    logging.info(f"gcloud_path: {gcloud_path}")
    try:
        # first check if gcloud is installed
        subprocess.run([gcloud_path, 'version'], check=True, capture_output=True)
    except FileNotFoundError:
        logging.error("gcloud CLI is not installed. Please install it to use this function.")
        raise RuntimeError("gcloud CLI is not installed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking gcloud version: {e.stderr}")
        raise RuntimeError("Error checking gcloud version.")
    
    if use_persistent:
        try:
            # Check if the user is already logged in
            process = subprocess.run([gcloud_path, 'auth', 'list'], check=True, capture_output=True, text=True)

            result = process.stdout + process.stderr
            if "No credentialed accounts" in result:
                pass
            else:
                logging.info("Already logged in to gcloud.")
                return gcloud_path
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running gcloud auth list: {e.stderr}")
            raise RuntimeError("Error running gcloud auth list.")

    try:
        # Check if the service account key file exists
        key_file_path = os.getenv('GCP_CREDENTIALS')
        # Set environment variable for the subprocess call
        env_with_adc = os.environ.copy()
        env_with_adc['GOOGLE_APPLICATION_CREDENTIALS'] = key_file_path

        # gcloud auth activate-service-account --key-file=/path/to/your/service-account-key.json
        process = subprocess.run(
            [gcloud_path, 'auth', 'activate-service-account', '--key-file', key_file_path],
            check=True,
            capture_output=True,
            text=True,
            env=env_with_adc # Pass the environment with the ADC variable set
        )
        logging.info("'gcloud auth activate-service-account' executed successfully.")
        logging.debug(f"gcloud stdout:\n{process.stdout}")
        if process.stderr and process.stderr.strip():
            logging.warning(f"gcloud stderr:\n{process.stderr}")
        return gcloud_path
    except FileNotFoundError as e:
        logging.error(f"Input file not found: {e}")
    except subprocess.CalledProcessError as e:
        logging.error(f"'gcloud auth configure-docker' failed with exit code {e.returncode}")
        logging.error(f"Stderr:\n{e.stderr}")
        logging.error(f"Stdout:\n{e.stdout}")
        logging.error("Check if the service account key is valid and has permissions.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while running subprocess: {e}")
    raise RuntimeError("Failed to run 'gcloud auth activate-service-account'.")


def config_docker(location):
    gcloud_path = find_gcloud()
    try:
        process = subprocess.run([gcloud_path, 'auth', 'configure-docker', f"{location}-docker.pkg.dev"], check=True, capture_output=True, text=True)
        logging.info("'gcloud auth configure-docker' executed successfully.")
        logging.debug(f"gcloud stdout:\n{process.stdout}")
        if process.stderr and process.stderr.strip():
            logging.warning(f"gcloud stderr:\n{process.stderr}")
    except FileNotFoundError as e:
        logging.error(f"Input file not found: {e}")
    except subprocess.CalledProcessError as e:
        logging.error(f"'gcloud auth configure-docker' failed with exit code {e.returncode}")
        logging.error(f"Stderr:\n{e.stderr}")
        logging.error(f"Stdout:\n{e.stdout}")
        logging.error("Check if the service account key is valid and has permissions.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while running subprocess: {e}")
    raise RuntimeError("Failed to run 'gcloud auth configure-docker'.")