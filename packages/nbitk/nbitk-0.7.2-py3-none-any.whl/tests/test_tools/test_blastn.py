import os
import pytest
import shutil
from pathlib import Path
from Bio import SeqIO
from nbitk.Tools.makeblastdb import Makeblastdb
from nbitk.Tools.blastdb_aliastool import BlastdbAliastool
from nbitk.Tools.blastdbcmd import Blastdbcmd
from nbitk.Tools.blastn import Blastn
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
    cfg.set('log_level', 'ERROR')
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


@pytest.fixture
def query_sequence(tmp_path):
    """Fixture to create a query FASTA file with the AANIC003-10.COI-5P sequence."""
    query_path = tmp_path / "query.fasta"
    sequence = "AACATTATATTTTATTTTTGGTATTTGAGCTGGTATAATTGGAACTTCTTTAAGATTATTAATTCGAGCAGAATTAGGTAATCCAGGATCTTTAATTGGAGATGATCAAATTTATAATACAATTGTCACTGCACATGCTTTTATTATAATTTTTTTTATAGTTATACCTATTATAATTGGAGGATTTGGAAATTGACTAATTCCTTTAATATTAGGAGCCCCAGATATAGCTTTCCCACGAATAAATAATATAAGATTTTGATTATTACCACCTTCTATTATTTTATTAATTTCAAGAAGAATTGTAGAAAATGGAGCAGGTACTGGTTGAACTGTCTACCCCCCGTTATCTTCTAATATTGCTCATGGAGGAAGTTCAGTAGATTTAGCTATTTTTTCCCTTCATTTAGCTGGTATCTCATCAATTTTAGGAGCTATTAATTTTATTACAACTATTATTAATATACGATTAAATAACTTATCTTTTGATCAAATACCTTTATTTGTGTGAGCTGTAGGAATTACAGCATTTTTATTATTATTATCATTACCTGTTTTAGCAGGAGCTATTACCATATTATTAACTGATCGAAATTTAAATACTTCATTTTTTGATCCAGCAGGAGGAGGAGATCCAATCTTATATCAACATTTATTT"
    with open(query_path, "w") as f:
        f.write(f">AANIC003-10.COI-5P\n{sequence}\n")
    return query_path


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


@pytest.mark.skipif(not is_tool_available("blastdbcmd"),
                    reason="blastdbcmd not available on PATH")
def test_blastdbcmd(blast_db, config, tmp_path):
    """Test retrieving a specific sequence using blastdbcmd."""
    output_file = tmp_path / "output.fasta"

    blastdbcmd_runner = Blastdbcmd(config)
    blastdbcmd_runner.set_db(str(blast_db))
    blastdbcmd_runner.set_entry(["AANIC003-10.COI-5P"])
    blastdbcmd_runner.set_outfmt("%f")
    blastdbcmd_runner.set_out(str(output_file))

    return_code = blastdbcmd_runner.run()

    assert return_code == 0, "blastdbcmd failed to run successfully"

    # Check if output file was created
    assert os.path.exists(output_file), "Output file was not created"

    # Read the output file and check the sequence
    with open(output_file, "r") as f:
        record = next(SeqIO.parse(f, "fasta"))

    assert record.id == "AANIC003-10.COI-5P", f"Expected sequence ID 'AANIC003-10.COI-5P', but got {record.id}"
    assert len(record.seq) == 658, f"Expected sequence length 658, but got {len(record.seq)}"


@pytest.mark.skipif(not is_tool_available("blastn"),
                    reason="blastn not available on PATH")
def test_blastn(blast_db, config, tmp_path, query_sequence):
    """Test running BLASTN with the AANIC003-10.COI-5P sequence as query."""
    output_file = tmp_path / "blastn_output.txt"

    blastn_runner = Blastn(config)
    blastn_runner.set_query(str(query_sequence))
    blastn_runner.set_db(str(blast_db))
    blastn_runner.set_out(str(output_file))
    blastn_runner.set_outfmt("6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore")
    blastn_runner.set_evalue(1e-10)
    blastn_runner.set_max_target_seqs(1)

    return_code = blastn_runner.run()

    assert return_code == 0, "blastn failed to run successfully"

    # Check if output file was created
    assert os.path.exists(output_file), "BLASTN output file was not created"

    # Read the output file and check the results
    with open(output_file, "r") as f:
        result = f.read().strip().split('\t')

    assert len(result) == 12, f"Expected 12 fields in BLASTN output, but got {len(result)}"
    assert result[0] == "AANIC003-10.COI-5P", f"Expected query ID 'AANIC003-10.COI-5P', but got {result[0]}"
    assert result[1] == "AANIC003-10.COI-5P", f"Expected subject ID 'AANIC003-10.COI-5P', but got {result[1]}"
    assert float(result[2]) == 100.0, f"Expected 100% identity, but got {result[2]}%"
    assert int(result[3]) == 658, f"Expected alignment length 658, but got {result[3]}"


@pytest.mark.skipif(not is_tool_available("blastn"),
                    reason="blastn not available on PATH")
def test_blastn_validation(config):
    """Test parameter validation in Blastn."""
    blastn_runner = Blastn(config)

    # Test setting and getting parameters
    blastn_runner.set_evalue(1e-5)
    assert blastn_runner.get_parameter("evalue") == "1e-05"

    blastn_runner.set_max_target_seqs(10)
    assert blastn_runner.get_parameter("max_target_seqs") == "10"

    # Test remote execution flag
    blastn_runner.set_remote(True)
    assert "remote" in blastn_runner.parameters
    blastn_runner.set_remote(False)
    assert "remote" not in blastn_runner.parameters

    # Test build_command method
    blastn_runner.set_query("query.fasta")
    blastn_runner.set_db("nr")
    blastn_runner.set_remote(True)
    command = blastn_runner.build_command()
    assert "blastn" in command
    assert "-query" in command
    assert "-db" in command
    assert "-remote" in command