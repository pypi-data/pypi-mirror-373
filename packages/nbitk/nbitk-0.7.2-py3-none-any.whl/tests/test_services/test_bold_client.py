from pathlib import Path
import pytest
from Bio import SeqIO
from nbitk.config import Config
from nbitk.Services.BOLD.IDService import IDService

@pytest.fixture(scope="session")
def config():
    """Create a basic config for tests"""
    config = Config()
    config.config_data = {
        'bold_database': 1,
        'bold_operating_mode': 1,
        'bold_timeout': 300,
        'log_level': 'WARNING'
    }
    config.initialized = True
    return config


@pytest.fixture(scope="session")
def input_fasta():
    """Test uploading a dataset to Galaxy"""
    test_file = Path(__file__).parent / "bold_test_file.fasta"
    return test_file

@pytest.mark.skip("Skipping test for BOLD TaxonValidator due to external problems")
def test_bold_client(config, input_fasta):
    """Test the BOLD client with a sample FASTA file."""
    client = IDService(config)
    with open(input_fasta, 'r') as handle:
        records = list(SeqIO.parse(handle, 'fasta'))
        results = client.identify_seqrecords(records)
        assert results is not None
        assert len(results) == len(records)


