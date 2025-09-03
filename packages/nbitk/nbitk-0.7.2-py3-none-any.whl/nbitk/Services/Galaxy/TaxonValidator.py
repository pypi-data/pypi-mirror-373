import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from io import StringIO
import logging
import tempfile
import pandas as pd
import numpy as np
from nbitk.Services.Galaxy.BLASTN import BLASTNClient
from nbitk.config import Config
from Bio import SeqIO, Entrez
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import time


class TaxonValidator(BLASTNClient):
    """
    Client for validating taxonomic assignments of DNA sequences using BLAST. This client
    is tailored to the use case where barcode records stored in the Core Sequence Cloud
    are validated in small batches against a reference database. The validation consists
    of a check to see whether the putative taxon (note: we assume this is the family name)
    is present in the BLAST results. The results are attached to the input records for
    further analysis.
    """

    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the TaxonValidator client. This constructor delegates to the BLASTNClient
        constructor, which in turn initializes the Galaxy connection and tool. Consult the
        BLASTNClient documentation and that of the AbstractClient for more information.
        :param config: NBITK Config object containing Galaxy connection settings
        :param logger: Optional logging.logger instance. If None, creates one using the class name
        """
        super().__init__(config, logger)
        # Set the Entrez email to the specified address
        Entrez.email = "bioinformatics@naturalis.nl"
        self.taxonomy_cache = {}  # Cache for taxonomy lookups to minimize API calls
        self.query_config = {}

    def validate_records(self, records: List[Dict[str, Any]], params: dict = { 'max_target_seqs': 100, 'identity': 80 }) -> List[Dict[str, Any]]:
        """
        Validate a list of records taxonomically by running BLAST and comparing the results.
        :param records: List of records. Each record is a dictionary with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon (note: we now assume this is the family name)
            - nuc: Nucleotide sequence
        :param params: Optional parameters for the BLAST analysis. The parameters are passed
            directly to the BLASTNClient.run_blast method. The parameters are tool-specific
            and can be found in the BLASTNClient documentation.
        :return: Enriched records with validation result and other analytics. Each record is a
            dictionary with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon
            - nuc: Nucleotide sequence
            - is_valid: Boolean indicating if the record is valid
            - blast_results: Pandas data frame with the BLAST results
            - best_hits: List of dictionaries containing the best hit information (including ties)
            - confidence: Confidence score based on the E-value of the top hit
            - timestamp: Timestamp of the validation
        """

        # Create SeqRecord objects and write to FASTA file
        self.logger.info(f"Going to validate {len(records)} records")
        fasta_filename = self._bcdm2fasta(records)

        # Run BLAST on the Galaxy
        self.logger.info(f"Running BLAST on {fasta_filename}")
        result = self.run_blast(fasta_filename, no_file_write=True, **params)

        # Process BLAST results
        self.logger.info(f"Processing BLAST results")
        output_file = result['blast_output_fasta']

        # Update config object
        self.query_config = {
            'maxh': params.get('max_target_seqs', 100),
            'mi': params.get('identity', 80),
            'mo': None,
            'order': None,
            'db': params.get('databases', ["Genbank CO1 (2023-11-15)"])[0],
        }

        return self._parse_blast_output(output_file, records, is_string=True)

    def get_taxonomic_lineage(self, taxon_id: str) -> Dict[str, str]:
        """
        Retrieve the complete taxonomic lineage for a given NCBI taxon ID.
        Uses caching to reduce API calls to NCBI.

        :param taxon_id: The NCBI taxonomy ID
        :return: A dictionary with taxonomic ranks as keys and taxonomic names as values
        """
        # Check cache first
        if taxon_id in self.taxonomy_cache:
            self.logger.debug(f"Using cached taxonomy for ID {taxon_id}")
            return self.taxonomy_cache[taxon_id]

        self.logger.debug(f"Fetching taxonomy for ID {taxon_id}")
        taxonomy_dict = {}

        try:
            # Fetch the taxonomy record
            handle = Entrez.efetch(db="taxonomy", id=str(taxon_id), retmode="xml")
            records = Entrez.read(handle)
            handle.close()

            if not records or len(records) == 0:
                self.logger.warning(f"No taxonomy record found for ID {taxon_id}")
                return taxonomy_dict

            record = records[0]

            # Get the scientific name (usually species name)
            taxonomy_dict['scientific_name'] = record.get('ScientificName', '')

            # Extract lineage information from LineageEx which contains detailed rank information
            if 'LineageEx' in record:
                for entry in record['LineageEx']:
                    if 'Rank' in entry and 'ScientificName' in entry:
                        rank = entry['Rank']
                        name = entry['ScientificName']
                        if rank != 'no rank':  # Skip entries without a specific rank
                            taxonomy_dict[rank] = name

            # The current taxon's rank might not be in LineageEx, so add it separately
            if 'Rank' in record and record['Rank'] != 'no rank':
                taxonomy_dict[record['Rank']] = record['ScientificName']

            # Add the taxon ID to the dictionary
            taxonomy_dict['taxon_id'] = taxon_id

            # Replace spaces in keys with underscores
            taxonomy_dict = {key.replace(" ", "_"): value for key, value in taxonomy_dict.items()}

            # Cache the result
            self.taxonomy_cache[taxon_id] = taxonomy_dict

            return taxonomy_dict

        except Exception as e:
            self.logger.error(f"Error retrieving taxonomy for ID {taxon_id}: {str(e)}")
            # Implement exponential backoff if getting rate-limited
            time.sleep(1)
            return taxonomy_dict

    def evalue_to_confidence(self, evalue, max_evalue=10.0):
        """
        Transform a BLAST E-value into a confidence score between 0 and 1.

        :param evalue: The E-value from BLAST results
        :param max_evalue: Maximum E-value to consider (higher values will be capped)
        :return: Confidence score between 0 and 1, where 1 represents maximum confidence
        """
        # Handle special cases
        if evalue is None or pd.isna(evalue):
            return 0.0

        # For E-value of 0, return maximum confidence
        if evalue == 0:
            return 1.0

        # Cap the E-value at the maximum
        evalue = min(float(evalue), max_evalue)

        # Exponential transformation, approaches 1 as E-value approaches 0
        k = 5.0 / max_evalue  # Controls the steepness of the curve
        return np.exp(-k * evalue)

    def _parse_blast_output(
        self, output: str, records: List[Dict[str, Any]], is_string: bool = False
    ) -> List[Dict[str, Any]]:
        """
        The BLAST operation performed by Galaxy returns a tab-separated file with the results. For every input
        record, the operation can return zero or more results. This method parses the BLAST output file for each
        set of results corresponding with an input 'local_id'. If the expected taxon is found in any of the results,
        the record is marked as valid by setting the 'is_valid' field to True. If no results are found, the record
        is marked as invalid. The full results are attached to the record under the 'blast_results' key as a pandas
        data frame for further analysis. Furthermore, the 'timestamp' field is added to the record to indicate when
        the validation was performed.
        :param output: The BLAST output file
        :param records: List of records. The records are dictionaries with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon
            - nuc: Nucleotide sequence
        :param is_string: If True, the output parameter is treated as a string containing the BLAST results
            instead of a file path. Default is False.
        :return: Enriched records. The records are dictionaries with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon
            - nuc: Nucleotide sequence
            - is_valid: Boolean indicating if the record is valid
            - blast_results: Pandas data frame with the BLAST results
            - best_hits: List of dictionaries containing the best BLAST hit data (ties included)
            - confidence: Confidence score based on E-value of the top hit
            - timestamp: Timestamp of the validation
        """
        self.logger.debug(f"Parsing BLAST output file {output}")

        # Accommodate both file path and string input for testing
        if is_string:
            df = pd.read_csv(StringIO(output), sep="\t", dtype=str)
        else:
            df = pd.read_csv(output, sep="\t", dtype=str)

        # Convert numerical columns to appropriate data types
        numeric_cols = ["#Identity percentage", "#Coverage", "#evalue", "#bitscore"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Rename columns first
        df.columns = [c.replace(" ", "_").replace("#", "") for c in df.columns]

        # Then group by query ID
        grouped = dict(tuple(df.groupby("Query_ID")))

        # Process records
        for seq_dict in records:
            local_id = seq_dict["local_id"]
            exp_taxon = seq_dict["identification"]
            seq_dict["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            seq_dict["best_hits"] = []

            blast_rows = grouped.get(local_id)

            if blast_rows is None or blast_rows.empty:
                # No results: placeholder hit
                seq_dict["is_valid"] = False
                seq_dict["blast_results"] = None
                seq_dict["confidence"] = 0.0
                seq_dict["best_hits"].append({"blast_hit_id": str(uuid.uuid4())})
            else:
                seq_dict["is_valid"] = False

                # Use itertuples to significantly enhance speed
                for hit in blast_rows.itertuples(index=False):
                    taxon_id = hit.Subject_Taxonomy_ID
                    hit_dict = {
                        "blast_hit_id": str(uuid.uuid4()),
                        "sequence_id": hit.Subject_accession,
                        "source": hit.Source,
                        "coverage": hit.Coverage,
                        "identity_percentage": hit.Identity_percentage,
                        "evalue": hit.evalue,
                        "bitscore": hit.bitscore,
                        "taxon_id": taxon_id,
                        "confidence": self.evalue_to_confidence(hit.evalue),
                        "lineage": self.get_taxonomic_lineage(taxon_id) if taxon_id else None,
                    }

                    seq_dict["best_hits"].append(hit_dict)

                    # Mark valid if expected taxon is in lineage
                    lineage = hit_dict["lineage"]
                    if lineage and exp_taxon and exp_taxon in lineage.values():
                        seq_dict["is_valid"] = True

                # Optionally keep full blast results
                # seq_dict["blast_results"] = blast_rows.to_dict("records")

        return records

    def _bcdm2fasta(self, records: List[Dict[str, Any]]) -> str:
        """
        Convert a list of records to a temporary FASTA file. In this operation, the
        'nuc' key in each record is expected to contain the nucleotide sequence, and
        the 'local_id' key is expected to contain a locally unique identifier. The
        resulting FASTA file will have the local_id as the header and the nucleotide
        sequence as the body. No other keys or values are expected in the records.
        The resulting file is uploaded to Galaxy for BLAST analysis. The results
        are joined with the input by way of the local_id.
        :param records: List of records
        :return: Name of the temporary FASTA file
        """
        self.logger.debug(f"Converting {len(records)} records to FASTA")

        # Create a list of SeqRecord objects
        seq_records = []
        for seq_dict in records:
            sequence = Seq(seq_dict['nuc'])
            record = SeqRecord(
                seq=sequence,
                id=seq_dict['local_id'],
                description=""  # Empty description to keep the FASTA header clean
            )
            seq_records.append(record)

        # Create a temporary file with .fasta extension
        temp_fasta = tempfile.NamedTemporaryFile(suffix='.fasta', delete=False)

        # Write records to the temporary FASTA file
        SeqIO.write(seq_records, temp_fasta.name, "fasta")
        return temp_fasta.name