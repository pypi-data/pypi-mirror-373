import os
import pytest
import shutil
from pathlib import Path
from Bio import SeqIO
from Bio import AlignIO
from nbitk.Tools.hmmalign import Hmmalign
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


@pytest.mark.skipif(not is_tool_available("hmmalign"),
                    reason="hmmalign not available on PATH")
def test_hmmalign(temp_fasta, config, tmp_path):
    """Test running hmmalign with the BCDM sequences."""
    output_file = tmp_path / "alignment.sto"

    hmmalign_runner = Hmmalign(config)
    hmmalign_runner.set_hmmfile(str(HMM_PATH))
    hmmalign_runner.set_seqfile(str(temp_fasta))
    hmmalign_runner.set_output(str(output_file))
    hmmalign_runner.set_outformat("Stockholm")
    hmmalign_runner.set_trim()

    return_code = hmmalign_runner.run()

    assert return_code == 0, "hmmalign failed to run successfully"

    # Check if output file was created
    assert os.path.exists(output_file), "hmmalign output file was not created"

    # Read the output file and check the results
    alignment = AlignIO.read(output_file, "stockholm")

    assert len(alignment) > 0, "No sequences in the alignment"


@pytest.mark.skipif(not is_tool_available("hmmalign"),
                    reason="hmmalign not available on PATH")
def test_hmmalign_validation(config):
    """Test parameter validation in Hmmalign."""
    hmmalign_runner = Hmmalign(config)

    # Test missing required parameters
    with pytest.raises(ValueError, match="HMM file is required for hmmalign"):
        hmmalign_runner.validate_parameters()

    hmmalign_runner.set_hmmfile("test.hmm")
    with pytest.raises(ValueError, match="Sequence file is required for hmmalign"):
        hmmalign_runner.validate_parameters()

    # Test incompatible options
    hmmalign_runner.set_seqfile("sequences.fasta")
    hmmalign_runner.set_amino()
    hmmalign_runner.set_dna()
    with pytest.raises(ValueError, match="Only one of --amino, --dna, or --rna can be set"):
        hmmalign_runner.validate_parameters()


@pytest.mark.skipif(not is_tool_available("hmmalign"),
                    reason="hmmalign not available on PATH")
def test_hmmalign_command_building(config):
    """Test command building in Hmmalign."""
    hmmalign_runner = Hmmalign(config)
    hmmalign_runner.set_hmmfile("test.hmm")
    hmmalign_runner.set_seqfile("sequences.fasta")
    hmmalign_runner.set_output("alignment.sto")
    hmmalign_runner.set_outformat("Stockholm")
    hmmalign_runner.set_trim()

    command = hmmalign_runner.build_command()

    assert command[0] == "hmmalign"
    assert "-o" in command
    assert "--outformat" in command
    assert "--trim" in command
    assert command[-2] == "test.hmm"
    assert command[-1] == "sequences.fasta"