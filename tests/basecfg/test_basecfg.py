#!/usr/bin/env python3
""" some basic pytest checks """
import json
import os

import pytest


def test_defaults(config):
    """ensure that default values are working"""
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


def test_args_help(config, capsys):
    """test -h support in argparser"""
    with pytest.raises(SystemExit):
        _ = config(cli_args=["-h"])
    captured = capsys.readouterr()
    expected_contents = (
        "--help",
        "--verbose",
        "--batch-size",
        "--input-files",
        "--yn",
        "--temps",
        "--favorite-color",
    )
    for string in expected_contents:
        assert string in captured.out


def test_args_full(config):
    """test good cli args"""
    conf = config(
        cli_args=[
            # fmt: off
            "--no-verbose",
            "--batch-size", "12345",
            "--input-files", "/tmp/one.txt",
            "--input-files", "/tmp/two.txt",
            "--input-files", "/tmp/three.txt",
            "--yn", "no",
            "--yn", "yes",
            "--temps", "212.0",
            "--temps", "98.6",
            "--temps", "32.0",
            "--favorite-color", "orange",
            # fmt: on
        ]
    )
    assert conf is not None
    assert conf.verbose is False
    assert conf.batch_size == 12345
    assert conf.input_files == ["/tmp/one.txt", "/tmp/two.txt", "/tmp/three.txt"]
    assert conf.yn == [False, True]
    assert conf.temps == [212.0, 98.6, 32.0]
    assert conf.favorite_color == "orange"


def test_args_bad_type(config, capsys):
    """test cli args with value that cannot be coerced into the correct type"""
    with pytest.raises(SystemExit):
        _ = config(
            cli_args=[
                # fmt: off
                "--batch-size", "xyz",
                # fmt: on
            ]
        )
    captured = capsys.readouterr()
    expected_content = "error: argument --batch-size: invalid int value: 'xyz'"
    assert expected_content in captured.err


def test_args_bad_value(config, capsys):
    """test cli args with value not in the list of available choices"""
    with pytest.raises(SystemExit):
        _ = config(
            cli_args=[
                # fmt: off
                "--favorite-color", "mauve",
                # fmt: on
            ]
        )
    captured = capsys.readouterr()
    expected_content = (
        "error: argument --favorite-color: invalid choice: 'mauve' "
        "(choose from 'blue', 'green', 'orange')"
    )
    assert expected_content in captured.err


def test_all_sources(config, temp_envvars, json_partial_good):
    """
    test all of the following in a single setup:
    * a value from defaults
    * a value from the json config
    * a value from envvars
    * a value from cli args
    """
    # default: verbose
    # json: favorite_color
    # envvars: batch_size
    # cli: input_files
    temp_envvars()
    os.environ["BATCH_SIZE"] = "28934"
    cli_args = [
        # fmt: off
        "--input-files", "/tmp/one.txt",
        "--input-files", "/tmp/two.txt",
        "--input-files", "/tmp/three.txt",
        # fmt: on
    ]
    conf = config(json_partial_good, True, cli_args=cli_args)
    assert conf is not None
    assert conf.verbose is False
    assert conf.batch_size == 28934
    assert conf.input_files == ["/tmp/one.txt", "/tmp/two.txt", "/tmp/three.txt"]
    assert conf.yn == []
    assert conf.temps == []
    assert conf.favorite_color == "green"
