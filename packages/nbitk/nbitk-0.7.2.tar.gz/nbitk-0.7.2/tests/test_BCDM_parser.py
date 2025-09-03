import os
import pytest
import json
from Bio import SeqIO
from nbitk.SeqIO.BCDM import BCDMIterator

# Paths to test files
BCDM_JSONL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'BCDM.jsonl')
BCDM_TSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'BCDM.tsv')


def test_bcdm_tsv_parser():
    """Test parsing of TSV format BCDM files."""
    with open(BCDM_TSV_PATH, 'r') as handle:
        records = list(SeqIO.parse(handle, 'bcdm-tsv'))

    assert len(records) == 10  # Number of records in BCDM.tsv

    # Test first record content
    first = records[0]
    assert first.id == "AANIC003-10.COI-5P"  # record_id
    assert first.name == "AANIC003-10"  # processid
    assert first.description == "Arhodia lasiocamparia"  # identification
    assert str(first.seq).startswith("AACATTATATTTTATTTTTGGTATTTGAGCTGGTATAATT")

    # Test taxonomy annotation
    assert first.annotations['taxonomy'] == [
        "Animalia",  # kingdom
        "Arthropoda",  # phylum
        "Insecta",  # class
        "Lepidoptera",  # order
        "Geometridae",  # family
        "Oenochrominae",  # subfamily
        "None",  # tribe
        "Arhodia",  # genus
        "Arhodia lasiocamparia",  # species
        "None"  # subspecies
    ]

    # Test key BCDM fields
    bcdm = first.annotations['bcdm_fields']
    assert bcdm['marker_code'] == "COI-5P"
    assert bcdm['bin_uri'] == "BOLD:AAB9307"
    assert bcdm['collection_date_start'] == "2009-01-18"
    assert bcdm['country/ocean'] == "Australia"
    assert bcdm['nuc_basecount'] == "658"


def test_bcdm_jsonl_parser():
    """Test parsing of JSONL format BCDM files."""
    with open(BCDM_JSONL_PATH, 'r') as handle:
        records = list(SeqIO.parse(handle, 'bcdm-jsonl'))

    # Should match TSV output
    with open(BCDM_TSV_PATH, 'r') as handle:
        tsv_records = list(SeqIO.parse(handle, 'bcdm-tsv'))

    assert len(records) == len(tsv_records)

    # Compare first records
    json_rec = records[0]
    tsv_rec = tsv_records[0]
    assert json_rec.id == tsv_rec.id
    assert json_rec.name == tsv_rec.name
    assert json_rec.description == tsv_rec.description
    assert str(json_rec.seq) == str(tsv_rec.seq)
    assert json_rec.annotations['taxonomy'] == tsv_rec.annotations['taxonomy']
    assert json_rec.annotations['bcdm_fields'] == tsv_rec.annotations['bcdm_fields']


def test_missing_required_fields():
    """Test handling of records with missing required fields."""
    bad_record = {
        'processid': 'TEST001-99',
        # Missing record_id and nuc
    }

    # Create a single-record file
    test_file = os.path.join(os.path.dirname(__file__), 'data', 'bad.jsonl')
    with open(test_file, 'w') as f:
        f.write(json.dumps(bad_record))

    with pytest.raises(ValueError, match="Missing required fields"):
        with open(test_file, 'r') as handle:
            list(SeqIO.parse(handle, 'bcdm-jsonl'))

    os.remove(test_file)


def test_field_presence():
    """Test presence of key fields in parsed records."""
    with open(BCDM_TSV_PATH, 'r') as handle:
        records = list(SeqIO.parse(handle, 'bcdm-tsv'))

    for record in records:
        # Test core SeqRecord attributes
        assert record.id.endswith(".COI-5P")  # record_id pattern
        assert record.name  # processid
        assert record.description  # identification
        assert record.seq  # nuc

        # Test required annotations
        assert 'taxonomy' in record.annotations
        assert len(record.annotations['taxonomy']) == 10
        assert 'bcdm_fields' in record.annotations

        # Test key BCDM fields
        bcdm = record.annotations['bcdm_fields']
        assert 'marker_code' in bcdm
        assert 'identification' in bcdm
        assert 'identification_rank' in bcdm


def test_empty_file():
    """Test handling of empty input files."""
    empty_file = os.path.join(os.path.dirname(__file__), 'data', 'empty.tsv')
    with open(empty_file, 'w') as f:
        pass

    with open(empty_file, 'r') as handle:
        records = list(SeqIO.parse(handle, 'bcdm-tsv'))
    assert len(records) == 0

    os.remove(empty_file)


if __name__ == "__main__":
    pytest.main()