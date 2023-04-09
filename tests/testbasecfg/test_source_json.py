#!/usr/bin/env python3
""" test configuration via JSON config file """
import json

import pytest


def test_json_config_full(config, json_full_good):
    """verify that the json config parsing works as expected"""
    conf = config(json_full_good, True)

    print(conf.__dict__)

    # assert the config values
    assert conf is not None
    assert conf.verbose is True
    assert conf.batch_size == 65535
    assert conf.input_files == ["a.txt", "b.txt", "c.txt"]
    assert conf.yn == [True, False, True]
    assert conf.temps == [1.2, 1.3, 1.4]
    assert conf.favorite_color == "green"

    # assert a non-existant value raises AttributeError
    with pytest.raises(AttributeError):
        assert conf.blerg == 1


def test_json_config_partial(config, json_partial_good):
    """verify that the json config parsing works as expected"""
    conf = config(json_partial_good, True)

    print(conf.__dict__)

    # assert the config values
    assert conf is not None
    assert conf.verbose is False
    assert conf.batch_size == 65535
    assert conf.input_files == []
    assert conf.yn == []
    assert conf.temps == []
    assert conf.favorite_color == "green"

    # assert a non-existant value raises AttributeError
    with pytest.raises(AttributeError):
        assert conf.blerg == 1


def test_json_bad_format(config, bad_json_inputs):
    """test an invalid json file"""
    json_filename = bad_json_inputs["bad_format"]
    with pytest.raises(json.JSONDecodeError):
        conf = config(json_filename, True)
        assert conf is None


def test_json_bad_type(config, bad_json_inputs):
    """test a json file with a value of the wrong type"""
    json_filename = bad_json_inputs["bad_type"]
    with pytest.raises(TypeError):
        conf = config(json_filename, True)
        assert conf.batch_size != "white"


def test_json_bad_value(config, bad_json_inputs):
    """test a json file with a value not in the list of available choices"""
    json_filename = bad_json_inputs["bad_value"]
    with pytest.raises(ValueError):
        conf = config(json_filename, True)
        assert conf.favorite_color != "white"
