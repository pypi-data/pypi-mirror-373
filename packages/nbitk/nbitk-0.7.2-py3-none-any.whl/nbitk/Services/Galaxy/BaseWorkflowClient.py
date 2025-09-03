from nbitk.Services.Galaxy.BaseClient import BaseClient
from nbitk.config import Config
from typing import Optional, Dict, Any
import os
import logging
from nbitk.logger import get_formatted_logger
import requests
import time


class BaseWorkflowClient(BaseClient):
    """
    Base class for Galaxy workflow clients that handles common operations and cleanup.
    Provides standardized interfaces for Galaxy instance management, history handling,
    file uploads and downloads, and job monitoring. Subclasses should implement
    workflow-specific methods for running analyses and processing results.
    """

    def __init__(self, config: Config, workflow_name: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, workflow_name, logger)
        self._preserve_history = True
        self.workflowInvocation = None
        self.results = None
        self.workflow_id = self._get_workflow(workflow_name)['id']
      

    def invoke_workflow(self, input_data: Dict[str, Any],params: Dict[str, Any]) -> None:
        """
        start the workflow with the given parameters. This method should be implemented by subclasses.
        :param params: Dictionary of parameters for the workflow
        """
        try:
            self.logger.debug(f"Running workflow {self.workflow_id} with parameters: {params}")
            self.workflowInvocation = self._gi.workflows.invoke_workflow(
                history_id=self._history['id'],
                workflow_id=self.workflow_id,
                inputs=input_data,
                params=params,
                inputs_by='step_index'
                
                )
            self.logger.debug(f"Workflow {self.workflow_id} submitted with job ID: {self.workflowInvocation['id']}")
        except Exception as e:
            self.logger.error(f"Error running workflow {self.workflow_id}: {e}")
            raise
    
    def _get_workflow(self, name: str) -> Dict[str, Any]:
        """
        Get workflow by name from Galaxy. The name is provided in bold at the top of the workflow form.
        For example: `Identify reads with blastn and find taxonomy`

        :param name: Name of the workflow to retrieve
        :return: Workflow dictionary containing at least 'id' key
        :raises RuntimeError: if workflow is not found
        """
        workflows = self._gi.workflows.get_workflows(name=name)
        if not workflows:
            raise RuntimeError(f"Workflow '{name}' not found")
        return workflows[0]
    
    def create_workflow_from_history(self, workflow_name: str = None, job_ids: list = None) -> None:
        """
        Create a workflow from the current history.

        :param history_id: ID of the history to create a workflow from
        :raises RuntimeError: if creation fails or no history exists
        """
        if not self._history:
            raise RuntimeError("No active history to create workflow from")

        try:
            return self._gi.workflows.extract_workflow_from_history(
                history_id=self._history['id'],
                workflow_name=workflow_name or f"Workflow from {self._history['name']}",
                job_ids=job_ids 
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow from history: {str(e)}")
            raise

    # blue print to export worfkflow_invocation to RO-crate 
    # make post request to: /api/invocations/{invocation_id}/prepare_store_download
    # check if export is ready with: /api/short_term_storage/{trigger_response['storage_request_id']}/ready
    # then download from: /api/short_term_storage/{trigger_response['storage_request_id']}

    def export_workflow_invocation(self,
                                   target_path: str,
                                   invocation_id: str,
                                   export_format: str = "rocrate.zip",
                                   include_hidden: bool = False,
                                   include_deleted: bool = False,
                                   max_wait: int = 50) -> str:
        """
        Export the current Galaxy workflow invocation as an RO-crate zip file.

        :param target_path: Local path where the RO-crate zip should be saved
        :param export_format: Format of the export (default is "rocrate.zip")
        :param invocation_id: ID of the workflow invocation to export 
        :param include_hidden: Whether to include hidden datasets
        :param include_deleted: Whether to include deleted datasets
        :param max_wait: Maximum wait time in seconds for the export to be ready
        :return: Path to the downloaded RO-crate file
        :raises RuntimeError: if export fails or no history exists
        """
        try:
            # Prepare the export request payload
            payload = {
                "model_store_format": export_format,
                "include_files": True,
                "include_hidden": include_hidden,
                "include_deleted": include_deleted
            }

            
            # trigger export to short term storage
            
            url = f"{self._gi.base_url}/api/invocations/{invocation_id}/prepare_store_download"
            self.logger.info(f"Initiating RO-crate export for workflow invocation: {invocation_id}")
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


    def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete a workflow by its ID.

        :param workflow_id: ID of the workflow to delete
        :raises RuntimeError: if deletion fails
        """
        try:
            self._gi.workflows.delete_workflow(workflow_id)
            self.logger.info(f"Successfully deleted workflow with ID {workflow_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete workflow {workflow_id}: {str(e)}")
            raise