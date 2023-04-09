#!/usr/bin/env python3
""" general source tests """
import os


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
