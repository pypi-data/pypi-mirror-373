
from nbitk.Services.Galaxy.BaseToolClient import BaseToolClient
from nbitk.Services.Galaxy.BaseWorkflowClient import BaseWorkflowClient
import logging
from nbitk.config import Config
from typing import Optional, Dict, Any
import os


class MetabarcodingToolClient(BaseToolClient):
    """
    Client for running metabarcoding analyses through Galaxy.

    :param config: NBITK configuration object containing Galaxy connection settings
    :param logger: Optional logger instance. If None, creates one using the class name

    Examples:
        >>> from nbitk.config import Config
        >>> from nbitk.logger import get_formatted_logger
        >>>
        >>> # Initialize with config
        >>> config = Config()
        >>> config.load_config('config.yaml')
        >>>
        >>> # Create client
        >>> metabarcoding = MetabarcodingClient(config)
        >>> # Configure history: this is the work env for galaxy
        >>> metabarcoding.config_history(history_name='nbitk_Test_history', existing_history=True)
        >>> # Run analysis with defaults
        >>> results = metabarcoding.run_metabarcoding(params)
    """

    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, "eDentity Metabarcoding Pipeline", logger)
        self._preserve_history = True
        self.input_dataset: Optional[Dict[str, Any]] = None
        self.tool_params: Optional[Dict[str, Any]] = None
        # self.job_id = None
        self.results = None

    def config_history(self, history_name: Optional[str] = None, existing_history=False) -> None:
        """
        Configure the history for the client. If a history name is provided, retrieve its ID
        and update the client to use that history.

        :param history_name: The name of the history to configure
        :param existing_history: Flag indicating whether to use an existing history or create a new one
        """
        try:
            if history_name is not None and existing_history is True:
                
                # Retrieve all histories
                histories = self._gi.histories.get_histories()
                # Find the history with the given name
                matching_history = next((h for h in histories if h['name'] == history_name), None)
                if not matching_history:
                    raise ValueError(f"No history found with name: {history_name}")
                # Update the client with the history ID and name
                self._history = {
                    'id': matching_history['id'],
                    'name': matching_history['name']
                }
                self.logger.info(
                    f"Configured to use history '{self._history['name']}' "
                    f"with ID '{self._history['id']}'."
                )
            else:
                # Create a new history
                self._ensure_history(history_name)
                self.logger.info(
                    f"Created and configured new history '{self._history['name']}' "
                    f"with ID '{self._history['id']}'."
                )

        except Exception as e:
            self.logger.error(f"Failed to configure history: {e}")
            raise

    def config_tool_params(self, params: Dict[str, Any]) -> None:
        """
        Configure the parameters for the metabarcoding tool.

        This method sets up the tool parameters based on the provided dictionary of input parameters.
        It maps the input parameters to the corresponding tool-specific configuration keys.

        :param params: A dictionary containing the following keys:
            - 'project_name' (str): Name of the project.
            - 'data_type' (str): Type of the input data.
            - 'input_fastqs' (list): List of input FASTQ file paths.
            - 'n_max' (str): Maximum number of N bases allowed.
            - 'average_qual' (float): Minimum average quality score required.
            - 'length_required' (str): Minimum length of sequences required.
            - 'fastq_maxdiffpct' (float): Maximum percentage of differences allowed for merging.
            - 'fastq_maxdiffs' (str): Maximum number of differences allowed for merging.
            - 'fastq_minovlen' (str): Minimum overlap length required for merging.
            - 'forward_primer' (str): Sequence of the forward primer.
            - 'reverse_primer' (str): Sequence of the reverse primer.
            - 'discard_untrimmed' (bool): Whether to discard untrimmed sequences.
            - 'minlen' (str): Minimum length of sequences after filtering.
            - 'maxlen' (str): Maximum length of sequences after filtering.
            - 'maxee' (float): Maximum expected errors allowed.
            - 'fasta_width' (str): Width of the FASTA output sequences.
            - 'alpha' (float): Alpha parameter for denoising.
            - 'minsize' (str): Minimum size of clusters for denoising.

        :raises KeyError: If any required key is missing from the `params` dictionary.
        """

        # config dataset
        if not self.input_dataset:
            self.config_input_dataset(self._history['id'], params['input_fastqs'])

        # config rest of the parameters
        self.tool_params = {
            'dataType|project_name': params['project_name'],
            'dataType|data_type': params['data_type'],
            'dataType|input_fastqs': self.input_dataset,
            'fastp|n_max': params['n_max'],
            'fastp|average_qual': params['average_qual'],
            'fastp|length_required': params['length_required'],
            'merge|fastq_maxdiffpct': params['fastq_maxdiffpct'],
            'merge|fastq_maxdiffs': params['fastq_maxdiffs'],
            'merge|fastq_minovlen': params['fastq_minovlen'],
            'trimming|forward_primer': params['forward_primer'],
            'trimming|reverse_primer': params['reverse_primer'],
            'trimming|anchored': params['anchored'],
            'trimming|discard_untrimmed': params['discard_untrimmed'],
            'Filter|minlen': params['minlen'],
            'Filter|maxlen': params['maxlen'],
            'Filter|maxee': params['maxee'],
            'Dereplication|fasta_width': params['fasta_width'],
            'Denoise|alpha': params['alpha'],
            'Denoise|minsize': params['minsize'],
            "extended_json_reports|create_extended_json_reports": params['create_extended_json_reports'],
                }
        self.logger.debug(f"Configured tool parameters: {self.tool_params}")

    def config_input_dataset(self, history_id: str, dataset_name: str) -> str:
        """
        Configure the dataset for the metabarcoding tool by retrieving its ID.

        :param history_id: ID of the history containing the dataset
        :param dataset_name: Name of the dataset
        :return: updates self.input_dataset
        """
        try:
            # Retrieve datasets from the specified history
            datasets = self._gi.histories.show_history(history_id, contents=True)

            matching_dataset = next((d for d in datasets if d['name'] == dataset_name), None)

            if matching_dataset:
                self.logger.info(
                    f"Found dataset '{dataset_name}' with ID '{matching_dataset['id']}' "
                    f"in history ID '{history_id}'."
                )
                self.input_dataset = {'values': [{'id': matching_dataset['id'], 'src': 'hda'}]}
            else:
                raise ValueError(
                    f"No dataset found with name: {dataset_name} in history ID: {history_id}")

        except Exception as e:
            self.logger.error(f"Failed to configure dataset: {e}")
            raise

    def download_results(self, job_id: str, output_names: list[str], output_path: str):
        """
        Download the results of the metabarcoding analysis for a given job ID.

        :param job_id: ID of the job containing the results
        :param output_names: List of output names to download
        :param: output_path: Path to save the downloaded results
        """
        self.logger.info(f"Downloading results for job ID: {job_id}...")
        try:
            # Retrieve job details
            job_details = self._gi.jobs.show_job(job_id, full_details=True)

            valid_outputs = [
                "ESV_table",
                "multiqc_report",
                "ESV_sequences",
                "json_reports",
                "summary_report"]
            os.makedirs(output_path, exist_ok=True)
            for name in output_names:
                if name not in valid_outputs:
                    raise ValueError(
                        f"Invalid output name: {name}. Valid options are: {valid_outputs}")
                # Download the outputs
                self._gi.datasets.download_dataset(
                    job_details['outputs'][name]['id'],
                    output_path)

        except Exception as e:
            self.logger.error(f"Failed to download results for job ID {job_id}: {e}")
            raise

    def run_metabarcoding(self, params: Dict[str, Any]) -> None:
        """
        Run the metabarcoding analysis with the specified parameters.

        This method ensures that the history is configured, tool parameters are set,
        and the job is submitted to Galaxy for processing. It waits for the job to complete
        and stores the results.

        :param params: Dictionary containing the parameters for the analysis
        :return: None
        """

        # Run the metabarcoding analysis
        self.logger.info("Starting metabarcoding analysis...")

        # Ensure history has been configured
        if not self._history:
            self.logger.info("No history found, creating a new one.")
            self.config_history()

        # Configure tool parameters
        self.config_tool_params(params)

        # submit the job to Galaxy
        self.run_tool(
            params=self.tool_params,
        )
        self.job_id = self.results['jobs'][0]['id']
        self.logger.info(f"Job submitted with ID: {self.job_id}....waiting for completion")
        self._wait_for_job(self.job_id)

