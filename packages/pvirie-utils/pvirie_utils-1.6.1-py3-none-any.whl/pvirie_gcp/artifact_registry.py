from google.cloud import artifactregistry
from google.api_core import exceptions as google_api_exceptions
import logging
import subprocess
import os

from . import gcp

# Access Cloud Storage

def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    client = artifactregistry.ArtifactRegistryClient(credentials=credentials)
    return client


class Docker_Registry:
    def __init__(self, project_id, location, repository, credentials=None):
        self.session = get_session(credentials)
        self.project_id = project_id
        self.location = location
        self.repository = repository

        host = f"{self.location}-docker.pkg.dev"
        self.artifact_registry = f"{host}/{self.project_id}/{self.repository}"


    def build_and_push_image(self, docker_client, image_name, tag, dockerfile_path, dockerfile_context, use_persistent=True, platform='linux/amd64'):
        """
        Build and push a Docker image to Artifact Registry.
        To ensure compatibility with Artifact Registry, use platform='linux/amd64' when building on non-linux systems.
        """
        gcp.ensure_console_login(use_persistent)
        try:
            gcp.config_docker(self.location)
        except Exception as e:
            logging.warning(f"Error configuring Docker for Artifact Registry: {e}")
        
        full_image_name = f"{self.artifact_registry}/{image_name}:{tag}"
        build_command = [
            "docker", "buildx", "build",
            "--platform", platform,
            "-t", full_image_name,
            "-f", dockerfile_path,
            dockerfile_context,
            "--push"
        ]
        logging.info(f"Running buildx command: {' '.join(build_command)}")
        result = subprocess.run(build_command, capture_output=True, text=True)

        for line in result.stdout.splitlines():
            yield line

        if result.returncode != 0:
            for line in result.stderr.splitlines():
                yield line
    

    def list_images(self):
        parent_repo = self.session.repository_path(self.project_id, self.location, self.repository)
        logging.info(f"Listing packages (image names) in repository: {parent_repo}")

        try:
            package_pager = self.session.list_packages(parent=parent_repo)
            image_names = [pkg.name.split('/')[-1] for pkg in package_pager] # Extract just the image name
            return image_names
        except google_api_exceptions.PermissionDenied:
            logging.error(f"Permission denied listing packages in {parent_repo}. Need artifactregistry.reader role?")
        except Exception as e:
            logging.error(f"Error listing packages: {e}")
        return None


    def list_versions(self, image_name: str):
        parent_package = self.session.package_path(self.project_id, self.location, self.repository, image_name)
        logging.info(f"Listing versions for package: {parent_package}")

        try:
            # Use view=FULL to include tag information with versions
            request = artifactregistry.ListVersionsRequest(parent=parent_package, view=artifactregistry.VersionView.FULL)
            version_pager = self.session.list_versions(request=request)

            versions = []
            for version in version_pager:
                # Extract the digest and tags
                tags = version.related_tags
                if tags:
                    tag = tags[0].name
                    parts = tag.split('/')
                    if len(parts) > 1:
                        tag = parts[-1]
                    # Extract the creation time
                    created_time = version.create_time
                    versions.append({'tag': tag, 'created_time': created_time, 'full_name': version.name})
                else:
                    versions.append({'full_name': version})
            return versions
        
        except google_api_exceptions.NotFound:
            logging.error(f"Package (image) '{image_name}' not found in repository.")
        except google_api_exceptions.PermissionDenied:
            logging.error(f"Permission denied listing versions/tags for {parent_package}. Need artifactregistry.reader role?")
        except Exception as e:
            logging.error(f"Error listing versions/tags: {e}")
        return None