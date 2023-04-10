#!/usr/bin/env python3
""" test configuration via command-line arguments """
import pytest


def test_args_help(config, capsys):
    """test -h support in argparser"""
    with pytest.raises(SystemExit):
        _ = config(cli_args=["-h"], version="98.76.54")
    captured = capsys.readouterr()
    expected_contents = (
        "--help",
        "--verbose",
        "--batch-size",
        "--input-files",
        "--yn",
        "--temps",
        "--favorite-color",
        "--version",
    )
    for string in expected_contents:
        assert string in captured.out


def test_args_version(config, capsys):
    """verify that setting version on the constructor enables --version functionality"""
    with pytest.raises(SystemExit):
        _ = config(cli_args=["--version"], version="98.76.54")
    captured = capsys.readouterr()
    expected_content = "98.76.54\n"
    assert expected_content == captured.out


def test_args_version_unset(config, capsys):
    """
    verify that --version functionality is unimplemented if version is not set on the
    constructor
    """
    with pytest.raises(SystemExit):
        _ = config(cli_args=["--version"])
    captured = capsys.readouterr()
    expected_content = "error: unrecognized arguments: --version"
    assert expected_content in captured.err


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
            "--favorite-color", "Orange",
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
