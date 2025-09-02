""" Defines and Validates Argument Syntax.
 - Encapsulates Argument Parser.
 - Returns Argument Data, the args provided by the User.
"""
from argparse import ArgumentParser
from sys import exit
from typing import Optional

from changelist_foci.input.argument_data import ArgumentData
from changelist_foci.input.string_validation import validate_name


def parse_arguments(args: Optional[list[str]] = None) -> ArgumentData:
    """ Parse command line arguments.
 - Returns Default Argument Data when input is empty.

**Parameters:**
 - args: A list of argument strings.

 **Returns:**
 ArgumentData : Container for Valid Argument Data.
    """
    if args is None:
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
    # Validate Changelist Name
    if (changelist := parsed_args.changelist) is not None:
        if not validate_name(changelist):
            exit("The ChangeList Name was invalid.")
    # Check Changelist Path Argument
    if (cl_path := parsed_args.changelists_file) is not None:
        if not validate_name(cl_path):
            exit("changelists_file argument invalid.")
    # Check Workspace Argument
    if (path := parsed_args.workspace_file) is not None:
        if not validate_name(path):
            exit("workspace_path argument invalid.")
    #
    return ArgumentData(
        changelist_name=changelist,
        changelists_path=cl_path,
        workspace_path=path,
        full_path=parsed_args.full_path,
        no_file_ext=parsed_args.no_file_ext,
        filename=parsed_args.filename,
        all_changes=parsed_args.all_changes,
        comment=parsed_args.comment,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
 - Sets Required/Optional Arguments and Flags.

**Returns:**
 argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description="ChangeList FOCI (File Oriented Commit Information).",
    )
    # Introduced in Version 3.14: Color, SuggestOnError.
    parser.color = True
    parser.suggest_on_error = True
    # Optional Arguments
    parser.add_argument(
        '--changelist',
        type=str,
        default=None,
        help='The Name of the ChangeList to focus on. Uses Active Changelist by default.'
    )
    parser.add_argument(
        '--changelists_file',
        type=str,
        default=None,
        help='The Path to the Changelists file. Searches default path if not given.',
    )
    parser.add_argument(
        '--workspace_file', '--workspace',
        type=str,
        default=None,
        help='The Path to the workspace file. Searches default path if not given.',
    )
    parser.add_argument(
        '--full-path',
        action='store_true',
        default=False,
        help='Display the Full File Path.',
    )
    parser.add_argument(
        '--no-file-ext', '-x',
        action='store_true',
        default=False,
        help='Remove File Extension from File paths.',
    )
    parser.add_argument(
        '--filename', '-f',
        action='store_true',
        default=False,
        help='Remove Parent Directories from File paths.',
    )
    parser.add_argument(
        '--all-changes', '-a',
        action='store_true',
        default=False,
        help='Output All Changes in any Changelist.',
    )
    parser.add_argument(
        '--comment', '-c',
        action='store_true',
        default=False,
        help='Insert FOCI into Changelist Workspace Comments instead of printing.',
    )
    return parser