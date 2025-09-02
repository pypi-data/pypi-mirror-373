""" Defines and Validates Argument Syntax.
 - Encapsulates Argument Parser.
 - Returns Argument Data, the args provided by the User.
"""
from argparse import ArgumentParser
from sys import exit
from typing import Optional

from changelist_init.input.argument_data import ArgumentData
from changelist_init.input.string_validation import validate_name


def parse_arguments(
    args: Optional[list[str]] = None
) -> ArgumentData:
    """ Parse command line arguments.

**Parameters:**
 - args: A list of argument strings.

**Returns:**
 ArgumentData : Container for Valid Argument Data.
    """
    if args is None or len(args) == 0:
        return ArgumentData()
    # Initialize the Parser and Parse Immediately
    try:
        parsed_args = _define_arguments().parse_args(args)
    except SystemExit:
        exit("Unable to Parse Arguments.")
    return _validate_arguments(parsed_args)


def _validate_arguments(
    parsed_args,
) -> ArgumentData:
    """ Checks the values received from the ArgParser.
- Uses Validate Name method from StringValidation.

**Parameters:**
 - parsed_args : The object returned by ArgumentParser.

**Returns:**
 ArgumentData - A DataClass of syntactically correct arguments.
    """
    if (changelists_file := parsed_args.changelists_file) is not None:
        if not validate_name(changelists_file):
            exit("The Changelists File name was invalid.")
    if (workspace_file := parsed_args.workspace_file) is not None:
        if not validate_name(workspace_file):
            exit("The Workspace File name was invalid.")
    return ArgumentData(
        changelists_file=parsed_args.changelists_file,
        workspace_file=parsed_args.workspace_file,
        include_untracked=parsed_args.include_untracked,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
 - Sets Required/Optional Arguments and Flags.

**Returns:**
 argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description="Initializes and updates the Changelist data storage file with git status information.",
    )
    parser.color = True
    # Optional Arguments
    parser.add_argument(
        '--changelists_file',
        type=str,
        default=None,
        help='The Path to the Changelists Data File. Searches default paths if none.',
    )
    parser.add_argument(
        '--workspace_file',
        type=str,
        default=None,
        help='The Path to the Workspace Data File. Searches default paths if none.',
    )
    parser.add_argument(
        "--include_untracked", "-u",
        action='store_true',
        default=False,
        help='The option to include untracked files in changelists.',
    )
    return parser
