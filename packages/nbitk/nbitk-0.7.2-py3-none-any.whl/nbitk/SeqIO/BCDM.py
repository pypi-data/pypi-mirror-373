from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import json
import csv
import sys

class BCDMIterator:
    """
    Iterator for BCDM (Barcode Data Matrix) formatted files.

    The BCDM format is a data standard for DNA barcode records that includes
    specimen metadata, taxonomic classification, and sequence data. This parser
    creates Bio.SeqRecord objects with annotations that preserve the rich
    metadata while making essential fields readily accessible for barcode
    validation.
    """

    REQUIRED_FIELDS = {'record_id', 'nuc'}
    TAXONOMY_FIELDS = {
        'kingdom', 'phylum', 'class', 'order', 'family',
        'subfamily', 'tribe', 'genus', 'species', 'subspecies'
    }

    def __init__(self, handle):
        self.handle = handle
        # Set CSV field size limit to system maximum
        maxInt = sys.maxsize
        while True:
            try:
                csv.field_size_limit(maxInt)
                break
            except OverflowError:
                maxInt = int(maxInt/10)

    def _create_seqrecord(self, record):
        # Validate required fields
        if not all(field in record for field in ['record_id', 'nuc']):
            raise ValueError("Missing required fields: record_id and nuc")

        seq = Seq(record.get("nuc"))
        seqrecord = SeqRecord(
            seq=seq,
            id=record["record_id"],
            name=record.get("processid", ""),
            description=record.get('identification', '')
        )

        # Set core annotations
        seqrecord.annotations["molecule_type"] = "DNA"

        # Full taxonomy list with all ranks
        seqrecord.annotations["taxonomy"] = [
            record.get("kingdom", ""),
            record.get("phylum", ""),
            record.get("class", ""),
            record.get("order", ""),
            record.get("family", ""),
            record.get("subfamily", ""),
            record.get("tribe", ""),
            record.get("genus", ""),
            record.get("species", ""),
            record.get("subspecies", "")
        ]

        # Store complete BCDM fields, including those also in taxonomy
        seqrecord.annotations["bcdm_fields"] = {
            k: v for k, v in record.items()
            if k != "nuc" and v is not None
        }

        return seqrecord


class BCDMIteratorJsonl(BCDMIterator):
    """Iterator for BCDM (Barcode Data Matrix) formatted JSON lines files."""

    def __iter__(self):
        return self._parse_json()

    def _parse_json(self):
        for line in self.handle:
            record = json.loads(line)
            yield self._create_seqrecord(record)


class BCDMIteratorTsv(BCDMIterator):
    """Iterator for BCDM (Barcode Data Matrix) formatted TSV files."""

    def __iter__(self):
        return self._parse_tsv()

    def _parse_tsv(self):
        """Process TSV in chunks to maintain memory efficiency."""
        tsv_reader = csv.DictReader(self.handle, delimiter="\t")
        for record in tsv_reader:
            if seqrecord := self._create_seqrecord(record):
                yield seqrecord


# Add the BCDM parser to Biopython's SeqIO
SeqIO._FormatToIterator["bcdm-jsonl"] = BCDMIteratorJsonl
SeqIO._FormatToIterator["bcdm-tsv"] = BCDMIteratorTsv