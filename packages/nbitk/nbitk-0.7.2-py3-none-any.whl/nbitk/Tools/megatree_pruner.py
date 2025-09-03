from typing import List, Tuple
from .tool_runner import ToolRunner
from nbitk.config import Config
import logging


class MegatreePruner(ToolRunner):
    """
    A subclass of ToolRunner specifically for running megatree-pruner.

    Examples:
        >>> config = Config()
        >>> config.load_config('path/to/config.yaml')
        >>> megatree_pruner = MegatreePruner(config)
        >>> megatree_pruner.set_dbfile('tree_database.sqlite')
        >>> megatree_pruner.set_infile('taxa_list.txt')
        >>> megatree_pruner.set_outfile('pruned_tree.newick')
        >>> megatree_pruner.set_tabular(True)
        >>> megatree_pruner.set_relabel(True)
        >>> return_code = megatree_pruner.run()
    """

    def __init__(self, config: Config):
        """
        Initialize the MegatreePrunerRunner with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)
        self.tool_name = "megatree-pruner"

    def set_dbfile(self, dbfile: str) -> None:
        """
        Set the database file produced by megatree-*-loader scripts.

        :param dbfile: Path to the database file.
        :type dbfile: str
        """
        self.set_parameter("d", dbfile)

    def set_infile(self, infile: str) -> None:
        """
        Set the input file containing a list of taxon names.

        :param infile: Path to the input file.
        :type infile: str
        """
        self.set_parameter("i", infile)

    def set_outfile(self, outfile: str) -> None:
        """
        Set the output file for the pruned tree.

        :param outfile: Path to the output file.
        :type outfile: str
        """
        self.set_parameter("o", outfile)

    def set_list(self, taxa_list: List[str]) -> None:
        """
        Set the list of taxon names to be retained.

        :param taxa_list: List of taxon names.
        :type taxa_list: List[str]
        """
        self.set_parameter("l", ",".join(taxa_list))

    def set_tabular(self, tabular: bool = True) -> None:
        """
        Set the option to produce a tab-separated table instead of a Newick-formatted tree.

        :param tabular: Whether to produce tabular output.
        :type tabular: bool
        """
        if tabular:
            self.set_parameter("t", "")

    def set_relabel(self, relabel: bool = True) -> None:
        """
        Set the option to relabel internal nodes in the output.

        :param relabel: Whether to relabel internal nodes.
        :type relabel: bool
        """
        if relabel:
            self.set_parameter("r", "")

    def build_command(self) -> Tuple[List[str], str]:
        """
        Build the megatree-pruner command with all set parameters.

        :return: A tuple containing the complete megatree-pruner command as a list of strings,
                 and the output file path (or None if not specified).
        :rtype: Tuple[List[str], str]
        """
        command = super().build_command()

        # Handle verbosity based on logger level
        logger_level = self.logger.getEffectiveLevel()
        if logger_level <= logging.DEBUG:
            command.extend(["-v", "-v"])
        elif logger_level <= logging.INFO:
            command.append("-v")

        # Handle boolean flags (parameters without values)
        bool_params = ["t", "r", "h", "m"]
        for param in bool_params:
            if self.get_parameter(param) is not None:
                command.append(f"-{param}")

        # Get the output file if specified
        outfile = self.get_parameter("o")

        return command, outfile

    def run(self) -> int:
        """
        Run the megatree-pruner command after validating parameters.

        :return: The return code of the megatree-pruner command.
        :rtype: int
        :raises ValueError: If required parameters are missing or incompatible options are set.
        """
        self.validate_parameters()
        command, outfile = self.build_command()

        if outfile:
            with open(outfile, 'w') as f:
                return self._run_command(command, stdout=f)
        else:
            return self._run_command(command)

    def _run_command(self, command: List[str], stdout=None) -> int:
        """
        Run the command with optional output redirection.

        :param command: The command to run.
        :type command: List[str]
        :param stdout: File object to redirect stdout to, or None for no redirection.
        :type stdout: file object or None
        :return: The return code of the command.
        :rtype: int
        """
        import subprocess

        try:
            result = subprocess.run(command, check=True, stdout=stdout, stderr=subprocess.PIPE, text=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed with return code {e.returncode}")
            self.logger.error(f"Error output: {e.stderr}")
            return e.returncode

    def is_arg(self, key: str) -> bool:
        """
        Check if a key is a command-line argument.

        :param key: Parameter key.
        :type key: str
        :return: True if the key is a command-line argument, False otherwise.
        :rtype: bool
        """
        return not key == 'o'

    def validate_parameters(self) -> None:
        """
        Validate that required parameters are set before running the command.

        :raises ValueError: If required parameters are missing or incompatible options are set.
        """
        if self.get_parameter("d") is None:
            raise ValueError("Database file (-d) is required for megatree-pruner.")

        if self.get_parameter("i") is None and self.get_parameter("l") is None:
            raise ValueError("Either file (-i) or list (-l) must be provided for megatree-pruner.")

        if self.get_parameter("i") is not None and self.get_parameter("l") is not None:
            raise ValueError(
                "Only one of file (-i) or list (-l) can be provided for megatree-pruner."
            )