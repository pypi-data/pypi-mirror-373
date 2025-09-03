import unittest.mock
import pytest
import shutil
from pathlib import Path
from nbitk.Tools.vsearch import Vsearch
from nbitk.config import Config
from unittest.mock import MagicMock, patch
import subprocess


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


@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_vsearch_initialization(config):
    vsearch_runner = Vsearch(config)
    assert vsearch_runner.tool_name == "vsearch"


@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_set_params(config):
    vsearch_runner = Vsearch(config)
    # Create a mock for set_parameter to check if it is called properly
    vsearch_runner.set_parameter = MagicMock()
    params = {
        'fastq_mergepairs': 'input_R1.fastq',
        'output': 'merged_output.fastq',
        'threads': '8',
        'maxaccepts': '10',
        'maxrejects': '5',
        'id': '0.97'
    }

    vsearch_runner.set_params(params)

    # Check that set_parameter is called for each param
    vsearch_runner.set_parameter.assert_any_call('fastq_mergepairs',
                                                 'input_R1.fastq')
    vsearch_runner.set_parameter.assert_any_call('output',
                                                 'merged_output.fastq')
    vsearch_runner.set_parameter.assert_any_call('threads', '8')
    vsearch_runner.set_parameter.assert_any_call('maxaccepts', '10')
    vsearch_runner.set_parameter.assert_any_call('maxrejects', '5')
    vsearch_runner.set_parameter.assert_any_call('id', '0.97')


@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_build_command(config):
    vsearch_runner = Vsearch(config)

    # Set real vsearch parameters
    params = {
        "fastq_mergepairs": "input_R1.fastq",
        "reverse": "input_R2.fastq",
        "fastqout": "merged_output.fastq",
        "threads": "8",
        "maxaccepts": "10",
        "maxrejects": "5",
        "id": "0.97"
        }

    vsearch_runner.set_params(params)

    # Build the command
    command = vsearch_runner.build_command()

    # test that the commands were properly built
    assert command == ["vsearch", "--fastq_mergepairs",
                       "input_R1.fastq", "--reverse", "input_R2.fastq",
                       "--fastqout", 'merged_output.fastq', '--threads', '8',
                       '--maxaccepts', '10',
                       '--maxrejects', '5', '--id', '0.97']


@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_set_params_invalid(config, caplog):
    vsearch_runner = Vsearch(config)
    vsearch_runner.get_valid_tool_params = MagicMock(return_value=[
        "--threads", "--maxaccepts", "--maxrejects", "--id"])

    # Create a mock for set_parameter to check if it is called properly
    vsearch_runner.set_parameter = MagicMock()

    params = {
        'invalid_param': 'some_value',
        'threads': '8'
    }
    with pytest.raises(AssertionError) as e_info:
        with caplog.at_level('ERROR'):
            vsearch_runner.set_params(params)

        # Check that set_parameter is called only for valid params

        vsearch_runner.set_parameter.assert_any_call('threads', '8')
        assert "invalid_param is not a valid vsearch parameter" in caplog.text


@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_set_params_empty(config):
    vsearch_runner = Vsearch(config)
    vsearch_runner.get_valid_tool_params = MagicMock(return_value=[
        "--threads", "--maxaccepts", "--maxrejects", "--id"])

    # Create a mock for set_parameter to check if it is called properly
    vsearch_runner.set_parameter = MagicMock()

    params = {}

    vsearch_runner.set_params(params)

    # Check that set_parameter is not called
    vsearch_runner.set_parameter.assert_not_called()


