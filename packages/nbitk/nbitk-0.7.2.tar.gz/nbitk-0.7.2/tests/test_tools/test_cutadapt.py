import pytest
import shutil
from pathlib import Path
from nbitk.Tools.cutadapt import Cutadapt
from nbitk.config import Config
from unittest.mock import MagicMock


# Construct the path to the config file
CONFIG_PATH = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'


def is_tool_available(name):
    """Check whether `name` is on PATH and executable."""
    return shutil.which(name) is not None

@pytest.fixture
def config():
    """Fixture to create and load a Config object for each test."""
    cfg = Config()
    cfg.load_config(CONFIG_PATH)
    cfg.set('log_level', 'ERROR')
    return cfg


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_cutcutadapt_initialization(config):
    cutadapt_runner = Cutadapt(config)
    assert cutadapt_runner.tool_name == "cutadapt"

# Test set_params method with real cutadapt parameters


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_set_params(config):
    cutadapt_runner = Cutadapt(config)
    # Create a mock for set_parameter to check if it is called properly
    cutadapt_runner.set_parameter = MagicMock()
    params = {
        'output': 'merged_output.fastq',
        'cores': '8',
        "json": "cutadapt.json",
        "adapter": "AAACTCGTGCCAGCCACC",
        "front": "CTGTCTCTTATACACATCT"
    }
    cutadapt_runner.set_params(params)

    # Check that set_parameter is called for each param
    cutadapt_runner.set_parameter.assert_any_call(
        'output', 'merged_output.fastq')
    cutadapt_runner.set_parameter.assert_any_call('cores', '8')
    cutadapt_runner.set_parameter.assert_any_call(
        'json', 'cutadapt.json')
    cutadapt_runner.set_parameter.assert_any_call(
        'adapter', 'AAACTCGTGCCAGCCACC')
    cutadapt_runner.set_parameter.assert_any_call(
        'front', 'CTGTCTCTTATACACATCT')


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_set_params_file_not_exist(config):
    cutadapt_runner = Cutadapt(config)
    # Create a mock for set_parameter to check if it is called properly
    cutadapt_runner.set_parameter = MagicMock()
    params = {
        'output': 'merged_output.fastq',
        'cores': '8',
        "json": "cutadapt.json",
        "adapter": "AAACTCGTGCCAGCCACC",
        "front": "CTGTCTCTTATACACATCT",
        "sequences": ["input_R1.fastq", "input_R2.fastq"]
    }
    with pytest.raises(AssertionError):
        cutadapt_runner.set_params(params)


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_build_command(config):
    cutadapt_runner = Cutadapt(config)

    # Set real cutadapt parameters
    params = {
        'output': 'merged_output.fastq',
        'cores': '8',
        "json": "cutadapt.json",
        "adapter": "AAACTCGTGCCAGCCACC",
        "front": "CTGTCTCTTATACACATCT",
        "discard-untrimmed": "",
        "g": "AAACTCGTGCCAGCCACC",
        "a": "CTGTCTCTTATACACATCT"
    }
    cutadapt_runner.set_params(params)

    # Build the command
    command = cutadapt_runner.build_command()

    # test that the commands were properly built
    assert command == [
        "cutadapt", "--output", "merged_output.fastq",
        "--cores", "8", "--json", "cutadapt.json", "--adapter",
        "AAACTCGTGCCAGCCACC", "--front", "CTGTCTCTTATACACATCT",
        "--discard-untrimmed", "-g", "AAACTCGTGCCAGCCACC",
        "-a", "CTGTCTCTTATACACATCT"]


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_set_params_invalid(config, caplog):
    cutadapt_runner = Cutadapt(config)
    params = {
        'invalid_param': 'some_value',
        'cores': '8'
    }
    with pytest.raises(AssertionError):
        cutadapt_runner.set_params(params)


@pytest.mark.skipif(not is_tool_available("cutadapt"),
                    reason="cutadapt not available on PATH")
def test_run(config):
    cutadapt_runner = Cutadapt(config)
    params = {
        'output': 'merged_output.fastq',
        'cores': '8',
        "json": "cutadapt.json",
        "adapter": "AAACTCGTGCCAGCCACC",
        "front": "CTGTCTCTTATACACATCT",
        "discard-untrimmed": "",
        "g": "AAACTCGTGCCAGCCACC",
        "a": "CTGTCTCTTATACACATCT",
        "sequences": ["tests/data/sample_R1.fastq.gz"]
    }

    # Mock the existence of the input file
    cutadapt_runner.set_params(params)
    return_code = cutadapt_runner.run()
    assert return_code == 0
