#!/usr/bin/env python3
""" configuration for tests in this package """

from typing import List, Optional

import pytest

from basecfg import BaseCfg

opt = BaseCfg.OptFunc()


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
CONFIG_FULL_GOOD = """
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
    tmp_file.write_text(CONFIG_FULL_GOOD)
    assert tmp_file.read_text() == CONFIG_FULL_GOOD
    return tmp_file


CONFIG_PARTIAL_GOOD = """
{
  "batch_size": 65535,
  "favorite_color": "green"
}
""".strip()


@pytest.fixture()
def json_partial_good(tmp_path):
    """test a json file which only covers a few options of the config"""
    tmp_file = tmp_path / "json_partial_good.json"
    tmp_file.write_text(CONFIG_PARTIAL_GOOD)
    assert tmp_file.read_text() == CONFIG_PARTIAL_GOOD
    return tmp_file


CONFIG_BAD_FORMAT = """
{
  batch_size: 65535,
  "favorite_color": "green"
}
""".strip()

CONFIG_BAD_TYPE = """
{
  "batch_size": "white"
}
""".strip()

CONFIG_BAD_VALUE = """
{
  "favorite_color": "white"
}
""".strip()


@pytest.fixture()
def bad_json_inputs(tmp_path):
    """fixture which presents a dict of problematic json files"""
    inputs = {
        "bad_format": CONFIG_BAD_FORMAT,
        "bad_type": CONFIG_BAD_TYPE,
        "bad_value": CONFIG_BAD_VALUE,
    }
    result = {}

    for name, content in inputs.items():
        tmp_file = tmp_path / f"json_{name}.json"
        tmp_file.write_text(content)
        assert tmp_file.read_text() == content
        result[name] = tmp_file
    return result


# @pytest.fixture()
# def client(app):  # pylint: disable=redefined-outer-name
#     """a client fixture for use in test functions"""
#     return app.test_client()
