from typing import List
from .tool_runner import ToolRunner
from nbitk.config import Config
import os
import ast
import re
from typing import Union


class Cutadapt(ToolRunner):
    """
    A subclass of ToolRunner specifically for running cutadapt.

    Examples:

        >>> from nbitk.Tools.cutadapt import cutadapt
        >>> from nbitk.config import Config

        >>> config = Config()
        >>> config.load_config('path/to/config.yaml')
        >>> cutadapt_runner.set_params({
        >>>     "adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC",
        >>>     "front": "CTGTCTCTTATACACATCT",
        >>>     "cores": "8"})
        >>> return_code = cutadapt_runner.run()
    """

    def __init__(self, config: Config):
        """
        Initialize the Cutadapt runner with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)
        self.tool_name = "cutadapt"

    def set_input_sequences(self, sequences: List[str]) -> None:
        """
        Set the sequences parameter for Cutadapt.

        Args:
            sequences (List[str]): A list of sequence files to be used by Cutadapt.
            if only one sequence file is provided, it should be a list with one element.
        Returns:
            None
        """
        self.set_params({"sequences": sequences})

    def set_output(self, output: str) -> None:
        """
        Set the output parameter for Cutadapt.

        Args:
            output (str): The output file path for Cutadapt.
        Returns:
            None
        """
        self.set_params({"output": output})

    def set_pair_output(self, pair_output: str) -> None:
        """
        Set the pair output parameter for Cutadapt.

        Args:
            pair_output (str): The pair output file path for Cutadapt.
        Returns:
            None
        """
        self.set_params({"paired-output": pair_output})

    def set_adapter(self, adapter: str) -> None:
        """
        Set the adapter parameter for Cutadapt.

        Args:
            adapter (str): The adapter sequence to be used by Cutadapt.
        Returns:
            None
        """
        self.set_params({"adapter": adapter})

    def set_front_adapter(self, front: str) -> None:
        """
        Set the front adapter parameter for Cutadapt.

        Args:
            front (str): The front adapter sequence to be used by Cutadapt.
        Returns:
            None
        """
        self.set_params({"front": front})

    def set_minimum_length(self, minimum_length: int) -> None:
        """
        Set the minimum length parameter for Cutadapt.

        Args:
            minimum_length (int): The minimum length of reads to be kept by Cutadapt.
        Returns:
            None
        """
        self.set_params({"minimum-length": minimum_length})

    def set_quality_cutoff(self, quality_cutoff: Union[int, str]) -> None:
        """
        Set the quality cutoff parameter for Cutadapt.

        Args:
            quality_cutoff (int): The quality cutoff for reads to be kept by Cutadapt.
        Returns:
            None
        """
        self.set_params({"quality-cutoff": str(quality_cutoff)})

    def set_overlap(self, overlap: int) -> None:
        """
        Set the overlap parameter for Cutadapt.

        Args:
            overlap (int): The overlap length for reads to be kept by Cutadapt.
        Returns:
            None
        """
        self.set_params({"overlap": str(overlap)})

    def set_max_n(self, max_n: int) -> None:
        """
        Set the maximum N parameter for Cutadapt.

        Args:
            max_n (int): The maximum number of Ns allowed in reads by Cutadapt.
        Returns:
            None
        """
        self.set_params({"max-n": str(max_n)})

    def set_cores(self, cores: int = 0) -> None:
        """
        Set the number of cores to be used by Cutadapt.

        Args:
            cores (int): The number of cores to be used by Cutadapt.
        Returns:
            None
        """
        self.set_params({"cores": cores})

    def set_discard_untrimmed(self, discard_untrimmed: bool = True) -> None:
        """
        Set the discard untrimmed parameter for Cutadapt.

        Args:
            discard_untrimmed (bool): Whether to discard untrimmed reads.
        Returns:
            None
        """
        if discard_untrimmed is True:
            self.set_params({"discard-untrimmed": ""})

    def set_trim_n(self, trim_n: bool = False) -> None:
        """
        Set the trim N parameter for Cutadapt.

        Args:
            trim_n (bool): Whether to trim Ns from reads.
        Returns:
            None
        """
        if trim_n is True:            self.set_params({"trim-n": ""})

    def set_fasta_output(self, output_fasta: bool = False) -> None:
        """
        Set to output FASTA to standard output even on FASTQ input.

        Args:
            output_fasta (bool): Whether to output FASTA to standard output.
        """
        if output_fasta is True:
            self.set_params({"fasta": ""})

    def set_json_report(self, json_output_file: str) -> None:
        """
        Set to output JSON to standard output.

        Args:
            json_output_file (str): The JSON output file path.
        """

        self.set_params({"json": json_output_file})

    def set_error_rate(self, error_rate: float) -> None:
        """
        Set the error rate parameter for Cutadapt.

        Args:
            error_rate (float): The error rate for Cutadapt.
        Returns:
            None
        """
        self.set_params({"error-rate": str(error_rate)})

    def set_params(self, params: dict) -> None:
        """
        Set multiple command-line parameters for cutadapt.

        Args:
            params (dict): A dictionary where keys are parameter names (str) and
                        values are the parameter value (str or any type that
                        can be converted to a string).
        Returns:
            None
        """
        cutadapt_valid_params = self.get_valid_tool_params("--help")
        # remove any commas, parentheses, and periods from the valid parameters
        cutadapt_valid_params = [re.sub(r'[,\(\)\.]', "", param)
                                 for param in cutadapt_valid_params]

        for param, value in params.items():
            # special case for sequences, since cutadapt doesnt have a named parameter for it

            if param == "sequences":
                # eval if sequences are a valid file path
                valid_sequences_paths = []
                try:
                    for seq_path in value:
                        assert os.path.isfile(seq_path), f"provided sequence file does not exist: {seq_path}"
                        valid_sequences_paths.append(seq_path)

                except AssertionError as e:
                    self.logger.error(str(e))
                    raise
                # if there are valid sequences paths, set the parameter
                if valid_sequences_paths:
                    self.set_parameter(param, valid_sequences_paths)

            else:  # validate and set all other named parameters
                try:
                    assert f'--{param}' in cutadapt_valid_params or \
                        f'-{param}' in cutadapt_valid_params, \
                        f"{param} is not a valid {self.tool_name} parameter"
                    self.set_parameter(param, value)
                    self.logger.info(f"Set parameter --{param} to {value}")
                except AssertionError as e:
                    self.logger.error(str(e))
                    raise

    def build_command(self) -> List[str]:
        """
        Build the Cutadapt command with all set parameters.

        :return: The complete Cutadapt command as a list of strings.
        :rtype: List[str]
        """

        command = super().build_command()

        # get the index of "--sequences" parameter
        if "--sequences" in command:

            seq_index = command.index("--sequences")
            sequences = command[seq_index + 1]  # get the sequences value

            command.pop(seq_index)  # remove the "--sequences" parameter
            command.pop(seq_index)  # remove the sequences value

            command = command + ast.literal_eval(sequences)

            return command
        else:
            return command

    @staticmethod
    def long_arg_prefix() -> str:
        """
        Get the appropriate prefix for a long command-line argument

        :return: The appropriate prefix for a long argument
        :rtype: str
        """
        return "--"
