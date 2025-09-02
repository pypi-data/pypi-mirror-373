""" The Input Package level methods.
"""
from pathlib import Path
from sys import exit

from changelist_data import storage

from changelist_foci.format_options import FormatOptions
from changelist_foci.input.argument_data import ArgumentData
from changelist_foci.input.argument_parser import parse_arguments
from changelist_foci.input.input_data import InputData
from changelist_foci.input.string_validation import validate_name


def validate_input(
    arguments: list[str],
) -> InputData:
    """ Given the Command Line Arguments, obtain the InputData.
 1. Parse arguments with argument parser
 2. Check File Arguments, read Storage
 3. Return Structured Input Data

**Parameters:**
 - arguments (list[str]): The Command Line Arguments received by the program.
    
**Returns:**
 InputData - The formatted InputData.
    """
    arg_data = parse_arguments(arguments)
    return InputData(
        changelists=(cl_data_storage := _load_storage(arg_data.changelists_path, arg_data.workspace_path)).generate_changelists(),
        changelist_name=arg_data.changelist_name,
        format_options=_extract_format_options(arg_data),
        all_changes=arg_data.all_changes,
        changelist_data_storage=cl_data_storage if arg_data.comment else None,
    )


def _load_storage(
    changelists_file: str | None,
    workspace_file: str | None,
) -> storage.ChangelistDataStorage:
    """ Load the Changelist Data Storage access object.

**Parameters:**
 - changelists_file (str?): A string path to the Changelists file, if specified.
 - workspace_file (str?): A string path to the Workspace file, if specified.

**Returns:**
 ChangelistDataStorage - The Data Storage Access object.
    """
    if isinstance(changelists_file, str) and isinstance(workspace_file, str):
        exit("Cannot use two Data Files!")
    if validate_name(changelists_file):
        return storage.load_storage(
            storage.storage_type.StorageType.CHANGELISTS,
            Path(changelists_file)
        )
    elif validate_name(workspace_file):
        return storage.load_storage(
            storage.storage_type.StorageType.WORKSPACE,
            Path(workspace_file)
        )
    else:
        return storage.load_storage()


def _extract_format_options(
    data: ArgumentData,
) -> FormatOptions:
    # Map Property names
    return FormatOptions(
        full_path=data.full_path,
        no_file_ext=data.no_file_ext,
        file_name=data.filename,
    )