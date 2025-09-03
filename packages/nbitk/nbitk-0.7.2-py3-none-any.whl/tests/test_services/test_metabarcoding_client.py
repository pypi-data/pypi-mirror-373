import pytest 
from nbitk.Services.Galaxy.metabarcoding import MetabarcodingToolClient
from nbitk.config import Config
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def config():
    """Create a basic config for tests"""
    config = Config()
    config.config_data = { 'galaxy_domain': 'galaxy.naturalis.nl' }
    config.initialized = True
    return config

@pytest.fixture(scope="session")
def metabarcoding_client(config):
    """Initialize the MetabarcodingToolClient"""
    client = MetabarcodingToolClient(config)
    client.config_history()
    return client

@pytest.fixture(scope="session")
def input_params():
    """Input parameters for the metabarcoding tool"""
    return  {
        'project_name': 'test_metabarcoding_nbitk_ci',
        'data_type': 'Illumina',
        'input_fastqs': 'test_metabarcoding_client.zip',
        'n_max': '0',
        'average_qual': '25',
        'length_required': '100',
        'fastq_maxdiffpct': '100',
        'fastq_maxdiffs': '5',
        'fastq_minovlen': '10',
        'forward_primer': 'AAACTCGTGCCAGCCACC',
        'reverse_primer': 'GGACTACNVGGGTWTCTAAT',
        'discard_untrimmed': "True",
        'anchored': "True",
        'minlen': 150,
        'maxlen': 700,
        'maxee': 1,
        'fasta_width': 0,
        'alpha': 2,
        'minsize': 4,
        'create_extended_json_reports': "True"
        }

@pytest.fixture(scope="session")
def upload_test_dataset(metabarcoding_client):
    """Test uploading a dataset to Galaxy"""


    test_data_path = (Path(__file__).parent.parent / "data" / "test_metabarcoding_client.zip").resolve()


    # Mock the upload function
    upload_details = metabarcoding_client._upload_file(
        file_path=test_data_path, file_type="zip")
    return upload_details

@pytest.fixture(scope="session")
def get_uploaded_data_details(upload_test_dataset, metabarcoding_client):
    """Test uploading a dataset to Galaxy"""
    # upload
    upload_details = upload_test_dataset

    datasets = metabarcoding_client._gi.histories.show_history(metabarcoding_client._history['id'], contents=True)
    assert any(dataset['name'] == 'test_metabarcoding_client.zip' for dataset in datasets), "test dataset not found in history"
    for dataset in datasets:
        if dataset['name'] == 'test_metabarcoding_client.zip':
            return {'values': [{'id': dataset['id'], 'src': 'hda'}]}

def test_metabarcoding_client_initialization(metabarcoding_client):
    """Test initialization of MetabarcodingToolClient"""

    assert metabarcoding_client._history['id'] is not None
    assert metabarcoding_client.tool_name == "eDentity Metabarcoding Pipeline"



# test config tool params
def test_config_tool_params(metabarcoding_client, input_params, get_uploaded_data_details):
    """Test configuration of tool parameters"""


    expected_params= {
        'dataType|project_name': input_params['project_name'],
        'dataType|data_type': input_params['data_type'],
        'dataType|input_fastqs': get_uploaded_data_details,
        'fastp|n_max': input_params['n_max'],
        'fastp|average_qual': input_params['average_qual'],
        'fastp|length_required': input_params['length_required'],
        'merge|fastq_maxdiffpct': input_params['fastq_maxdiffpct'],
        'merge|fastq_maxdiffs': input_params['fastq_maxdiffs'],
        'merge|fastq_minovlen': input_params['fastq_minovlen'],
        'trimming|forward_primer': input_params['forward_primer'],
        'trimming|reverse_primer': input_params['reverse_primer'],
        'trimming|anchored': input_params['anchored'],
        'trimming|discard_untrimmed': input_params['discard_untrimmed'],
        'Filter|minlen': input_params['minlen'],
        'Filter|maxlen': input_params['maxlen'],
        'Filter|maxee': input_params['maxee'],
        'Dereplication|fasta_width': input_params['fasta_width'],
        'Denoise|alpha': input_params['alpha'],
        'Denoise|minsize': input_params['minsize'],
        "extended_json_reports|create_extended_json_reports": input_params['create_extended_json_reports']
    }

     # Set the tool parameters
    metabarcoding_client.config_tool_params(input_params)

    # Check if the parameters are set correctly
    assert metabarcoding_client.tool_params == expected_params



# test run metabarcoding
def test_run_metabarcoding(metabarcoding_client, input_params):
    """Test running the metabarcoding tool"""

    # Set the tool parameters
    metabarcoding_client.run_metabarcoding(input_params)


# test export history as rocrate
def test_export_history_as_rocrate(metabarcoding_client, get_uploaded_data_details):
    """Test exporting the history as a rocrate"""
    # delete input dataset to make export faster
    metabarcoding_client._gi.histories.update_dataset(
        history_id=metabarcoding_client._history['id'],
        dataset_id=get_uploaded_data_details['values'][0]['id'],
        deleted=True
    )
    # Set the target path for the rocrate
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        target_path = temp_file.name

        # Export the history as a rocrate
        metabarcoding_client.export_history_as_rocrate(target_path=target_path, max_wait=50)

        # Check if the file was created
        assert os.path.exists(target_path), "RoCrate file was not created"

def test_download_results(metabarcoding_client):
    """Test downloading the results of the metabarcoding analysis"""

    # Set the job ID to download results from
    job_id = metabarcoding_client.job_id

    # Define the output path and names
    output_path = tempfile.mkdtemp(prefix="metabarcoding_results_")
    output_names = [
        'ESV_table',
        'multiqc_report',
        'ESV_sequences',
        'json_reports',
        'summary_report'
    ]

    # Download the results
    metabarcoding_client.download_results(
        job_id=job_id,
        output_path=output_path,
        output_names=output_names
    )

    downloded_files = os.listdir(output_path)
    # Check if the files were downloaded
    for name in output_names:
        if name == 'multiqc_report':
            # Special case: look for '_Quality_control_report.html.zip'
            assert any(
                '_Quality_control_report.html.zip' in downloaded_file
                for downloaded_file in downloded_files
            ), "Quality control report was not downloaded"
        else:
            assert any(
                name in downloaded_file
                for downloaded_file in downloded_files
            ), (
                f"File containing '{name}' was not downloaded"
            )

if __name__ == "__main__":
    pytest.main()