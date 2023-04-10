#!/usr/bin/env python3
"""
module for specifying configuration options as a class with typed members and
loading the configuration values from json config files, environment variables,
and command-line arguments
"""
# pylint: disable=too-many-arguments
import argparse
import json
import os
import re
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

# pylint: disable=invalid-name
OptType = TypeVar("OptType")
OptParserInput = Union[str, int, float, list]

empty_line = re.compile(r"^\s*([#].*|$)")


class OptionMetadata(NamedTuple):
    """
    OptionMetadata is a named tuple which encapsulates data captured by OptFunc
    instances
    """

    name: Optional[str]
    option_type: Optional[Any]
    default: Any
    doc: str
    required: bool
    parser: Optional[Callable[[OptParserInput], Any]]
    choices: Optional[Any]
    sep: str
    redact: bool


class BaseCfg:
    """
    BaseCfg is a base class for typed application configurations with
    automatic support for taking configuration data from config files,
    environment variables, and command-line arguments. Users of BaseCfg
    subclass basecfg.BaseCfg and add typed class attributes, defining
    them with basecfg.opt
    """

    _optmeta: List[OptionMetadata] = []
    _optmeta_reset: bool = True
    _options: Dict[str, OptionMetadata]
    _prog: Optional[str] = None
    _prog_description: Optional[str] = None
    _prog_epilog: Optional[str] = None
    _version: Optional[str] = None

    def __init__(
        self,
        json_config_path: Optional[str] = None,
        json_required=False,
        envfile_path: Optional[str] = None,
        envfile_required: bool = False,
        secrets_dir: str = "/run/secrets",
        cli_args: Optional[Sequence[str]] = None,
        prog: Optional[str] = None,
        prog_description: Optional[str] = None,
        prog_epilog: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        """
        Creates a new instance of the configuration class; all arguments are optional
        json_config_path [str]: the path to a json config file to parse
        json_required [bool]: if True an exception will be raised if the given json
            config file is missing
        cli_args List[str]: instead of using sys.argv, this list of arguments will be
            passed to the command-line argument processing routine
        prog [str]: sets the name of the program - used while printing usage
            documentation when the program is invoked with -h or --help
        prog_description [str]: describes what the program does - used while printing
            usage documentation when the program is invoked with -h or --help
        prog_epilog [str]: additional text appearing at the end of the usage
            documentation that is printed when the program is invoked with -h or --help
        """
        self._prog = prog
        self._prog_description = prog_description
        self._prog_epilog = prog_epilog
        self._version = version

        # step 1: enrich our metadata about the configuration options and load
        # default values. At this point we finally have the names of the fields
        # and are aware of their resolved type annotations.

        BaseCfg._optmeta_reset = True
        # copying the _optmeta list from a BaseCfg class attr to an attr of this subclass
        setattr(self.__class__, "_optmeta", BaseCfg._optmeta.copy())
        option_metadata = iter(self.__class__._optmeta)

        self._options = {}
        for key, val in self.__class__.__annotations__.items():
            self._options[key] = next(option_metadata)._replace(
                name=key,
                option_type=val,
            )

        # step 2: load config data from json config file
        if json_config_path:
            for key, val in self._parse_json_config(
                json_config_path, json_required
            ).items():
                setattr(self, key, val)

        # step 3: load config data from .env files
        if envfile_path:
            envfile_values = self._read_envfile(envfile_path, envfile_required)
            self._apply_dict(envfile_values)

        # step 4: load config data from environment variables
        self._apply_dict(self._read_envvars())

        # step 5: load config data from docker secrets
        self._apply_dict(
            {
                name: self._read_docker_secret(secret_path)
                for name, secret_path in self._list_docker_secrets(secrets_dir).items()
            }
        )

        # step 6: load config data from command-line arguments
        for key, val in self._parse_args(cli_args).items():
            if val is not None:
                setattr(self, key, val)

    def _parse_json_config(self, path: str, required: bool = False) -> Dict[str, Any]:
        """parses the configuration from the json file at the given path"""
        result: Dict[str, Any] = {}
        if not os.path.isfile(path):
            if required:
                raise RuntimeError(f"required json config file {path} was not found")
            # no file, not required
            return result
        with open(path, "rt", encoding="utf8") as json_fp:
            for key, val in json.load(json_fp).items():
                if key not in self._options:
                    # in the future we may want to optionally raise an
                    # exception here
                    continue
                option = self._options[key]
                option_type = self._base_type(option.option_type)

                # check json value types against the supported types
                val_type = type(val).__name__

                coercions: Dict[str, Callable[[Any], Any]] = {
                    "bool": bool,
                    "float": float,
                    "int": int,
                    "str": str,
                    "List[bool]": self._bool_list,
                    "List[float]": self._float_list,
                    "List[int]": self._int_list,
                    "List[str]": self._str_list,
                }

                coerced_value = val
                if option.parser:
                    coerced_value = option.parser(val)
                elif val_type != option_type:
                    if val_type == "list":
                        if option_type not in coercions:
                            raise TypeError(
                                f"{key}: unsupported list type {option_type}"
                            )
                    if option_type not in coercions:
                        raise TypeError(f"{key}: unsupported value type {option_type}")
                    try:
                        coerced_value = coercions[option_type](val)
                    except ValueError:
                        raise TypeError(
                            f"{key}: unsupported value type {val_type}"
                        ) from None

                if option.choices:
                    if coerced_value not in option.choices:
                        raise ValueError(
                            f'{key}: value "{coerced_value}" not in specified '
                            f"option choices ({str(option.choices)})"
                        )
                result[key] = coerced_value

        return result

    def _bool_list(self, input_list: List[Any]) -> List[bool]:
        """converts a list of unknown type into a list of bool values"""
        return [bool(x) for x in input_list]

    def _float_list(self, input_list: List[Any]) -> List[float]:
        """converts a list of unknown type into a list of float values"""
        return [float(x) for x in input_list]

    def _int_list(self, input_list: List[Any]) -> List[int]:
        """converts a list of unknown type into a list of int values"""
        return [int(x) for x in input_list]

    def _str_list(self, input_list: List[Any]) -> List[str]:
        """converts a list of unknown type into a list of str values"""
        return [str(x) for x in input_list]

    def _keys(self) -> Sequence[str]:
        """return a list of keys in this configuration"""
        return [key for key in self._options if not key.startswith("_")]

    def _parse_args(self, cli_args: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """generate an args parser and call it"""
        argp = argparse.ArgumentParser(
            prog=self._prog,
            description=self._prog_description,
            epilog=self._prog_epilog,
        )
        if self._version:
            argp.add_argument("--version", action="version", version=self._version)
        for optname, option in self._options.items():
            arg_name = "--" + optname.replace("_", "-")
            option_type = self._base_type(option.option_type)

            # use this for as little as possible (because it doesn't get type checked)
            # it could be good to switch to TypedDict for this
            arg_config: Dict[str, Any] = {"action": "store"}

            if option.parser:
                arg_config["type"] = option.parser
            elif option_type == "bool":
                arg_config["action"] = argparse.BooleanOptionalAction
            elif option_type == "int":
                arg_config["type"] = int
            elif option_type == "float":
                arg_config["type"] = float
            elif option_type == "List[str]":
                arg_config["action"] = "append"
            elif option_type == "List[int]":
                arg_config["action"] = "append"
                arg_config["type"] = int
            elif option_type == "List[float]":
                arg_config["action"] = "append"
                arg_config["type"] = float
            elif option_type == "List[bool]":
                arg_config["action"] = "append"
                arg_config["type"] = self._parse_bool

            argp.add_argument(
                arg_name,
                dest=optname,
                help=option.doc + f" (default {str(option.default)})",
                required=False,
                choices=option.choices,
                **arg_config,
            )

        return vars(argp.parse_args(args=cli_args))

    def _read_envvars(self) -> Dict[str, str]:
        """read environment variables for configuration values"""
        result: Dict[str, str] = {}

        for optname in self._options:
            for envvar_name in (optname.upper(), optname):
                if envvar_name in os.environ:
                    result[optname] = os.environ[envvar_name]
                    break
        return result

    def _apply_dict(self, inputs: Dict[str, str]) -> bool:
        """
        given a dict mapping option names to string input values, convert the values to
        the selected type
        """
        # pylint: disable=too-many-branches
        for optname, input_value in inputs.items():
            option = self._options[optname]
            option_type = self._base_type(option.option_type)

            coerced_value: Any = input_value
            if option.parser:
                coerced_value = option.parser(input_value)
            elif option_type == "str":
                coerced_value = input_value
            elif option_type == "bool":
                coerced_value = self._parse_bool(input_value)
            elif option_type == "int":
                coerced_value = int(input_value)
            elif option_type == "float":
                coerced_value = float(input_value)
            elif option_type == "List[str]":
                coerced_value = input_value.split(option.sep)
            elif option_type == "List[int]":
                coerced_value = [int(n) for n in input_value.split(option.sep)]
            elif option_type == "List[float]":
                coerced_value = [float(f) for f in input_value.split(option.sep)]
            elif option_type == "List[bool]":
                coerced_value = [
                    self._parse_bool(s) for s in input_value.split(option.sep)
                ]
            else:
                raise ValueError(
                    f"Don't know how to parse type {option.option_type} "
                    f"({option_type})"
                )

            if option.choices:
                if coerced_value not in option.choices:
                    raise ValueError(
                        f"{optname} (envvar: {input_value}): "
                        f'value "{coerced_value}" not in specified '
                        f"choices list ({str(option.choices)})"
                    )

            setattr(self, optname, coerced_value)

        return True

    @staticmethod
    def _read_envfile(path: str, required: bool = False) -> Dict[str, str]:
        """
        parse entries in an environment file (aka .env) - the format supported
        is described in the "docker run" (NOT compose) documentation. Notably
        no quotation marks nor multi-line values are supported and comments are
        only valid at the beginning of the line
        """
        result: Dict[str, str] = {}
        try:
            dotenvfh = open(path, "rt", encoding="utf8")
        except FileNotFoundError as fnf:
            if not required:
                return result
            raise fnf from None
        with dotenvfh as dotenv:
            for i, line in enumerate(dotenv.readlines()):
                if empty_line.match(line):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f'envfile parsing error; file:"{path}" line:{i}; data line '
                        f'contains no "-" character'
                    )
                key, value = line.split("=", 1)
                result[key.lower().strip()] = value.strip()
        return result

    @staticmethod
    def _list_docker_secrets(
        secrets_dir: str = "/run/secrets/",
    ) -> Dict[str, str]:
        """
        return a dict mapping names to full paths for docker secrets found
        on disk
        """
        result: Dict[str, str] = {}
        try:
            dircontents = os.listdir(secrets_dir)
        except FileNotFoundError:
            return result
        for name in dircontents:
            if name.startswith("."):
                continue
            path = os.path.abspath(os.path.join(secrets_dir, name))
            if not os.path.isfile(path):
                continue
            result[name] = path
        return result

    @staticmethod
    def _read_docker_secret(
        path: str,
        open_mode: str = "rt",
        encoding: Optional[str] = "utf-8",
        strip_whitespace: bool = True,
    ) -> str:
        """
        open the secrets directory, look for a file with the given name; return its
        contents, optionally stripping whitespace from the value
        """
        with open(path, open_mode, encoding=encoding) as secret:
            contents = secret.read()
        if strip_whitespace:
            return contents.strip()
        return contents

    def _base_type(self, type_spec: Any) -> str:
        """returns a string representing the type of object"""
        # print(
        #     f"spec: {type_spec}; "
        #     f"name: {type_spec.__name__}; "
        #     f"origin: {get_origin(type_spec)}; "
        #     f"args: {get_args(type_spec)}"
        # )
        result = (
            type_spec.__name__ if hasattr(type_spec, "__name__") else repr(type_spec)
        )
        origin = get_origin(type_spec)
        args = get_args(type_spec)
        if origin == Union and len(args) == 2 and args[1] == type(None):  # noqa
            # Optional[thing] where thing is in args[0]
            return self._base_type(args[0])
        if origin == list and len(args) == 1:
            if args[0] in (str, int, float, bool):
                result = f"List[{args[0].__name__}]"

        # print(f"result is: {result}")
        return result

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """evaluates the string value in a boolean context and returns the result"""
        return value.lower().strip() in ("1", "enable", "on", "true", "t", "y", "yes")

    def __getitem__(self, key):
        """returns the value for the given configuration variable"""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f'key "{key}" not found') from None

    def __len__(self):
        """returns the number of configuration options in the class"""
        return len(self._options)

    def __iter__(self):
        """returns keys iterator"""
        return iter(self._options.keys())


def opt(
    default: OptType,
    doc: str,
    required: bool = False,
    parser: Optional[Callable[[OptParserInput], OptType]] = None,
    choices: Optional[Sequence[OptType]] = None,
    sep: str = ",",
    redact: bool = False,
) -> OptType:
    """
    opt captures data related to a BaseCfg option and returns the default
    the annotated type of the return value is determined by the type of the
    given default argument
    """
    # pylint: disable=protected-access
    if BaseCfg._optmeta_reset:
        BaseCfg._optmeta = []
        BaseCfg._optmeta_reset = False
    BaseCfg._optmeta.append(
        OptionMetadata(None, None, default, doc, required, parser, choices, sep, redact)
    )
    return default
