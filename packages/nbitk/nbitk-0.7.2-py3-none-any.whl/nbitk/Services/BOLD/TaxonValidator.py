import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from nbitk.logger import get_formatted_logger
from nbitk.Services.BOLD.IDService import IDService
from nbitk.config import Config
import uuid


class TaxonValidator():
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the TaxonValidator client. The object delegates to the IDService
        object rather than subclassing. Consult the IDService documentation for more information.
        :param config: NBITK Config object containing logging and BOLD connection settings
        :param logger: Optional logging.logger instance. If None, creates one using the class name
        """
        if logger is not None:
            self.logger = logger
        else:
            self.logger = get_formatted_logger(__name__, config)
        self.query_config = None
        self.config = config

    def validate_records(self, records: List[Dict[str, Any]], params: dict = { 'max_target_seqs': 100, 'identity': 80 }, polling_interval: int = 10, retry_delay: int = 60, max_retries: int = 10) -> List[Dict[str, Any]]:
        """
        Validate a list of records taxonomically by running BOLD ID service and comparing the results.
        :param records: List of records. Each record is a dictionary with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon (note: we now assume this is the family name)
            - nuc: Nucleotide sequence
        :param params: Optional parameters for the BOLD analysis. The parameters are passed
            to the BOLD web service method. Default {'max_target_seqs': 100, 'identity': 80}
        :param polling_interval: Number of seconds to wait between status checks (default: 10)
        :param retry_delay: Number of seconds to wait between retries (default: 60)
        :param max_retries: Maximum number of retry attempts (default: 10)
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
        seqrecords = self._prepare_seqrecords(records)
        idservice = self._prepare_idservice(params, polling_interval, retry_delay, max_retries)
        results = idservice.identify_seqrecords(seqrecords)
        enriched_records = self._parse_bold_output(results, records)
        self.query_config = idservice.params
        return enriched_records


    def _prepare_idservice(self, params: Dict, polling_interval: int = 10, retry_delay: int = 60, max_retries: int = 10) -> IDService:
        """
        Prepare the IDService instance for taxonomic validation using BOLD.
        :param params: Parameters for the BOLD analysis including:
            - identity: Minimum percent identity threshold (default: 80)
            - max_target_seqs: Maximum number of target sequences to return (default: 100)
        :param polling_interval: Number of seconds to wait between status checks (default: 10)
        :param retry_delay: Number of seconds to wait between retries (default: 60)
        :param max_retries: Maximum number of retry attempts (default: 10)
        :return: An instance of IDService configured for BOLD
        """

        # Set BOLD parameters
        parms = self.config.get('bold_params', {})
        parms['mi'] = params.get('identity', 80) / 100.0  # Convert percentage to fraction
        parms['maxh'] = params.get('max_target_seqs', 100)

        # Run BOLD ID service
        config = Config()
        config.config_data = {
            'bold_database': self.config.get('bold_database', 1),  # Default to public.bin-tax-derep
            'bold_operating_mode': self.config.get('bold_operating_mode', 1),  # Default to 94% similarity
            'bold_timeout': self.config.get('bold_timeout', 300),  # 5 minutes default timeout
            'bold_params': parms
        }
        config.initialized = True
        bold_service = IDService(config, polling_interval, retry_delay, max_retries)

        return bold_service

    def _prepare_seqrecords(self, records) -> List[SeqRecord]:
        """
        Prepare a list of SeqRecord objects from the provided records for taxonomic validation.
        :param records: A list of records, where each record is a dictionary with the following keys:
            - local_id: Locally unique identifier
            - identification: Expected taxon (e.g., family name)
            - nuc: Nucleotide sequencez
        :return: A list of SeqRecord objects ready for validation
        """
        if len(records) > 500:
            self.logger.warning("More than 500 records provided for validation. This may take a long time to process.")

        # Prepare as SeqRecord objects
        seqrecords = []
        for record in records:
            if not record.get("nuc"):
                self.logger.warning(f"Record {record.get('local_id', 'unknown')} has no nucleotide sequence. Skipping.")
                continue
            seqrecord = SeqRecord(
                seq=Seq(record.get("nuc")),
                id=record["local_id"]
            )
            seqrecords.append(seqrecord)
        self.logger.debug(f"Validating {len(seqrecords)} records taxonomically")

        return seqrecords


    def _parse_bold_output(self, results, records) -> List[Dict[str, Any]]:
        """
        Parse the BOLD ID service's results
        :param results: List of BOLD results
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
        self.logger.debug(f"Parsing BOLD output")

        enriched_records = []
        for result in results:

            # Match this result to the original records
            seqid = result['seqid']
            focal_record = next((d for d in records if d.get("local_id") == seqid), None)
            identification = focal_record['identification'] if focal_record else None

            # Create enriched record structure
            enriched_record = {
                'local_id': seqid,
                'identification': identification,
                'nuc': result['sequence'],
                'is_valid': False,
                'blast_results': result['results'],
                'best_hits': [],
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat()
            }

            # Add results to enriched record
            matches = set()
            for hit in result['results']:
                hit_dict = {
                    "blast_hit_id": str(uuid.uuid4()), # Add a unique quid for each hit for the biocloud team
                    "sequence_id": hit["process_id"],
                    "source": "BOLD",
                    "coverage": None,
                    "identity_percentage": hit["pct_identity"],
                    "evalue": hit["evalue"],
                    "bitscore": hit["bitscore"],
                    "taxon_id": hit["taxid"],
                    "confidence": self.evalue_to_confidence(hit["evalue"]),
                    "lineage": {
                        "phylum": hit["phylum"],
                        "class": hit["class"],
                        "order": hit["order"],
                        "family": hit["family"],
                        "subfamily": hit["subfamily"],
                        "genus": hit["genus"],
                        "species": hit["species"],
                        "taxon_id": hit["taxid"],
                    },
                }
                for key in ['phylum', 'class', 'order', 'family', 'subfamily', 'genus', 'species']:
                    matches.add(hit[key])

                # Update highest confidence hit
                if hit_dict['confidence'] > enriched_record['confidence']:
                    enriched_record['confidence'] = hit_dict['confidence']

                # Add hit to best hits
                enriched_record['best_hits'].append(hit_dict)

            # If we have matches, set the is_valid flag
            if identification is not None and identification in matches:
                enriched_record['is_valid'] = True

            enriched_records.append(enriched_record)

        return enriched_records


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