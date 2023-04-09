#!/usr/bin/env python3
""" tests for loading values from docker secrets """
# pylint: disable=duplicate-code
import pytest


def test_load_dockersecrets_good(config, secrets_test_files):
    """test loading a conforming value from a docker secret"""
    conf = config(secrets_dir=secrets_test_files["good"])
    assert conf is not None
    assert conf.verbose is True
    assert conf.batch_size == 65535
    assert conf.input_files == ["a.txt", "b.txt", "c.txt"]
    assert conf.yn == [True, False, True]
    assert conf.temps == [1.2, 1.3, 1.4]
    assert conf.favorite_color == "green"
    with pytest.raises(AttributeError):
        assert conf.blerg == 1


def test_load_dockersecrets_bad_type(config, secrets_test_files):
    """test loading a conforming value from a docker secret"""
    with pytest.raises(ValueError):
        conf = config(secrets_dir=secrets_test_files["bad_type"])
        assert conf.batch_size != "white"


def test_load_dockersecrets_bad_value(config, secrets_test_files):
    """test loading a conforming value from a docker secret"""
    with pytest.raises(ValueError):
        conf = config(secrets_dir=secrets_test_files["bad_value"])
        assert conf.batch_size != "white"
