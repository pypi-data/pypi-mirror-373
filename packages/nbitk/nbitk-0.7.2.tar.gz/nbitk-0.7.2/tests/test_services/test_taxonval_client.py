import pytest
import os
from nbitk.config import Config
from nbitk.Services.Galaxy.TaxonValidator import TaxonValidator


@pytest.fixture(scope="session")
def config():
    """Create a basic config for tests"""
    config = Config()
    config.config_data = {}
    config.initialized = True
    return config


@pytest.fixture(autouse=True)
def check_galaxy_key():
    """Verify Galaxy API key is available"""

    if not os.environ.get('GALAXY_API_KEY'):
        pytest.skip("GALAXY_API_KEY not set in environment")

@pytest.fixture
def test_data():
    """Create BCDM data for testing"""
    return [
        {
            'local_id': '1',
            'identification': 'Apidae',
            'nuc': 'AATATTATACTTTATTTTTGCTATATGATCAGGAATAATTGGTTCATCTATAAGATTATTAATTCGAATAGAATTAAGACATCCAGGTATATGAATTAATAATGATCAAATTTATAATTCTTTAGTAACAAGACATGCATTTTTAATAATTTTTTTTATAGTTATACCTTTTATAATTGGTGGATTTGGAAATTATCTAATTCCATTAATATTAGGATCCCCAGATATAGCTTTTCCTCGAATAAATAATATTAGATTTTGACTTCTACCTCCATCATTATTCATATTATTATTAAGAAATATATTTACACCTAATGTAGGTACAGGATGAACTGTATATCCTCCTTTATCTTCTTATTTATTTCATTCATCACCTTCAATTGATATTGCAATCTTTTCTTTACATATATCAGGAATCTCTTCAATTATTGGATCATTAAATTTTATCGTTACTATTTTATTAATAAAAAATTTTTCATTAAATTATGATCAAATTAATTTATTTTCATGATCAGTATGTATTACAGTAATTTTATTAATTCTATCTTTACCAGTATTAGCCGGCGCAATTACTATATTATTATTTGATCGAAATTTTAATACTTCATTTTTTGACCCAATAGGAGGAGGAGATCCAATCCTTTATCAACATTTATTT'
        },
        {
            'local_id': '2',
            'identification': 'Apidae',
            'nuc': 'ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG'
        }
    ]

@pytest.fixture
def client(config):
    """Create a fresh client for each test"""
    client = TaxonValidator(config)
    yield client
    del client


def test_basic_validation(client, test_data):
    """Test basic taxon validation search with default parameters"""
    result = client.validate_records(test_data, params = {'databases': ['Genbank CO1 (2023-11-15)'], 'max_target_seqs': 100, 'identity': 80})
    query_config = client.query_config

    assert len(result) == 2
    assert result[0]['is_valid']
    assert result[1]['is_valid'] == False
    assert query_config is not None