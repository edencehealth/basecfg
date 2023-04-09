#!/usr/bin/env python3
""" tests for loading values from envfile sources"""
# pylint: disable=duplicate-code
import pytest


def test_envfile_good(config, envfile_full_good):
    """test loading a conforming value from a docker secret"""
    conf = config(envfile_path=envfile_full_good)
    assert conf is not None
    assert conf.verbose is True
    assert conf.batch_size == 65535
    assert conf.input_files == ["a.txt", "b.txt", "c.txt"]
    assert conf.yn == [True, False, True]
    assert conf.temps == [1.2, 1.3, 1.4]
    assert conf.favorite_color == "green"

    # assert a non-existant value raises AttributeError
    with pytest.raises(AttributeError):
        assert conf.blarf == 1


def test_envfile_config_partial(config, envfile_partial_good):
    """verify that the envfile config parsing works as expected"""
    conf = config(envfile_path=envfile_partial_good)
    assert conf is not None
    assert conf.verbose is False
    assert conf.batch_size == 65535
    assert conf.input_files == []
    assert conf.yn == []
    assert conf.temps == []
    assert conf.favorite_color == "green"


def test_envfile_bad_format(config, bad_envfile_inputs):
    """test an invalid envfile file"""
    envfile_path = bad_envfile_inputs["bad_format"]
    with pytest.raises(ValueError):
        conf = config(envfile_path=envfile_path, envfile_required=True)
        assert conf is None


def test_envfile_bad_type(config, bad_envfile_inputs):
    """test a envfile file with a value of the wrong type"""
    envfile_path = bad_envfile_inputs["bad_type"]
    with pytest.raises(ValueError):
        conf = config(envfile_path=envfile_path, envfile_required=True)
        assert conf.batch_size != "white"


def test_envfile_bad_value(config, bad_envfile_inputs):
    """test a envfile file with a value not in the list of available choices"""
    envfile_path = bad_envfile_inputs["bad_value"]
    with pytest.raises(ValueError):
        conf = config(envfile_path=envfile_path, envfile_required=True)
        assert conf.favorite_color != "white"
