import pytest
from nbitk.logger import get_formatted_logger
from nbitk.config import Config
import os


@pytest.fixture
def config():
    config = Config()
    # Create a temporary config file
    config_content = """
    log_level: INFO
    """
    with open('temp_config.yaml', 'w') as f:
        f.write(config_content)

    # Load the config
    config.load_config('temp_config.yaml')

    yield config

    # Clean up: remove the temporary config file
    os.remove('temp_config.yaml')


def test_multiple_handlers(config):
    # Create the first logger
    logger1 = get_formatted_logger("test_logger", config)

    # Count the handlers after first creation
    handlers_count1 = len(logger1.handlers)

    # Create a second logger with the same name
    logger2 = get_formatted_logger("test_logger", config)

    # Count the handlers after second creation
    handlers_count2 = len(logger2.handlers)

    # Check if the number of handlers increased
    assert handlers_count2 == handlers_count1, (
        f"Expected same number of handlers after second logger creation. "
        f"First count: {handlers_count1}, Second count: {handlers_count2}"
    )

    # Verify that both loggers are actually the same object
    assert logger1 is logger2, "Both loggers should be the same object"