import json
import time
from json.decoder import JSONDecodeError

import requests
from Bio.SeqRecord import SeqRecord
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from nbitk.config import Config
from nbitk.logger import get_formatted_logger


class IDService:
    """
    Client for running BOLD identification analyses.
    """

    # Constants for Bold configuration
    DATABASE_MAPPING = {
        1: "public.bin-tax-derep",
        2: "species",
        3: "all.bin-tax-derep",
        4: "DS-CANREF22",
        5: "public.plants",
        6: "public.fungi",
        7: "all.animal-alt",
        8: "DS-IUCNPUB",
    }

    OPERATING_MODE_MAPPING = {
        1: {"mi": 0.94, "maxh": 25},
        2: {"mi": 0.9, "maxh": 50},
        3: {"mi": 0.75, "maxh": 100},
    }

    BASE_URL = "https://id.boldsystems.org/submission"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"

    def __init__(self, config: Config, polling_interval: int = 10, retry_delay: int = 60, max_retries: int = 10):
        """
        Client for running BOLD identification analyses. The configuration object may contain settings such as:
        - `log_level`: Logging level for the service (default is WARNING)
        - `bold_database`: The BOLD database to use (default is 1 for public.bin-tax-derep)
        - `bold_operating_mode`: The operating mode for BOLD (default is 1 for 94% similarity)
        - `bold_timeout`: Timeout for BOLD requests in seconds (default is 300 seconds)
        - `bold_params`: Additional parameters for BOLD requests (default is an empty dictionary)

        The additional bold parameters can include:
        - `db`, which is one of "public.bin-tax-derep" (default), "species", "all.bin-tax-derep", "DS-CANREF22",
                "public.plants", "public.fungi", "all.animal-alt", "DS-IUCNPUB",
        - `mi`, minimum identity, e.g. 0.8 for 80% similarity
        - `maxh`, maximum hits, e.g. 100 for 100 hits
        - `mo`, maximum number of orders to return
        - `order`, order of the results, e.g. 3 for ordering by bit score

        :param config: NBITK configuration object containing BOLD connection settings
        :param polling_interval: Time in seconds between polling requests (default 10)
        :param retry_delay: Time in seconds to wait between retries (default 60)
        :param max_retries: Maximum number of retries for failed requests (default 10)
        """
        self.config = config
        if config.get("log_level") is None:
            config.set("log_level", "INFO")
        self.logger = get_formatted_logger(__name__, config)

        # Get BOLD-specific configuration with defaults
        self.database = config.get(
            "bold_database", 1
        )  # Default to public.bin-tax-derep
        self.operating_mode = config.get(
            "bold_operating_mode", 1
        )  # Default to 94% similarity
        self.timeout = config.get("bold_timeout", 300)  # 5 minutes default timeout
        self.params = config.get("bold_params", {})
        self.polling_interval = polling_interval
        self.retry_delay = retry_delay
        self.max_retries = max_retries

        # Build parameters from config
        self.params = self._build_url_params()

        self.logger.debug(
            f"Initialized BOLD service with database {self.database}, operating mode {self.operating_mode}"
        )

    def _build_url_params(self) -> dict:
        """
        Builds and validates the parameters for BOLD requests.

        :return: A dictionary of parameters.
        """
        if self.database not in self.DATABASE_MAPPING:
            raise ValueError(
                f"Invalid database: {self.database}. Must be one of {list(self.DATABASE_MAPPING.keys())}."
            )
        if self.operating_mode not in self.OPERATING_MODE_MAPPING:
            raise ValueError(
                f"Invalid operating mode: {self.operating_mode}. Must be one of {list(self.OPERATING_MODE_MAPPING.keys())}."
            )

        # Base parameters
        params = {
            "db": self.DATABASE_MAPPING[self.database],
            **self.OPERATING_MODE_MAPPING[self.operating_mode],
            "mo": 100,
            "order": 3,
        }

        # Override with any additional parameters from config
        params.update(self.config.get("bold_params", {}))

        return params

    def _get_session(self) -> requests.Session:
        """
        Creates and configures a requests.Session with a retry strategy.
        """
        session = requests.Session()
        session.headers.update({"User-Agent": self.USER_AGENT})

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.polling_interval,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)  # Mount for both HTTP and HTTPS

        return session

    def _submit_sequences(self, records: list[SeqRecord]) -> str:
        """
        Submit a sequence to BOLD and return the submission ID.

        :param record: A Bio.SeqRecord object containing the sequence to submit
        :return: The submission ID returned by BOLD
        """
        session = self._get_session()

        data = "".join(f">{record.id}\n{record.seq}\n" for record in records)
        files = {"fasta_file": ("submitted.fas", data, "text/plain")}

        try:
            self.logger.info("Submitting sequences to BOLD...")
            response = session.post(
                self.BASE_URL, params=self.params, files=files, timeout=60
            )

            # Check the status, if not correct will throw exception.
            response.raise_for_status()

            # This handles cases where the request succeeds but the JSON is malformed.
            result = response.json()

            # Handle potential missing key errors with .get()
            sub_id = result.get("sub_id")
            if not sub_id:
                raise KeyError("'sub_id' not found in response.")

            self.logger.info(f"Received submission ID: {sub_id}")
            return sub_id

        except requests.RequestException as e:
            self.logger.error(
                f"Failed to submit sequences after {self.max_retries} retries. Error: {e}"
            )
            raise

        except JSONDecodeError:
            self.logger.error("Response received but could not be decoded as JSON.")
            raise

        except KeyError as e:
            self.logger.error(f"Error parsing BOLD response: {e}")
            raise

        finally:
            session.close()

    def _wait_for_and_get_results(
        self, sub_id: str, records: list[SeqRecord]
    ) -> list[dict]:
        """
        Wait for BOLD processing to complete and return parsed results.

        :param sub_id: The submission ID returned by BOLD
        :param records: The list of input SeqRecord objects to match against results
        :return: A list of dictionaries containing the parsed results
        """
        session = self._get_session()

        try:
            start_time = time.time()

            while time.time() - start_time < self.timeout:
                self.logger.info(f"Checking BOLD results for submission {sub_id}...")

                try:
                    response = session.get(f"{self.BASE_URL}/results/{str(sub_id)}", timeout=60)

                    response.raise_for_status()

                    # If the status code is 200, try to parse the JSON.
                    # If this succeeds, the results are ready.
                    result = []
                    data = response.text
                    for json_line in data.splitlines():
                        json_object = json.loads(json_line)
                        result.append(
                            {
                                "seqid": json_object["seqid"],
                                "sequence": json_object["sequence"],
                                "results": self._parse_bold_result(json_object),
                            }
                        )

                    self.logger.info(
                        f"Successfully retrieved results for submission {sub_id}"
                    )
                    return result

                except requests.exceptions.HTTPError as e:
                    # The server returned a non-200 status code.
                    # This could be a temporary issue, so we'll wait and retry.
                    self.logger.warning(
                        f"Received HTTP error {e.response.status_code}. "
                        f"This means the result is not ready yet. Trying again in {self.polling_interval} seconds..."
                    )
                    time.sleep(self.polling_interval)

                except JSONDecodeError:
                    # Results aren't ready yet (invalid JSON format).
                    self.logger.info(
                        "Results not ready (invalid JSON format), waiting..."
                    )
                    time.sleep(self.polling_interval)

                except requests.RequestException as e:
                    # Catch other request exceptions (e.g., connection errors)
                    # and re-raise them, as they are likely unrecoverable.
                    self.logger.error(
                        f"Failed to retrieve results due to a network error: {e}"
                    )
                    raise

            raise TimeoutError(
                f"BOLD processing timed out after {self.timeout} seconds for submission {sub_id}"
            )

        finally:
            session.close()

    def _parse_bold_result(self, result_data: dict) -> list[dict]:
        """
        Parse a BOLD result response into our standard format.

        :param result_data: The raw result data from BOLD
        :return: A list of dictionaries containing parsed results
        """
        results = []
        bold_results = result_data.get("results", {})

        if bold_results:
            for key, result_info in bold_results.items():
                # Parse the key format: process_id|primer|bin_uri|taxid|etc
                key_parts = key.split("|")
                process_id = key_parts[0] if len(key_parts) > 0 else ""
                primer = key_parts[1] if len(key_parts) > 1 else ""
                bin_uri = key_parts[2] if len(key_parts) > 2 else ""
                taxid = key_parts[3] if len(key_parts) > 3 else ""

                # Extract alignment metrics
                pident = result_info.get("pident", 0.0)
                bitscore = result_info.get("bitscore", 0.0)
                evalue = result_info.get("evalue", 1.0)

                # Extract taxonomy information
                taxonomy = result_info.get("taxonomy", {})
                result_dict = {
                    "phylum": taxonomy.get("phylum"),
                    "class": taxonomy.get("class"),
                    "order": taxonomy.get("order"),
                    "family": taxonomy.get("family"),
                    "subfamily": taxonomy.get(
                        "subfamily"
                    ),  # Include subfamily if present
                    "genus": taxonomy.get("genus"),
                    "species": taxonomy.get("species"),
                    "pct_identity": pident,
                    "bitscore": bitscore,
                    "evalue": evalue,
                    "process_id": process_id,
                    "primer": primer,
                    "bin_uri": bin_uri,
                    "taxid": taxid,
                    "taxid_count": taxonomy.get("taxid_count", ""),
                }
                results.append(result_dict)
        else:
            # No matches found
            self.logger.debug(
                f"No matches found for sequence {result_data.get('seqid', 'unknown')}"
            )

        return results

    def identify_seqrecords(self, records: list[SeqRecord]) -> list[dict]:
        """
        Identify a sequence using BOLD and return the results.

        :param records: A list of Bio.SeqRecord objects containing the sequences to identify
        :return: A list of dictionaries containing the identification results
        """
        self.logger.info(f"Identifying {len(records)} sequences using BOLD")

        # Submit the sequence to BOLD
        sub_id = self._submit_sequences(records)

        # Do an inital wait to allow BOLD to start processing
        initial_wait = self.polling_interval * len(records)
        self.logger.info(f"Sequences submitted. Waiting {initial_wait} seconds for BOLD to start processing...")
        time.sleep(initial_wait)

        # Poll for results and get parsed data
        results = self._wait_for_and_get_results(sub_id, records)

        if not results:
            self.logger.warning("No identification results found for sequences")

        return results


