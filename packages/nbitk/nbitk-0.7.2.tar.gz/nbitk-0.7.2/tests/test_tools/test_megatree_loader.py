import os
import pytest
import sqlite3
import shutil
from pathlib import Path
from Bio import SeqIO
from Bio import AlignIO
from nbitk.Tools.hmmalign import Hmmalign
from nbitk.Tools.raxml_ng import RaxmlNg
from nbitk.Tools.megatree_loader import MegatreeLoader
from nbitk.config import Config
from nbitk.SeqIO.BCDM import BCDMIterator

# Construct relative path to the test data
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
BCDM_TSV_PATH = TEST_DATA_DIR / "BCDM.tsv"
HMM_PATH = TEST_DATA_DIR / "COI-5P.hmm"

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
    cfg.set('log_level', 'ERROR')
    return cfg


@pytest.fixture
def aligned_fasta(temp_fasta, config, tmp_path):
    """Fixture to create an aligned FASTA file using hmmalign."""
    stockholm_file = tmp_path / "aligned.sto"
    output_file = tmp_path / "aligned.fasta"

    hmmalign_runner = Hmmalign(config)
    hmmalign_runner.set_hmmfile(str(HMM_PATH))
    hmmalign_runner.set_seqfile(str(temp_fasta))
    hmmalign_runner.set_output(str(stockholm_file))
    hmmalign_runner.set_outformat("Stockholm")
    hmmalign_runner.set_trim()

    return_code = hmmalign_runner.run()
    assert return_code == 0, "hmmalign failed to run successfully"

    # Convert Stockholm to FASTA
    with open(stockholm_file, "r") as sto_handle, open(output_file, "w") as fasta_handle:
        alignments = AlignIO.parse(sto_handle, "stockholm")
        AlignIO.write(alignments, fasta_handle, "fasta")

    return output_file


@pytest.fixture
def raxml_tree(aligned_fasta, config, tmp_path):
    """Fixture to create a phylogenetic tree using raxml-ng."""
    output_prefix = tmp_path / "raxml_output"

    raxml_runner = RaxmlNg(config)
    raxml_runner.set_msa(str(aligned_fasta))
    raxml_runner.set_model("GTR+G")
    raxml_runner.set_prefix(str(output_prefix))
    raxml_runner.set_threads(2)  # Use 2 threads for testing
    raxml_runner.set_search()

    return_code = raxml_runner.run()
    assert return_code == 0, "raxml-ng failed to run successfully"

    best_tree_file = f"{output_prefix}.raxml.bestTree"
    assert os.path.exists(best_tree_file), "RAxML-NG best tree file not found"

    return best_tree_file


@pytest.mark.skipif(not is_tool_available("megatree-loader"),
                    reason="megatree-loader not available on PATH")
def test_megatree_loader(raxml_tree, config, tmp_path):
    """Test running megatree-loader with the RAxML-NG tree."""
    output_db = tmp_path / "megatree.sqlite"

    megatree_runner = MegatreeLoader(config)
    megatree_runner.set_infile(str(raxml_tree))
    megatree_runner.set_dbfile(str(output_db))

    return_code = megatree_runner.run()

    assert return_code == 0, "megatree-loader failed to run successfully"

    # Check if output database file was created
    assert os.path.exists(output_db), "megatree-loader output database file not found"

    # Verify the structure of the SQLite database
    conn = sqlite3.connect(str(output_db))
    cursor = conn.cursor()

    # Check if the 'node' table exists and has the correct columns
    cursor.execute("PRAGMA table_info(node)")
    columns = {row[1] for row in cursor.fetchall()}
    expected_columns = {"id", "parent", "length", "height", "left", "right"}
    assert expected_columns.issubset(
        columns), f"Not all expected columns found in 'node' table. Missing: {expected_columns - columns}"

    # Check if there are any rows in the 'node' table
    cursor.execute("SELECT COUNT(*) FROM node")
    row_count = cursor.fetchone()[0]
    assert row_count > 0, "No rows found in the 'node' table"

    conn.close()


@pytest.mark.skipif(not is_tool_available("megatree-loader"),
                    reason="megatree-loader not available on PATH")
def test_megatree_loader_validation(config):
    """Test parameter validation in MegatreeLoader."""
    megatree_runner = MegatreeLoader(config)

    # Test missing required parameter
    with pytest.raises(ValueError, match="Input file \\(-i\\) is required for megatree-loader"):
        megatree_runner.validate_parameters()

    # Test setting and getting parameters
    megatree_runner.set_infile("input_tree.newick")
    assert megatree_runner.get_parameter("i") == "input_tree.newick"

    megatree_runner.set_dbfile("output_db.sqlite")
    assert megatree_runner.get_parameter("d") == "output_db.sqlite"


@pytest.mark.skipif(not is_tool_available("megatree-loader"),
                    reason="megatree-loader not available on PATH")
def test_megatree_loader_command_building(config):
    """Test command building in MegatreeLoader."""
    megatree_runner = MegatreeLoader(config)
    megatree_runner.set_infile("input_tree.newick")
    megatree_runner.set_dbfile("output_db.sqlite")

    command = megatree_runner.build_command()

    assert command[0] == "megatree-loader"
    assert "-i" in command
    assert "input_tree.newick" in command
    assert "-d" in command
    assert "output_db.sqlite" in command