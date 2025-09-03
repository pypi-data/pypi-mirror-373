"""
    script utility, allows the use of the app's context (database, models ...)
    from within command line calls
"""
import logging
import sys
import argparse

from typing import TypeVar, Union, Callable

from docopt import docopt
from pyramid.paster import bootstrap
from transaction import commit
from pyramid.paster import setup_logging
from caerp.utils import ascii


def command(func, doc):
    """
    Usefull function to wrap command line scripts using docopt lib

    /!\ if starting to use this commande, you may want to use argparse_command() instead.
    (docopt is deprecated).

    If at any time, this commande becomes unused, remove it, and remove docopt
    from requirements.
    """
    logging.basicConfig()
    args = docopt(doc)
    pyramid_env = bootstrap(args["<config_uri>"])
    setup_logging(args["<config_uri>"])
    try:
        func(args, pyramid_env)
    finally:
        pyramid_env["closer"]()
    commit()
    return 0


def argparse_command(func, argparser: argparse.ArgumentParser, pyramid_env=None):
    """
    Wrap command line scripts, using argparse builtin module
    """
    logging.basicConfig()
    args = argparser.parse_args(sys.argv[1:])
    # L'app pyramid peut être bootstrappée avant dans le cas d'caerp-admin
    # par exemple
    if pyramid_env is None:
        pyramid_env = bootstrap(args.config_uri)
    setup_logging(args.config_uri)
    try:
        func(args, pyramid_env)
    finally:
        pyramid_env["closer"]()
    commit()
    return 0


def get_argument_value(arguments, key, default=None):
    """
    Return the value for an argument named key in arguments or default

    :param dict arguments: The cmd line arguments returned by docopt
    :param str key: The key we look for (type => --type)
    :param str default: The default value (default None)

    :returns: The value or default
    :rtype: str
    """
    val = arguments.get("<%s>" % key)
    if not val:
        val = default

    return ascii.force_unicode(val)


def get_value(arguments, key, default=None):
    """
    Return the value of an option named key in arguments or default

    :param dict arguments: The cmd line arguments returned by docopt
    :param str key: The key we look for (type => --type)
    :param str default: The default value (default None)

    :returns: The value or default
    :rtype: str
    """
    if not key.startswith("--"):
        key = "--%s" % key
    val = arguments.get(key)
    if not val:
        val = default

    return ascii.force_unicode(val)


class AbstractCommand:
    """
    Docstring will be used as CLI doc
    """

    name = None

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Adds arguments to the subcmd parser

        no-op if no special arguments is used for the subcmd

        :param parser: the sub-command parser already added to main CMD subparsers
        """
        return None

    @staticmethod
    def __call__(arguments: argparse.Namespace, env: dict):
        raise NotImplementedError


CommandClassType = TypeVar("CommandClassType", bound=AbstractCommand)


class CommandRegistry:
    # NB : Les classes filles doivent avoir redéfinir ces deux listes
    BASE_COMMANDS = []
    EXTRA_COMMANDS = []
    description = """Description should be set on subclass"""

    @classmethod
    def _get_all_commands(cls):
        return cls.EXTRA_COMMANDS + cls.BASE_COMMANDS

    @classmethod
    def add_function(cls, command_class: CommandClassType) -> None:
        cls.EXTRA_COMMANDS.append(command_class)

    @classmethod
    def get_command(cls, name: str) -> Union[Callable[[dict, dict], None], None]:
        """
        :param name: the command name
        :returns None if no known command is mentioned in arguments
        """
        for cmd in cls._get_all_commands():
            if cmd.name == name:
                return cmd()

    @classmethod
    def get_argument_parser(cls):
        parser = argparse.ArgumentParser(description="CAERP administration tool")
        parser.add_argument("config_uri")

        subparsers = parser.add_subparsers(dest="subcommand", required=True)
        for cmd in cls._get_all_commands():
            description = cmd.__doc__.strip()
            subparser = subparsers.add_parser(cmd.name, description=description)
            cmd.add_arguments(subparser)

        return parser
