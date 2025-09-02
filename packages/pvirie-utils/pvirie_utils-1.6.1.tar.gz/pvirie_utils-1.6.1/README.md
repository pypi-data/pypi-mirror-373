# python-utils

My personal collection of python utility functions.

## pvirie-gcp

This module contains utility functions for working with Google Cloud Platform (GCP) services.

### Installation

0. Install python [gcloud sdk](https://cloud.google.com/sdk/docs/install).
1. For macOS users, copy the gcloud sdk folder to `/Users/<username>/`
2. Add environment `GCP_CREDENTIALS` with the path to the GCP credentials file.
3. Install additional dependencies for each service you want to use. For example, to use Google Cloud Storage, Artifact Registry, Secret Manager, IAM, Cloud run, use the following command:
    ```bash
    pip install google-cloud-storage google-cloud-artifact-registry google-cloud-secret-manager google-cloud-iam google-cloud-run
    ```