# Test run method with no parameters set
@patch("subprocess.Popen")
@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_run_no_params(mock_popen, config):
    vsearch_runner = Vsearch(config)
    vsearch_runner.get_valid_tool_params = MagicMock(return_value=[
        "--threads", "--maxaccepts", "--maxrejects", "--id"])

    # Simulate subprocess behavior
    mock_process = MagicMock()
    mock_process.stdout = iter(["output line 1", "output line 2"])
    mock_process.stderr = iter(["error line 1", "error line 2"])
    mock_process.wait.return_value = 0  # Simulate successful completion
    mock_popen.return_value = mock_process

    # Call the run method without setting any parameters
    return_code = vsearch_runner.run()

    # Ensure subprocess.Popen was called with the expected command
    mock_popen.assert_called_once_with(
        ["vsearch"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # Ensure that the run method returns the expected return code
    assert return_code == 0


# Test run method with valid parameters
@patch("subprocess.Popen")
@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_run_valid_params(mock_popen, config):
    vsearch_runner = Vsearch(config)
    vsearch_runner.get_valid_tool_params = MagicMock(return_value=[
        "--fastq_mergepairs", "--reverse", "--fastqout",
        "--threads", "--maxaccepts", "--maxrejects", "--id"])

    # Simulate subprocess behavior
    mock_process = MagicMock()
    mock_process.stdout = iter(["output line 1", "output line 2"])
    mock_process.stderr = iter(["error line 1", "error line 2"])
    mock_process.wait.return_value = 0  # Simulate successful completion
    mock_popen.return_value = mock_process

    # Set real vsearch parameters
    params = {
        "fastq_mergepairs": "input_R1.fastq",
        "reverse": "input_R2.fastq",
        "fastqout": "merged_output.fastq",
        "threads": "8",
        "maxaccepts": "10",
        "maxrejects": "5",
        "id": "0.97"
        }
    vsearch_runner.set_params(params)

    # Call the run method
    return_code = vsearch_runner.run()

    # Ensure subprocess.Popen was called with the expected command
    expected_call_run = [
        "vsearch", "--fastq_mergepairs", "input_R1.fastq",
        "--reverse", "input_R2.fastq", "--fastqout",
        "merged_output.fastq", "--threads", "8",
        "--maxaccepts", "10",
        "--maxrejects", "5", "--id", "0.97"
    ]
    mock_popen.assert_has_calls([
        unittest.mock.call(expected_call_run,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           text=True, bufsize=1, universal_newlines=True)
    ])

    # Ensure that the run method returns the expected return code
    assert return_code == 0


# Test run method when subprocess fails (non-zero return code)
@patch("subprocess.Popen")
@pytest.mark.skipif(not is_tool_available("vsearch"),
                    reason="vsearch not available on PATH")
def test_run_failure(mock_popen, config):
    vsearch_runner = Vsearch(config)
    vsearch_runner.get_valid_tool_params = MagicMock(return_value=[
        "--fastq_mergepairs", "--reverse",
        "--fastqout", "--threads",
        "--maxaccepts", "--maxrejects", "--id"])

    # Simulate subprocess behavior (fail)
    mock_process = MagicMock()
    mock_process.stdout = iter(["output line"])
    mock_process.stderr = iter(["error line"])
    mock_process.wait.return_value = 1  # Simulate failure (non-zero exit code)
    mock_popen.return_value = mock_process

    # Set real vsearch parameters
    params = {
        "fastq_mergepairs": "input_R1.fastq",
        "reverse": "input_R2.fastq",
        "fastqout": "merged_output.fastq",
        "threads": "8",
        "maxaccepts": "10",
        "maxrejects": "5",
        "id": "0.97"
    }
    vsearch_runner.set_params(params)

    # Call the run method
    return_code = vsearch_runner.run()

    # Ensure subprocess.Popen was called with the expected command
    expected_call_run = [
        "vsearch", "--fastq_mergepairs", "input_R1.fastq",
        "--reverse", "input_R2.fastq", "--fastqout",
        "merged_output.fastq", "--threads", "8",
        "--maxaccepts", "10",
        "--maxrejects", "5", "--id", "0.97"
    ]
    mock_popen.assert_has_calls([
        unittest.mock.call(expected_call_run,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           text=True, bufsize=1,
                           universal_newlines=True)
    ])

    # Check that the return code is not zero
    assert return_code == 1
