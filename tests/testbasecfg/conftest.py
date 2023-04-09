#!/usr/bin/env python3
""" configuration for tests in this package """
# pylint: disable=too-few-public-methods

import os
from typing import List, Optional

import pytest

from basecfg import BaseCfg

opt = BaseCfg.optfunc()


@opt.link
class Config(BaseCfg):
    """Configuration for a fictional app"""

    verbose: bool = opt(
        default=False,
        doc="whether to log verbosely",
    )

    batch_size: Optional[int] = opt(
        default=None,
        doc="how big chunks should be when transferring data from the database",
    )

    input_files: List[str] = opt(
        default=[],
        doc="a list of files to process",
    )

    yn: List[bool] = opt(
        default=[],
        doc="a list of booleans?",
        sep=";",
    )

    temps: List[float] = opt(
        default=[],
        doc="a list of floats",
    )

    favorite_color: str = opt(
        default="blue",
        choices=["blue", "green", "orange"],
        doc="a choice between the best colors",
    )


@pytest.fixture()
def config():
    """a fixture which returns a config class instance (pre-linked)"""
    return Config


# content of test_tmp_path.py
JSON_FULL_GOOD = """
{
  "batch_size": 65535,
  "favorite_color": "green",
  "input_files": [
    "a.txt",
    "b.txt",
    "c.txt"
  ],
  "temps": [
    1.2,
    1.3,
    1.4
  ],
  "verbose": true,
  "yn": [
    true,
    false,
    true
  ]
}
""".strip()


@pytest.fixture()
def json_full_good(tmp_path):
    """test a json file which covers all options in the config"""
    tmp_file = tmp_path / "json_full_good.json"
    tmp_file.write_text(JSON_FULL_GOOD)
    assert tmp_file.read_text() == JSON_FULL_GOOD
    yield tmp_file
    os.unlink(tmp_file)


JSON_PARTIAL_GOOD = """
{
  "batch_size": 65535,
  "favorite_color": "green"
}
""".strip()


@pytest.fixture()
def json_partial_good(tmp_path):
    """test a json file which only covers a few options of the config"""
    tmp_file = tmp_path / "json_partial_good.json"
    tmp_file.write_text(JSON_PARTIAL_GOOD)
    assert tmp_file.read_text() == JSON_PARTIAL_GOOD
    yield tmp_file
    os.unlink(tmp_file)


@pytest.fixture(scope="function")
def temp_envvars():
    """fixture which saves envvars and then restores them after a test runs"""
    saved_env = os.environ.copy()
    yield lambda: None
    os.environ = saved_env


JSON_BAD_FORMAT = """
{
  batch_size: 65535,
  "favorite_color": "green"
}
""".strip()

JSON_BAD_TYPE = """
{
  "batch_size": "white"
}
""".strip()

JSON_BAD_VALUE = """
{
  "favorite_color": "white"
}
""".strip()


@pytest.fixture()
def bad_json_inputs(tmp_path):
    """fixture which presents a dict of problematic json files"""
    inputs = {
        "bad_format": JSON_BAD_FORMAT,
        "bad_type": JSON_BAD_TYPE,
        "bad_value": JSON_BAD_VALUE,
    }
    result = {}

    for name, content in inputs.items():
        tmp_file = tmp_path / f"json_{name}.json"
        tmp_file.write_text(content)
        assert tmp_file.read_text() == content
        result[name] = tmp_file
    yield result
    _ = [os.unlink(path) for path in result.values()]


ENVFILE_FULL_GOOD = """
BATCH_SIZE=65535
FAVORITE_COLOR=green
INPUT_FILES=a.txt,b.txt,c.txt
TEMPS=1.2,1.3,1.4
VERBOSE=true
YN=y;n;y
""".strip()


@pytest.fixture
def envfile_full_good(tmp_path):
    """
    fixture which presents a correctly-formatted envfile covering all options in the
    config
    """
    tmp_file = tmp_path / ".env-full_good"
    tmp_file.write_text(ENVFILE_FULL_GOOD)
    assert tmp_file.read_text() == ENVFILE_FULL_GOOD
    yield tmp_file
    os.unlink(tmp_file)


ENVFILE_PARTIAL_GOOD = """
BATCH_SIZE=65535
FAVORITE_COLOR=green
"""


@pytest.fixture
def envfile_partial_good(tmp_path):
    """
    fixture which presents a correctly-formatted envfile covering all options in the
    config
    """
    tmp_file = tmp_path / ".env-partial_good"
    tmp_file.write_text(ENVFILE_PARTIAL_GOOD)
    assert tmp_file.read_text() == ENVFILE_PARTIAL_GOOD
    yield tmp_file
    os.unlink(tmp_file)


ENVFILE_BAD_FORMAT = """
BATCH_SIZE: 65535
FAVORITE_COLOR=green
""".strip()

ENVFILE_BAD_TYPE = """
BATCH_SIZE=white
""".strip()

ENVFILE_BAD_VALUE = """
FAVORITE_COLOR=white
""".strip()


@pytest.fixture()
def bad_envfile_inputs(tmp_path):
    """fixture which presents a dict of problematic json files"""
    inputs = {
        "bad_format": ENVFILE_BAD_FORMAT,
        "bad_type": ENVFILE_BAD_TYPE,
        "bad_value": ENVFILE_BAD_VALUE,
    }
    result = {}

    for name, content in inputs.items():
        tmp_file = tmp_path / f".env-{name}"
        tmp_file.write_text(content)
        assert tmp_file.read_text() == content
        result[name] = tmp_file
    yield result
    _ = [os.unlink(path) for path in result.values()]


@pytest.fixture()
def secrets_test_files(tmp_path):
    """fixture which presents a dict of problematic json files"""
    inputs = {
        "good": {
            "batch_size": "65535",
            "favorite_color": "green",
            "input_files": "a.txt,b.txt,c.txt",
            "temps": "1.2,1.3,1.4",
            "verbose": "true",
            "yn": "y;n;y",
        },
        "bad_type": {
            "batch_size": "white",
        },
        "bad_value": {
            "favorite_color": "white",
        },
    }
    result = {}

    for group_name, subitems in inputs.items():
        group_dir = tmp_path / group_name
        os.mkdir(group_dir)
        result[group_name] = group_dir
        for optname, content in subitems.items():
            tmp_file = group_dir / optname
            tmp_file.write_text(content)
            assert tmp_file.read_text() == content
    yield result
    for group_name, group_dir in result.items():
        for filename in inputs[group_name]:
            secret_path = os.path.join(group_dir, filename)
            if os.path.isfile(secret_path):
                os.unlink(secret_path)
        os.rmdir(group_dir)


# @pytest.fixture()
# def client(app):  # pylint: disable=redefined-outer-name
#     """a client fixture for use in test functions"""
#     return app.test_client()
