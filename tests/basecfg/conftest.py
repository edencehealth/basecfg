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


# @pytest.fixture()
# def client(app):  # pylint: disable=redefined-outer-name
#     """a client fixture for use in test functions"""
#     return app.test_client()
