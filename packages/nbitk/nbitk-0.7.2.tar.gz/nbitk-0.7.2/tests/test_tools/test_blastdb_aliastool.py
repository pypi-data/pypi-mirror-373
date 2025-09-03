import os
import pytest
import shutil
from pathlib import Path
from Bio import SeqIO
from nbitk.Tools.makeblastdb import Makeblastdb
from nbitk.Tools.blastdb_aliastool import BlastdbAliastool
from nbitk.config import Config
from nbitk.SeqIO.BCDM import BCDMIterator


# Construct relative path to the test data
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
BCDM_TSV_PATH = TEST_DATA_DIR / "BCDM.tsv"

# Construct the path to the config file
CONFIG_PATH = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'

# Construct the path to the seqidlist file
SEQIDLIST = TEST_DATA_DIR / "seqidlist.txt"

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


@pytest.fixture
def blast_db(temp_fasta, config, tmp_path):
    """Fixture to create a BLAST database."""
    output_path = tmp_path / "blastdb"

    makeblastdb_runner = Makeblastdb(config)
    makeblastdb_runner.set_in(str(temp_fasta))
    makeblastdb_runner.set_dbtype("nucl")
    makeblastdb_runner.set_out(str(output_path))
    makeblastdb_runner.set_parse_seqids()

    return_code = makeblastdb_runner.run()
    assert return_code == 0, "makeblastdb failed to run successfully"

    return output_path


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
def test_makeblastdb(blast_db):
    """Test if BLAST database files were created."""
    expected_files = [f"{blast_db}.nhr", f"{blast_db}.nin", f"{blast_db}.nsq"]
    for file in expected_files:
        assert os.path.exists(file), f"Expected BLAST database file {file} not found"


@pytest.mark.skipif(not is_tool_available("blastdb_aliastool"),
                    reason="blastdb_aliastool not available on PATH")
def test_blastdb_aliastool(blast_db, config, tmp_path):
    """Test creating a BLAST database alias."""
    alias_output = tmp_path / "alias_db"

    aliastool_runner = BlastdbAliastool(config)
    aliastool_runner.set_db(str(blast_db))
    aliastool_runner.set_dbtype("nucl")
    aliastool_runner.set_out(str(alias_output))
    aliastool_runner.set_title("Test Alias Database")
    aliastool_runner.set_seqidlist(str(SEQIDLIST))

    return_code = aliastool_runner.run()

    assert return_code == 0, "blastdb_aliastool failed to run successfully"

    # Check if alias files were created
    expected_files = [f"{alias_output}.nal"]
    for file in expected_files:
        assert os.path.exists(file), f"Expected alias file {file} not found"


@pytest.mark.skipif(not is_tool_available("blastdb_aliastool"),
                    reason="blastdb_aliastool not available on PATH")
def test_blastdb_aliastool_validation(config):
    """Test parameter validation in BlastdbAliastool."""
    aliastool_runner = BlastdbAliastool(config)

    # Test incompatible options
    aliastool_runner.set_out("alias_db")
    aliastool_runner.set_gi_file_in("dummy_file")
    with pytest.raises(ValueError, match="'out' and 'gi_file_in' options are incompatible"):
        aliastool_runner.validate_parameters()

    # Test missing required parameters
    aliastool_runner = BlastdbAliastool(config)
    aliastool_runner.set_dblist(["db1", "db2"])
    with pytest.raises(ValueError, match="'dblist' requires 'out', 'dbtype', and 'title' to be set"):
        aliastool_runner.validate_parameters()