if __name__ == "__main__":
    import argparse

    from Bio import SeqIO

    from nbitk.config import Config

    # Process command line arguments
    parser = argparse.ArgumentParser(description="BOLD ID Service Example")
    parser.add_argument("--bold_database", type=int, help="BOLD database", default=1)
    parser.add_argument(
        "--bold_operating_mode", type=int, help="BOLD operating mode", default=1
    )
    parser.add_argument(
        "--bold_timeout", type=int, help="BOLD request timeout in seconds", default=300
    )
    parser.add_argument(
        "--log_level", type=str, help="Logging level", default="WARNING"
    )
    parser.add_argument(
        "--input_file", type=str, help="Input FASTA file", required=True
    )
    args = parser.parse_args()

    # Create a Config object and set parameters from command line arguments
    config = Config()
    config.config_data = {
        "bold_database": args.bold_database,
        "bold_operating_mode": args.bold_operating_mode,
        "bold_timeout": args.bold_timeout,
        "log_level": args.log_level,
    }
    config.initialized = True

    # Initialize the IDService with the configuration
    id_service = IDService(config)

    # Process the input FASTA file and print TSV output
    id_service.logger.info(f"Processing input file: {args.input_file}")

    # Read the input FASTA file into a list of SeqRecord objects
    with open(args.input_file) as handle:
        seqrecords = list(SeqIO.parse(handle, "fasta"))
        results = id_service.identify_seqrecords(seqrecords)

        # Prints the header only once
        header = results[0].keys()
        print("\t".join(header))

        # Print the results in TSV format
        for results_dict in results:
            print("\t".join(str(results_dict.get(key, "")) for key in header))