# abstract class
class MetabarcodingWorkflowClient(BaseWorkflowClient):
    """
    Abstract class for running metabarcoding workflows in Galaxy.
    This class is not intended to be instantiated directly.
    """
    def __init__(self, config: Config, workflow_name, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, workflow_name, logger)
        self._preserve_history = True
        self.input_dataset: Optional[Dict[str, Any]] = None
        self.tool_params: Optional[Dict[str, Any]] = None
        

        

    def run_metabarcoding_workflow(self, params: Dict[str, Any]) -> None:
        """
        Run the metabarcoding workflow with the specified parameters.

        :param params: Dictionary containing the parameters for the workflow
        :param input_data: Dictionary containing the input data for the workflow
        """
        self.logger.info("Starting metabarcoding workflow analysis...")

        # Ensure history has been configured
        if not self._history:
            self.logger.info("No history found, creating a new one.")
            self.config_history()

        # Configure tool parameters
        self.config_tool_params(params)
        
        # submit the job to Galaxy
        self.workflowInvocation = self.invoke_workflow(
            input_data=self.input_dataset,
            params=self.tool_params
        )
    

    def config_history(self, history_name: Optional[str] = None, existing_history=False) -> None:
        """
        Configure the history for the client. If a history name is provided, retrieve its ID
        and update the client to use that history.

        :param history_name: The name of the history to configure
        :param existing_history: Flag indicating whether to use an existing history or create a new one
        """
        try:
            if history_name is not None and existing_history is True:
                # Retrieve all histories
                histories = self._gi.histories.get_histories()
                # Find the history with the given name
                matching_history = next((h for h in histories if h['name'] == history_name), None)
                if not matching_history:
                    raise ValueError(f"No history found with name: {history_name}")
                # Update the client with the history ID and name
                self._history = {
                    'id': matching_history['id'],
                    'name': matching_history['name']
                }
                self.logger.info(
                    f"Configured to use history '{self._history['name']}' "
                    f"with ID '{self._history['id']}'."
                )
            else:
                # Create a new history
                self._ensure_history()
                self.logger.info(
                    f"Created and configured new history '{self._history['name']}' "
                    f"with ID '{self._history['id']}'."
                )

        except Exception as e:
            self.logger.error(f"Failed to configure history: {e}")
            raise

    def config_tool_params(self, params: Dict[str, Any]) -> None:
        """
        Configure the parameters for the metabarcoding tool.

        This method sets up the tool parameters based on the provided dictionary of input parameters.
        It maps the input parameters to the corresponding tool-specific configuration keys.

        :param params: A dictionary containing the following keys:
            - 'project_name' (str): Name of the project.
            - 'data_type' (str): Type of the input data.
            - 'input_fastqs' (list): List of input FASTQ file paths.
            - 'n_max' (str): Maximum number of N bases allowed.
            - 'average_qual' (float): Minimum average quality score required.
            - 'length_required' (str): Minimum length of sequences required.
            - 'fastq_maxdiffpct' (float): Maximum percentage of differences allowed for merging.
            - 'fastq_maxdiffs' (str): Maximum number of differences allowed for merging.
            - 'fastq_minovlen' (str): Minimum overlap length required for merging.
            - 'forward_primer' (str): Sequence of the forward primer.
            - 'reverse_primer' (str): Sequence of the reverse primer.
            - 'discard_untrimmed' (bool): Whether to discard untrimmed sequences.
            - 'minlen' (str): Minimum length of sequences after filtering.
            - 'maxlen' (str): Maximum length of sequences after filtering.
            - 'maxee' (float): Maximum expected errors allowed.
            - 'fasta_width' (str): Width of the FASTA output sequences.
            - 'alpha' (float): Alpha parameter for denoising.
            - 'minsize' (str): Minimum size of clusters for denoising.

        :raises KeyError: If any required key is missing from the `params` dictionary.
        """

        # config dataset
        if not self.input_dataset:
            self.config_input_dataset(self._history['id'], params['input_fastqs'])

        # config rest of the parameters
        self.tool_params = {"0" : {
            'dataType|project_name': params['project_name'],
            'dataType|data_type': params['data_type'],
            'dataType|input_fastqs': self.input_dataset,
            'fastp|n_max': params['n_max'],
            'fastp|average_qual': params['average_qual'],
            'fastp|length_required': params['length_required'],
            'merge|fastq_maxdiffpct': params['fastq_maxdiffpct'],
            'merge|fastq_maxdiffs': params['fastq_maxdiffs'],
            'merge|fastq_minovlen': params['fastq_minovlen'],
            'trimming|forward_primer': params['forward_primer'],
            'trimming|reverse_primer': params['reverse_primer'],
            'trimming|discard_untrimmed': params['discard_untrimmed'],
            'Filter|minlen': params['minlen'],
            'Filter|maxlen': params['maxlen'],
            'Filter|maxee': params['maxee'],
            'Dereplication|fasta_width': params['fasta_width'],
            'Denoise|alpha': params['alpha'],
            'Denoise|minsize': params['minsize'],
            "extended_json_reports|create_extended_json_reports": params['create_extended_json_reports'],
                }}
        self.logger.debug(f"Configured tool parameters: {self.tool_params}")

    def config_input_dataset(self, history_id: str, dataset_name: str) -> str:
        """
        Configure the dataset for the metabarcoding tool by retrieving its ID.

        :param history_id: ID of the history containing the dataset
        :param dataset_name: Name of the dataset
        :return: updates self.input_dataset
        """
        try:
            # Retrieve datasets from the specified history
            datasets = self._gi.histories.show_history(history_id, contents=True)

            matching_dataset = next((d for d in datasets if d['name'] == dataset_name), None)

            if matching_dataset:
                self.logger.info(
                    f"Found dataset '{dataset_name}' with ID '{matching_dataset['id']}' "
                    f"in history ID '{history_id}'."
                )
                self.input_dataset = {"0": {'id': matching_dataset['id'], 'src': 'hda'}} # make it dynamic
                
            else:
                raise ValueError(
                    f"No dataset found with name: {dataset_name} in history ID: {history_id}")

        except Exception as e:
            self.logger.error(f"Failed to configure dataset: {e}")
            raise

        
            
        
        