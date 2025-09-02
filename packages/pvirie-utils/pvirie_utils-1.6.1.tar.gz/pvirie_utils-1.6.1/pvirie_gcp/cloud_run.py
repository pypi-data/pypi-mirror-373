from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from google.cloud import run_v2 as run
from google.protobuf.json_format import MessageToDict, ParseDict, ParseError

from . import gcp, secret_manager


def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    client = run.ServicesClient(credentials=credentials)
    return client


def get_containers_list(service_object: run.types.Service) -> Optional[List[Dict[str, Any]]]:
    """
    Helper to find the list of containers in common Cloud Run Service structures.
    Returns None if the containers path is not found or is not a list.
    """
    containers = None
    # Check if the service object has a 'template' field
    if hasattr(service_object, 'template'):
        # Check if the template has a 'containers' field
        if hasattr(service_object.template, 'containers'):
            containers = service_object.template.containers

    # Check if the service object has a 'spec' field
    elif hasattr(service_object, 'spec'):
        # Check if the spec has a 'template' field
        if hasattr(service_object.spec, 'template'):
            # Check if the template has a 'containers' field
            if hasattr(service_object.spec.template, 'containers'):
                containers = service_object.spec.template.containers
    return containers


class Service_Configuration:

    def __init__(self, project_id, location, credentials=None):
        self.session = get_session(credentials)
        self.project_id = project_id
        self.location = location

    def get_service(self, service_name: str) -> Optional[run.types.Service]:
        # service_name is not the fully qualified name, but rather the service name you see in the gcp ui
        service_id = service_name
        try:
            service_name_fqn = self.session.service_path(self.project_id, self.location, service_id)
            request = run.GetServiceRequest(name=service_name_fqn)
            service = self.session.get_service(request=request)
            return service
        except Exception as e:
            logging.error(f"Error getting service {service_id}: {e}")
            return None


    def save_service_json(self, service, output_path: str):
        # Convert the service object message to json using to_json
        service_str = run.types.Service.to_json(service)
        # Save the JSON to a file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(service_str)
        logging.info(f"Service configuration saved to {output_path}")


    def load_service_json(self, service_json_path: str) -> Optional[run.types.Service]:
        try:
            with open(service_json_path, 'r', encoding='utf-8') as f:
                service_json_str = f.read()
                service_object = run.types.Service.from_json(service_json_str)
                return service_object
        except FileNotFoundError:
            logging.error(f"Error: file not found at {service_json_path}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON file: {e}")
            return None
        

    def get_full_image_name(self, image_name: str) -> str:
        return f"{self.location}-docker.pkg.dev/{self.project_id}/docker-registry/{image_name}"
        

    def update_service(self, service, container_images: List[Tuple[str, str, str]]):
        # container_images is a list of tuples (base_image_name, new_image_name, new_tag)
        # for example
        # base_image_name: an_image
        # new_image_name: (can be none if you want to keep the same name)
        # tag: abcd

        new_service = run.types.Service.from_json(run.types.Service.to_json(service))
        containers = get_containers_list(new_service)
        if containers is None:
            logging.warning(f"Warning: No 'containers'.")
            return service
        if not containers: # Handles empty list case
            logging.warning(f"Information: 'containers' is an empty list.")
            return service

        was_modified = False
        for container_index, container_def in enumerate(containers):
            current_image_spec = container_def.image
            for target_base_image_name, new_image_name, new_tag in container_images:
                target_base_image_name = self.get_full_image_name(target_base_image_name)
                if not isinstance(target_base_image_name, str) or not isinstance(new_tag, str) or not target_base_image_name or not new_tag:
                    logging.warning(f"Warning: Invalid entry in container_images: ({target_base_image_name}, {new_tag}). Both parts must be non-empty strings. Skipping this entry.")
                    continue

                if new_image_name is None:
                    new_image_name = target_base_image_name
                else:
                    new_image_name = self.get_full_image_name(new_image_name)

                is_match = False
                if current_image_spec == target_base_image_name:
                    # Exact match (e.g., current image has no tag/digest, matches base name)
                    is_match = True
                elif current_image_spec.startswith(target_base_image_name):
                    # Check if the part after target_base_image_name is a tag/digest separator
                    suffix = current_image_spec[len(target_base_image_name):]
                    if suffix.startswith(':') or suffix.startswith('@'):
                        is_match = True
                
                if is_match:
                    new_full_image_spec = f"{new_image_name}:{new_tag}"
                    if current_image_spec != new_full_image_spec:
                        logging.info(f"  Updating image for container: '{container_def.name}'")
                        logging.info(f"    Old image: {current_image_spec}")
                        logging.info(f"    New image: {new_full_image_spec}")
                        container_def.image = new_full_image_spec
                        was_modified = True
                    break

        if was_modified:
            logging.info(f"Service configuration modified.")
        else:
            logging.info(f"No changes made.")
        
        return new_service
        

    def redeploy_service(self, service, validate_only=False):
        try:
            # --- Use UpdateService with allow_missing=True for "upsert" behavior ---
            update_request = run.UpdateServiceRequest(
                service=service,
                validate_only=validate_only,
                allow_missing=True  # This enables create if not exists
            )

            logging.info(f"Deploying service {service.name} to location '{self.location}'...")

            operation = self.session.update_service(request=update_request)

            if not validate_only:
                logging.info(f"Operation initiated: {operation.operation.name}")
                logging.info("Waiting for operation to complete...")
                
                # Wait for the operation to complete with a timeout
                # The LRO (Long-Running Operation) metadata can provide progress,
                # but result() is simpler for blocking until completion.
                try:
                    # The actual result of an UpdateService operation upon success is the Service object itself.
                    # result() will raise an exception if the operation failed.
                    completed_service = operation.result(timeout=300) # Timeout in seconds (e.g., 5 minutes)
                    logging.info(f"Service '{completed_service.name}' deployed successfully.")
                    logging.info(f"Service URI: {completed_service.uri}")
                except TimeoutError:
                    logging.info(f"Timeout waiting for service deployment to complete for operation: {operation.operation.name}")
                    logging.info("The operation may still be in progress. Check the Google Cloud Console.")
                except Exception as e:
                    logging.info(f"Deployment failed for service '{service.name}': {e}")
            else:
                logging.info(f"Validation request for service '{service.name}' prepared. No deployment action taken.")

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        
