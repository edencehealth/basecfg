#!/usr/bin/env python3
""" general access method tests """
import pytest


def test_len(config, json_full_good):
    """verify that len is working correctly"""
    conf = config(json_full_good)
    assert len(conf) == 6


def test_iterate(config, json_full_good):
    """verify that iteration throws no exception"""
    expected_keys = (
        "verbose",
        "batch_size",
        "input_files",
        "yn",
        "temps",
        "favorite_color",
    )
    expected_key = iter(expected_keys)

    conf = config(json_full_good)
    count = 0
    for k in conf:
        assert k == next(expected_key)
        count += 1
    assert count == 6


def test_getitem(config, json_full_good):
    """verify getitem access to configuration"""
    conf = config(json_full_good)
    assert conf is not None
    assert conf["verbose"] is True
    assert conf["batch_size"] == 65535
    assert conf["input_files"] == ["a.txt", "b.txt", "c.txt"]
    assert conf["yn"] == [True, False, True]
    assert conf["temps"] == [1.2, 1.3, 1.4]
    assert conf["favorite_color"] == "green"
    # assert a non-existant value raises KeyError
    with pytest.raises(KeyError):
        assert conf["blerg"] is None


def test_contains(config, json_full_good):
    """verify that membership testing works"""
    conf = config(json_full_good)
    assert conf is not None
    assert ("input_files" in conf) is True
    assert ("output_files" in conf) is False
