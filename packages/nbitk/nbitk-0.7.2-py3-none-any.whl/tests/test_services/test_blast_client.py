import pytest
import os
import tempfile
from pathlib import Path
from nbitk.config import Config
from nbitk.Services.Galaxy.BLASTN import BLASTNClient, BlastTask, OutputFormat, TaxonomyMethod

@pytest.fixture(scope="session")
def config():
    """Create a basic config for tests"""
    config = Config()
    config.config_data = { 'galaxy_domain': 'galaxy.naturalis.nl' }
    config.initialized = True
    return config

@pytest.fixture(scope="session")
def test_files():
    """Create temporary FASTA files with test sequences"""
    # Valid ITS sequence (Bombus terrestris)
    bombus_seq = """>Symbiotaphrina_buchneri_DQ248313
ACGATTTTGACCCTTCGGGGTCGATCTCCAACCCTTTGTCTACCTTCCTTGTTGCTTTGGCGGGCCGATGTTCGTTCTCGCGAACGACACCGCTGGCCTGACGGCTGGTGCGCGCCCGCC
AGAGTCCACCAAAACTCTGATTCAAACCTACAGTCTGAGTATATATTATATTAAAACTTTCAACAACGGATCTCTTGGTTCTGGCATCGATGAAGAACGCAGCGAAATGCGATAAGTAAT
GTGAATTGCAGAATTCAGTGAATCATCGAATCTTTGAACGCACATTGCGCCCCTTGGTATTCCGAGGGGCATGCCTGTTCGAGCGTCATTTCACCACTCAAGCTCAGCTTGGTATTGGGT
CATCGTCTGGTCACACAGGCGTGCCTGAAAATCAGTGGCGGTGCCCATCCGGCTTCAAGCATAGTAATTTCTATCTTGCTTTGGAAGTCTCCGGAGGGTTACACCGGCCAACAACCCCAA
TTTTCTATG
"""

    # Invalid sequence (random nucleotides)
    random_seq = """>Random_sequence
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"""

    # Create temp directory and files
    temp_dir = tempfile.mkdtemp()
    files = {}

    # Write valid sequence
    valid_path = Path(temp_dir) / "DQ248313.fa"
    with open(valid_path, 'w') as f:
        f.write(bombus_seq)
    files['valid'] = str(valid_path)

    # Write invalid sequence
    invalid_path = Path(temp_dir) / "random.fa"
    with open(invalid_path, 'w') as f:
        f.write(random_seq)
    files['invalid'] = str(invalid_path)

    yield files

    # Cleanup after all tests
    for filepath in files.values():
        try:
            os.remove(filepath)
        except OSError:
            pass
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

@pytest.fixture(autouse=True)
def check_galaxy_key():
    """Verify Galaxy API key is available"""
    if not os.environ.get('GALAXY_API_KEY'):
        pytest.skip("GALAXY_API_KEY not set in environment")

@pytest.fixture
def client(config):
    """Create a fresh client for each test"""
    client = BLASTNClient(config)
    yield client
    del client

def test_basic_its_search(client, test_files):
    """Test basic ITS search with default parameters"""
    result = client.run_blast(test_files['valid'], databases=['UNITE'])

    assert 'blast_output_fasta' in result
    output_file = result['blast_output_fasta']
    assert os.path.exists(output_file)

    # Verify the content is tabular
    with open(output_file) as f:
        first_line = f.readline().strip()
        assert '\t' in first_line

def test_custom_parameters(client, test_files):
    """Test CO1 search with custom parameters"""
    result = client.run_blast(
        test_files['valid'],
        databases=['UNITE'],
        task=BlastTask.BLASTN,
        max_target_seqs=5,
        identity=95.0,
        coverage=75.0,
        output_format=OutputFormat.TABULAR
    )

    assert 'blast_output_fasta' in result
    assert os.path.exists(result['blast_output_fasta'])

def test_invalid_sequence(client, test_files):
    """Test behavior with invalid/random sequence"""
    result = client.run_blast(
        test_files['invalid'],
        databases=['UNITE'],
        output_format=OutputFormat.TABULAR
    )

    assert 'blast_output_fasta' in result
    assert os.path.exists(result['blast_output_fasta'])

def test_output_formats(client, test_files):
    """Test different output formats"""
    result = client.run_blast(
        test_files['valid'],
        databases=['UNITE'],
        output_format=OutputFormat.TABULAR
    )
    assert 'blast_output_fasta' in result
    assert os.path.exists(result['blast_output_fasta'])


def test_taxonomy_methods(client, test_files):
    """Test different taxonomy methods"""
    result = client.run_blast(
        test_files['valid'],
        databases=['UNITE'],
        output_format=OutputFormat.CUSTOM_TAXONOMY,
        taxonomy_method=TaxonomyMethod.DEFAULT
    )
    assert 'blast_output_fasta' in result
    assert os.path.exists(result['blast_output_fasta'])


@pytest.mark.xfail(reason="write_store endpoint not available or path incorrect")
def test_export_rocrate(client, test_files):
    """Test exporting results as RO-crate"""
    # Run a basic analysis
    client.run_blast(
        test_files['valid'],
        databases=['/data/blast_databases/CO1/CO1.fa']
    )

    # Export as RO-crate
    with tempfile.NamedTemporaryFile(suffix='.rocrate.zip') as tmp:
        crate_path = client.export_history_as_rocrate(tmp.name)
        assert os.path.exists(crate_path)
        assert os.path.getsize(crate_path) > 0

if __name__ == "__main__":
    pytest.main()