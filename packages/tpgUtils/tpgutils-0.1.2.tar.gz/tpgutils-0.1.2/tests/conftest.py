import pytest
import os
from collections import Counter


""" Central repository for Pytest fixtures for breakout groups."""

@pytest.fixture(scope='session')
def create_folders(tmp_path_factory):
    """this is a setup/teardown example"""
    # set_up: set paths
    base_dir = tmp_path_factory.mktemp("tpgUtils")
    base_dir = base_dir / "data"
    base_dir.mkdir()

    # yield, to let all tests within the scope
    yield

    # tear_down: remove test dir & files
    # if os.path.exists(tmp_path_factory):
    #     for pth, dir, files in os.walk(tmp_path_factory):
    #         for d in dir:
    #             for fl in files:
    #                 os.remove(f"{tmp_path_factory}{os.sep}{d}{fl}")
    #         for fl in files:
    #             os.remove(f"{tmp_path_factory}{fl}")
    #     os.rmdir(tmp_path_factory)

@pytest.fixture
def get_config():
    """Parses the configuration file values and returns them in a dict"""
    pass

@pytest.fixture
def config_event_defaults():
    """set cfg variables to EVENT values"""
    pass

