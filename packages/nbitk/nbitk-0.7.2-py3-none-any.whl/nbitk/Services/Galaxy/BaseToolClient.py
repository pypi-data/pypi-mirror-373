from nbitk.Services.Galaxy.BaseClient import BaseClient
from nbitk.config import Config
from typing import Optional, Dict, Any
import os
import logging
from nbitk.logger import get_formatted_logger
from bioblend import galaxy


class BaseToolClient(BaseClient):
    """
    Base class for Galaxy tool clients that handles common operations and cleanup.
    Provides standardized interfaces for Galaxy instance management, history handling,
    file uploads and downloads, and job monitoring. Subclasses should implement
    tool-specific methods for running analyses and processing results.
    """

    def __init__(self, config: Config, tool_name: str = None, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, tool_name, logger)
        self.job_id = None
        self.results = None
        self.tool_name = tool_name
        self.tool_id = None
        self._tool = self._get_tool(tool_name)

    def run_tool(self, params: Dict[str, Any]) -> None:
        """
        Run the tool with the given parameters. This method should be implemented by subclasses.
        :param params: Dictionary of parameters for the tool
        """
        
        try:
            self.logger.debug(f"Running tool {self.tool_name} with parameters: {params}")
            self.results = self._gi.tools.run_tool(
                history_id=self._history['id'],
                tool_id=self._tool['id'],
                tool_inputs=params)
            self.logger.debug(f"Tool {self.tool_name} submitted with job ID: {self.job_id}")
        except Exception as e:
            self.logger.error(f"Error running tool {self.tool_name}: {e}")
            raise
    
    def _get_tool(self, name: str) -> Dict[str, Any]:
        """
        Get tool by name from Galaxy. The name is provided in bold at the top of the tool form.
        For example: `Identify reads with blastn and find taxonomy`

        :param name: Name of the tool to retrieve
        :return: Tool dictionary containing at least 'id' key
        :raises RuntimeError: if tool is not found
        """
        tools = self._gi.tools.get_tools(name=name)
        if not tools:
            raise RuntimeError(f"Tool '{name}' not found")
        return tools[0]
    
    def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        """
        Get details of a specific tool by its ID.

        :param tool_id: ID of the tool to retrieve
        :return: Tool details as a dictionary
        """
        try:
            tool_details = self._gi.tools.show_tool(
                tool_id=tool_id,
                io_details=True)
            return tool_details
        except Exception as e:
            self.logger.error(f"Error retrieving tool details for {tool_id}: {e}")
            raise
    
    def _wait_for_job(self, job_id: str) -> None:
        """
        Poll Galaxy server until specified job completes. This is a blocking operation
        that will not return until the job either completes successfully or fails.

        :param job_id: Galaxy job identifier to monitor
        :raises Exception: if job fails or polling encounters an error
        """
        jc = galaxy.jobs.JobsClient(galaxy_instance=self._gi)
        try:
            jc.wait_for_job(job_id=job_id)
            self.logger.debug(f"Job {job_id} completed")
        except Exception as e:
            self.logger.error(f"Job {job_id} failed: {str(e)}")
            raise
