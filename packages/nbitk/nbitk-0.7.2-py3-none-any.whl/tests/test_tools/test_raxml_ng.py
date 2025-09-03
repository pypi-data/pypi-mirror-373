import os
import pytest
import shutil
from pathlib import Path
from Bio import SeqIO
from Bio import AlignIO
from Bio import Phylo
from nbitk.Tools.hmmalign import Hmmalign
from nbitk.Tools.raxml_ng import RaxmlNg
from nbitk.config import Config
from nbitk.SeqIO.BCDM import BCDMIterator

# Construct relative path to the test data
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
BCDM_TSV_PATH = TEST_DATA_DIR / "BCDM.tsv"
HMM_PATH = TEST_DATA_DIR / "COI-5P.hmm"  # Assuming there's an HMM file named test.hmm in the data directory

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


@pytest.mark.skipif(not is_tool_available("raxml-ng"),
                    reason="raxml-ng not available on PATH")
def test_raxml_ng(aligned_fasta, config, tmp_path):
    """Test running raxml-ng with the aligned FASTA file."""
    output_prefix = tmp_path / "raxml_output"

    raxml_runner = RaxmlNg(config)
    raxml_runner.set_msa(str(aligned_fasta))
    raxml_runner.set_model("GTR+G")
    raxml_runner.set_prefix(str(output_prefix))
    raxml_runner.set_threads(2)  # Use 2 threads for testing
    raxml_runner.set_search()

    return_code = raxml_runner.run()

    assert return_code == 0, "raxml-ng failed to run successfully"

    # Check if output files were created
    expected_files = [f"{output_prefix}.raxml.bestTree", f"{output_prefix}.raxml.log"]
    for file in expected_files:
        assert os.path.exists(file), f"Expected raxml-ng output file {file} not found"

    # Parse the best tree
    best_tree_file = f"{output_prefix}.raxml.bestTree"
    tree = Phylo.read(best_tree_file, "newick")

    # Count the number of tips in the tree
    tip_count = len(tree.get_terminals())

    # Count the number of sequences in the input alignment
    with open(aligned_fasta, "r") as f:
        seq_count = len(list(SeqIO.parse(f, "fasta")))

    # Verify that the number of tips matches the number of input sequences
    assert tip_count == seq_count, f"Number of tips in the tree ({tip_count}) does not match the number of input sequences ({seq_count})"


@pytest.mark.skipif(not is_tool_available("raxml-ng"),
                    reason="raxml-ng not available on PATH")
def test_raxml_ng_validation(config):
    """Test parameter validation in RaxmlNg."""
    raxml_runner = RaxmlNg(config)

    # Test setting and getting parameters
    raxml_runner.set_threads(4)
    assert raxml_runner.get_parameter("threads") == "4"

    raxml_runner.set_seed(12345)
    assert raxml_runner.get_parameter("seed") == "12345"

    # Test build_command method
    raxml_runner.set_msa("alignment.fasta")
    raxml_runner.set_model("GTR+G")
    raxml_runner.set_prefix("test_run")
    raxml_runner.set_all()
    command = raxml_runner.build_command()

    assert command[0] == "raxml-ng"
    assert "--msa" in command
    assert "--model" in command
    assert "--prefix" in command
    assert "--all" in command


@pytest.mark.skipif(not is_tool_available("raxml-ng"),
                    reason="raxml-ng not available on PATH")
def test_raxml_ng_command_building(config):
    """Test command building in RaxmlNg."""
    raxml_runner = RaxmlNg(config)
    raxml_runner.set_msa("alignment.fasta")
    raxml_runner.set_model("GTR+G")
    raxml_runner.set_prefix("test_run")
    raxml_runner.set_threads(4)
    raxml_runner.set_search()
    raxml_runner.set_bs_trees(100)

    command = raxml_runner.build_command()

    assert command[0] == "raxml-ng"
    assert "--msa" in command
    assert "--model" in command
    assert "--prefix" in command
    assert "--threads" in command
    assert "--search" in command
    assert "--bs-trees" in command
    assert "100" in command