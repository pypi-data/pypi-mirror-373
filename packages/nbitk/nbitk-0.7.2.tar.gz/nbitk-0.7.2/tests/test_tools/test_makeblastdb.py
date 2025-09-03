import os
import pytest
import shutil
from pathlib import Path
from Bio import SeqIO
from nbitk.Tools.makeblastdb import Makeblastdb
from nbitk.config import Config
from nbitk.SeqIO.BCDM import BCDMIterator

# Construct relative path to the test data
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
BCDM_TSV_PATH = TEST_DATA_DIR / "BCDM.tsv"

# Construct the path to the config file
CONFIG_PATH = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'


def is_tool_available(name):
    """Check whether `name` is on PATH and executable."""
    return shutil.which(name) is not None

@pytest.fixture
def temp_fasta(tmp_path):
    """Fixture to create a temporary FASTA file from BCDM TSV."""
    temp_fasta_path = tmp_path / "temp.fasta"
    with open(BCDM_TSV_PATH, "r") as bcdm_file, open(temp_fasta_path, "w") as fasta_file:
        sequences = SeqIO.parse(bcdm_file, "bcdm-tsv")
        SeqIO.write(sequences, fasta_file, "fasta")
    return temp_fasta_path



@pytest.fixture
def config():
    """Fixture to create and load a Config object for each test."""
    cfg = Config()
    cfg.load_config(CONFIG_PATH)
    cfg.set('log_level', 'WARNING')
    return cfg


def test_bcdm_parser():
    """Test if BCDM TSV file can be parsed correctly."""
    with open(BCDM_TSV_PATH, "r") as bcdm_file:
        sequences = list(SeqIO.parse(bcdm_file, "bcdm-tsv"))

    assert len(sequences) > 0, "No sequences were parsed from the BCDM file"

    # Check if essential fields are present in the first sequence
    first_seq = sequences[0]
    assert first_seq.id, "Sequence ID is missing"
    assert first_seq.seq, "Sequence is empty"
    assert "taxonomy" in first_seq.annotations, "Taxonomy information is missing"
    assert "bcdm_fields" in first_seq.annotations, "BCDM fields are missing"


@pytest.mark.skipif(not is_tool_available("makeblastdb"),
                    reason="makeblastdb not available on PATH")
def test_makeblastdb(temp_fasta, config, tmp_path):
    """Test creating a BLAST database from the FASTA file."""
    output_path = tmp_path / "blastdb"

    makeblastdb_runner = Makeblastdb(config)
    makeblastdb_runner.set_in(str(temp_fasta))
    makeblastdb_runner.set_dbtype("nucl")
    makeblastdb_runner.set_out(str(output_path))
    makeblastdb_runner.set_parse_seqids()

    return_code = makeblastdb_runner.run()

    assert return_code == 0, "makeblastdb failed to run successfully"

    # Check if BLAST database files were created
    expected_files = [f"{output_path}.nhr", f"{output_path}.nin", f"{output_path}.nsq"]
    for file in expected_files:
        assert os.path.exists(file), f"Expected BLAST database file {file} not found"


@pytest.mark.skipif(not is_tool_available("makeblastdb"),
                    reason="makeblastdb not available on PATH")
def test_makeblastdb_validation(config):
    """Test parameter validation in Makeblastdb."""
    makeblastdb_runner = Makeblastdb(config)

    # Test missing required parameter
    with pytest.raises(ValueError, match="'dbtype' is a required parameter"):
        makeblastdb_runner.validate_parameters()

    # Test incompatible options
    makeblastdb_runner.set_dbtype("nucl")
    makeblastdb_runner.set_taxid("1")
    makeblastdb_runner.set_taxid_map("dummy_map")
    with pytest.raises(ValueError, match="'taxid' and 'taxid_map' are incompatible options"):
        makeblastdb_runner.validate_parameters()