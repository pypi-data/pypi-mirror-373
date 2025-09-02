""" Input Sub-Package Methods.
"""
from changelist_data import load_storage_from_file_arguments

from changelist_init.input.argument_parser import parse_arguments
from changelist_init.input.input_data import InputData


def validate_input(
    arguments: list[str],
) -> InputData:
    """ Parse and Validate the Arguments, and return Input Data.

**Parameters:**
 - arguments (list[str]): The arguments received by the program.

**Returns:**
 InputData - The InputData containing the program inputs. The other packages will process the data from here.
    """
    arg_data = parse_arguments(arguments)
    return InputData(
        storage=load_storage_from_file_arguments(arg_data.changelists_file, arg_data.workspace_file),
        include_untracked=arg_data.include_untracked,
    )
