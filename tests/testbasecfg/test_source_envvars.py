#!/usr/bin/env python3
""" test configuration via environment variable """
import os

import pytest


def test_envvar_types(config, temp_envvars):
    """tests envvars of various types"""
    temp_envvars()
    os.environ["VERBOSE"] = "TRUE"
    os.environ["batch_size"] = "42"  # lowercase support is there
    os.environ["INPUT_FILES"] = "foo.py,bar.py,baz.py"
    os.environ["YN"] = "y;n;y;y;n"  # sep defined on field in conftest
    os.environ["TEMPS"] = "98.6,101.2,212.9"
    os.environ["FAVORITE_COLOR"] = "green"
    conf = config()

    assert conf is not None
    assert conf.verbose is True
    assert conf.batch_size == 42
    assert conf.input_files == ["foo.py", "bar.py", "baz.py"]
    assert conf.yn == [True, False, True, True, False]
    assert conf.temps == [98.6, 101.2, 212.9]
    assert conf.favorite_color == "green"


def test_envvar_bad_type(config, temp_envvars):
    """test envvar with value that cannot be coerced into the correct type"""
    temp_envvars()
    os.environ["BATCH_SIZE"] = "x"
    with pytest.raises(ValueError):
        _ = config()


def test_envvar_bad_value(config, temp_envvars):
    """test envvar with a value not in the list of available choices"""
    temp_envvars()
    os.environ["FAVORITE_COLOR"] = "white"
    with pytest.raises(ValueError):
        _ = config()
