from typing import Optional, List, Dict, Any, Union
import logging
import os
import requests
from enum import Enum
from bioblend import galaxy
from nbitk.config import Config
from nbitk.logger import get_formatted_logger
import time
import sys

class BaseClient:
    """
    Base class for Galaxy tool clients that handles common operations and cleanup.
    Provides standardized interfaces for Galaxy instance management, history handling,
    file uploads and downloads, and job monitoring. Subclasses should implement
    tool-specific methods for running analyses and processing results.
    """

    def __init__(self, config: Config, tool_name: str = None, workflow_name: str = None, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the BaseClient with a configuration object and optional logger.
        :param config: A Config object containing Galaxy connection settings. May contain
            the following keys:
            - 'galaxy_api_key' (optional; if absent, must be set as environment variable 'GALAXY_API_KEY')
            - 'galaxy_domain' (optional, default 'galaxy.naturalis.nl')
            - 'log_level' (optional, default 'WARNING')
            - 'preserve_history' (optional, default False)
        :param tool_name:
        :param logger:
        """
        self.config = config
        if config.get('log_level') is None:
            config.set('log_level', 'WARNING')
        self.logger = logger or get_formatted_logger(__name__, config)
        self._preserve_history = config.get('preserve_history', False)
        self._gi = self._initialize_galaxy_instance()
        self._history: Optional[Dict[str, Any]] = None
        self.tool_name = tool_name
        self.workflow_name = workflow_name

    def _initialize_galaxy_instance(self) -> galaxy.GalaxyInstance:
        """
        Initialize connection to Galaxy server using configuration settings.

        :return: Configured bioblend Galaxy instance
        :raises RuntimeError: if unable to establish connection to Galaxy
        """
        try:
            domain: str = self.config.get('galaxy_domain')
            if not domain:
                domain = os.environ.get('GALAXY_DOMAIN')
                if not domain:
                    raise RuntimeError("No Galaxy domain found in config or environment")
            self.logger.debug(f"Connecting to Galaxy instance at {domain}")
        
            key: str = self._get_api_key()
            gi = galaxy.GalaxyInstance(url=domain, key=key)
            gi.max_get_attempts = 5
            return gi
        except Exception as e:
            self.logger.error(f"Error retrieving Galaxy domain ensure: {e}")
            raise
        

    def _get_api_key(self) -> str:
        """
        Retrieve Galaxy API key from either config or environment variables.

        :return: Valid Galaxy API key
        :raises RuntimeError: if no API key is found in config or environment
        """
        key: Optional[str] = self.config.get('galaxy_api_key')
        if not key:
            key = os.environ.get('GALAXY_API_KEY')
        if not key:
            raise RuntimeError("No Galaxy API key found in config or environment")
        return key

    def _ensure_history(self, history_name: str = None) -> Dict[str, Any]:
        """
        Create a new Galaxy history or return existing one. History names are prefixed
        with 'nbitk_' followed by the object's id for tracking purposes.

        :return: Galaxy history object with at minimum an 'id' key
        """
        if self._history is None:
            name = history_name if history_name is not None else f'nbitk_{id(self)}'
            self._history = self._gi.histories.create_history(name)
            self.logger.debug(f"Created Galaxy history {self._history['id']}")
            return self._history
        else:
            self.logger.debug(f"Using existing Galaxy history {self._history['id']}")
            return self._history

    def _upload_file(self, file_path: str, file_type: str) -> str:
        """
        Upload a file to the current Galaxy history.

        :param file_path: Path to file to upload
        :param file_type: Galaxy datatype for the file (e.g., 'tabular', 'fasta')
        :return: Dataset ID of the uploaded file
        :raises RuntimeError: if upload fails or no history exists
        :raises FileNotFoundError: if file_path does not exist
        """
        history = self._ensure_history()
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")
            self.logger.debug(f"Uploading file {file_path} to Galaxy history {history['id']}")
            # Upload the file   
            return self._gi.tools.upload_file(
                file_path,
                history_id=history['id'],
                file_type=file_type
            )
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {str(e)}")
            raise

    def _download_result_content(self, output: dict) -> str:
        """
        Download a dataset from Galaxy and return its content as a string.

        :param output: Output dataset dictionary from Galaxy
        :return: Content of the downloaded dataset as a string
        :raises RuntimeError: if download fails
        """
        try:
            # external user URL is different than that inside the GUI
            url = f'{self._gi.base_url}/api/datasets/{output["id"]}/display?to_ext={output["file_ext"]}'
            self.logger.debug(f"Downloading result content from {url}")
            response = requests.get(
                url,
                headers={"x-api-key": self._gi.key},
                allow_redirects=True
            )
            response.raise_for_status()
            return response.text

        except Exception as e:
            self.logger.error(f"Failed to download result {output['id']}: {str(e)}")
            raise

    def _download_result(self, output: dict, extension: str) -> str:
        """
        Download a dataset from Galaxy and save to a local file.

        :param output: Output dataset dictionary from Galaxy
        :param extension: File extension to save the dataset as
        :return: Path to downloaded file
        :raises RuntimeError: if download fails
        """
        try:
            # external user URL is different than that inside the GUI
            url = f'{self._gi.base_url}/api/datasets/{output["id"]}/display?to_ext={output["file_ext"]}'
            response = requests.get(
                url,
                headers={"x-api-key": self._gi.key},
                allow_redirects=True
            )
            response.raise_for_status()

            # Save to file
            output_path = f"{output['output_name']}_{output['id']}.{extension}"
            with open(output_path, 'w') as f:
               f.write(response.text)

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to download result {output['id']}: {str(e)}")
            raise

    def export_history_as_rocrate(self, target_path: str, include_hidden: bool = False,
                                  include_deleted: bool = False, max_wait: int = 50) -> str:
        """
        Export the current Galaxy history as an RO-crate zip file.

        :param target_path: Local path where the RO-crate zip should be saved
        :param include_hidden: Whether to include hidden datasets
        :param include_deleted: Whether to include deleted datasets
        :return: Path to the downloaded RO-crate file
        :raises RuntimeError: if export fails or no history exists
        """
        if not self._history:
            raise RuntimeError("No active history to export")

        try:
            # Prepare the export request payload
            payload = {
                "model_store_format": "rocrate.zip",
                "include_files": True,
                "include_hidden": include_hidden,
                "include_deleted": include_deleted,
                
            }

            # trigger export to short term storage
            url = f"{self._gi.base_url}/api/histories/{self._history['id']}/prepare_store_download"
            self.logger.info(f"Initiating RO-crate export for history {self._history['id']}")
            trigger_response = self._gi.make_post_request(url, payload=payload) 

            download_url = f"{self._gi.base_url}/api/short_term_storage/{trigger_response['storage_request_id']}"
            retry_seconds = 0
            while True:
                try:
                    retry_seconds += 5
                    # check if the export is ready 
                    export_status_url = f"{self._gi.base_url}/api/short_term_storage/{trigger_response['storage_request_id']}/ready"
                    export_status_code = self._gi.make_get_request(export_status_url).json()
                    
                    with requests.get(download_url, stream=True) as download_response:
                        
                        if download_response.status_code == 200 and export_status_code is True:
                            with open(target_path, "wb") as f:
                                f.write(download_response.content)
                            self.logger.info("Download complete")
                            break
                        elif (download_response.status_code in [500, 202] and 
                              download_response.text == "Internal Server Error" and 
                              export_status_code is False):
                            self.logger.info("Export not ready, retrying...")
                            time.sleep(5)  # Wait for 5 seconds before retrying         
                        else:
                            self.logger.error("Error:", download_response.status_code)
                            self.logger.error("download_response:", download_response.text)
                            raise Exception("Error in response while exporting the rocrate")

                        if retry_seconds > max_wait:
                            raise Exception("Error timeout while exporting the rocrate; consider increasing the max_wait parameter")
                except requests.exceptions.RequestException as e:
                    raise

        except Exception as e:
            self.logger.error(f"Failed to export history as RO-crate: {str(e)}")
            raise

    def __del__(self) -> None:
        """
        Cleanup Galaxy history unless explicitly preserved. This will attempt to delete
        the associated Galaxy history if self._preserve_history is False. Failures to
        delete are logged but do not raise exceptions.
        """
        if self._history and self._preserve_history is False:
            try:
                self.logger.debug(f"Going to clean up Galaxy history {self._history['id']}")
                self._gi.histories.delete_history(self._history['id'])
            except Exception as e:
                self.logger.warning(f"Failed to cleanup history: {str(e)}")
