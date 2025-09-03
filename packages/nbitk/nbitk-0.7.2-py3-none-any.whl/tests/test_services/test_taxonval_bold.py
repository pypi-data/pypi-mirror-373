import pytest
from nbitk.config import Config
from nbitk.Services.BOLD.TaxonValidator import TaxonValidator


@pytest.fixture(scope="session")
def config():
    """Create a basic config for tests"""
    config = Config()
    config.config_data = { 'log_level': 'DEBUG' }
    config.initialized = True
    return config

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

@pytest.mark.skip("Skipping test for BOLD TaxonValidator due to external problems")
def test_basic_validation(client, test_data):
    """Test basic taxon validation search with default parameters"""
    result = client.validate_records(test_data)
    bold_config = client.query_config

    assert len(result) == 2
    assert result[0]['is_valid'] == True
    assert result[1]['is_valid'] == False
    assert bold_config is not None