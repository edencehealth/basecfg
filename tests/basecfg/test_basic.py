#!/usr/bin/env python3
""" some basic pytest checks """
import pytest


def test_defaults(config):
    """we want to ensure that by default requests are blocked"""
    conf = config()

    # assert the defaults
    assert conf is not None
    assert conf.verbose is False
    assert conf.batch_size is None
    assert conf.input_files == []
    assert conf.yn == []
    assert conf.temps == []
    assert conf.favorite_color == "blue"

    # assert a non-existant value raises AttributeError
    with pytest.raises(AttributeError):
        assert conf.blerg is None
