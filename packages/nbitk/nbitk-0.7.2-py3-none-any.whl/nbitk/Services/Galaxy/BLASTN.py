from typing import Optional, List, Dict, Any, Union
from enum import Enum
import logging

from nbitk.Services.Galaxy.BaseToolClient import BaseToolClient
from nbitk.config import Config
import os


class TaxonomyMethod(str, Enum):
    """
    Enumeration of supported taxonomy methods.
    """
    NONE = "none"
    DEFAULT = "default"
    GBIF = "GBIF"


class BlastTask(str, Enum):
    """
    Enumeration of supported BLAST tasks.
    """
    BLASTN = "blastn"
    MEGABLAST = "megablast"


class OutputFormat(str, Enum):
    """
    Enumeration of supported output formats.
    """
    CUSTOM_TAXONOMY = "custom_taxonomy"
    PAIRWISE = "0"
    TABULAR = "6"
    TEXT_ASN1 = "8"
    BLAST_ARCHIVE = "11"


class BLASTNClient(BaseToolClient):
    """
    Client for running BLASTN analyses through Galaxy.

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
        >>> blast = BLASTNClient(config)
        >>>
        >>> # Run analysis with defaults (CO1 database, megablast)
        >>> results = blast.run_blast('sequences.fasta')
        >>>
        >>> # Export the history as RO-crate
        >>> blast.export_history_as_rocrate('my_analysis.rocrate.zip')
        >>>
        >>> # Run against custom database with specific parameters
        >>> custom_results = blast.run_blast(
        ...     'sequences.fasta',
        ...     user_database='mydb.fasta',
        ...     task=BlastTask.BLASTN,
        ...     identity=95.0
        ... )
    """

    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the BLASTNClient object. This constructor does nothing more than specify the tool name,
        according to which the Galaxy tool is retrieved. The actual initialization of the Galaxy connection
        and tool is done in the BaseClient constructor. Consult the BaseClient documentation for more information.
        :param config: NBITK configuration object containing Galaxy connection settings
        :param logger: An optional logger instance. If None, a new logger is created using the class name
        """
        super().__init__(config, 'Identify reads with blastn and find taxonomy', logger)

    def run_blast(self,
                  input_file: str,
                  databases: List[str] = ["BOLD species only no duplicates"],
                  task: BlastTask = BlastTask.BLASTN,
                  max_target_seqs: int = 5,
                  output_format: OutputFormat = OutputFormat.CUSTOM_TAXONOMY,
                  taxonomy_method: TaxonomyMethod = TaxonomyMethod.DEFAULT,
                  coverage: float = 80.0,
                  identity: float = 97.0,
                  user_database: Optional[str] = None,
                  no_file_write: bool = False
                  ) -> Dict[str, str]:
        """
        Run BLASTN analysis with the given parameters.

        :param input_file: Path to input FASTA file
        :param databases: List of database paths to search against (ignored if user_database is provided)
        :param task: BLAST task type (blastn or megablast)
        :param max_target_seqs: Maximum number of BLAST hits per sequence
        :param output_format: Desired output format
        :param taxonomy_method: Method for taxonomy assignment
        :param coverage: Query coverage percentage cutoff
        :param identity: Identity percentage cutoff
        :param user_database: Optional path to user-provided FASTA database
        :param no_file_write: If True, do not write output files to disk (for testing)
        :return: Dictionary containing paths to output files
        :raises RuntimeError: if job fails or input parameters are invalid

        Examples:
            >>> # Basic usage with defaults
            >>> results = client.run_blast('sequences.fasta')
            >>> print(results['blast_output_fasta'])
            'blast_output_123.tsv'
            >>>
            >>> # Custom search against user database
            >>> results = client.run_blast(
            ...     input_file='query.fasta',
            ...     user_database='custom_db.fasta',
            ...     task=BlastTask.BLASTN,
            ...     max_target_seqs=5,
            ...     identity=95.0
            ... )
            >>>
            >>> # Search against multiple databases with custom taxonomy settings
            >>> results = client.run_blast(
            ...     input_file='query.fasta',
            ...     databases=[
            ...         'genbankco1',
            ...         'genbank16S'
            ...     ],
            ...     taxonomy_method=TaxonomyMethod.DEFAULT,
            ...     coverage=85.0,
            ...     output_format=OutputFormat.CUSTOM_TAXONOMY
            ... )
        """
        history = self._ensure_history()

        # Upload input file
        self.logger.info(f"Uploading input file: {input_file}")
        file_upload_details = self._upload_file(
            file_path=input_file,
            file_type='fasta' # TODO: this should be auto-detected
            )
        input_file_name = os.path.basename(input_file)
        assert file_upload_details['outputs'][0]['name'] == input_file_name, \
            f"Uploaded file name {file_upload_details['outputs'][0]['name']} does not match input file name {input_file_name}"
        input_id = file_upload_details['outputs'][0]['id']

        # Upload user database if provided
        # TODO: this is now ignored
        database_id = None
        if user_database:
            self.logger.info(f"Uploading user database: {user_database}")
            database_upload_details = self._upload_file(user_database, 'fasta')
            # assert user database has been uploaded
            assert database_upload_details['outputs'][0]['name'] == os.path.basename(user_database), \
                f"Uploaded database name {database_upload_details['outputs'][0]['name']} does not match user database name {os.path.basename(user_database)}"
            database_id = database_upload_details['outputs'][0]['id']
        
        # Prepare tool parameters
        params = {
            'input_type|type': 'fasta',
            'input_type|input': {'values': [{'id': input_id, 'src': 'hda'}]},
            'database_type|type': 'local',
            'database_type|database': databases,
            'task': task.value,
            'output_format|output_format_type': output_format.value,
            'output_format|taxonomy_method': taxonomy_method.value,
            'output_format|coverage': str(coverage),
            'identity': str(identity),
            'max_target_seqs': str(max_target_seqs)
        }

        # Add taxonomy parameters if needed
#        if output_format == OutputFormat.CUSTOM_TAXONOMY:
#            params['output_format'].update({
#                'taxonomy_method': taxonomy_method.value,
#                'coverage': coverage
#            })

        # Run BLAST
        self.logger.info("Starting BLASTN analysis...")
        try:
            result = self._gi.tools.run_tool(history['id'], self._tool['id'], params)
            job_id = result['jobs'][0]['id']
            self._wait_for_job(job_id)

            # Collect outputs
            outputs = {}
            for output in result['outputs']:
                if output['output_name'] == 'log_output':

                    # Accommodate cases where client cannot write to temp files
                    if no_file_write:
                        outputs['log_output'] = self._download_result_content(output)
                    else:
                        outputs['log_output'] = self._download_result(output, 'log')
                elif output['output_name'] == 'blast_output_fasta':

                    if no_file_write:
                        outputs['blast_output_fasta'] = self._download_result_content(output)
                    else:
                        outputs['blast_output_fasta'] = self._download_result(output, 'tsv')

            return outputs

        except Exception as e:
            self.logger.error(f"BLASTN analysis failed: {str(e)}")
            raise
