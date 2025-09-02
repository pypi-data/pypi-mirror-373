""" The Input Package for Changelist Sort
"""
from changelist_data import load_storage_from_file_arguments

from changelist_sort.input.argument_parser import parse_arguments
from changelist_sort.input.input_data import InputData
from changelist_sort.sorting.sort_mode import SortMode
from changelist_sort.xml import load_sorting_config


def validate_input(args_list: list[str]) -> InputData:
    """ Validate the arguments and gather program input into InputData object.
 - Parses command line strings into Arguments data object.
 - Finds storage file and loads it into InputData as ChangelistDataStorage object.

**Parameters:**
 - args_list (list[str]): The input argument strings.

**Returns:**
 InputData - container for the program input.
    """
    arg_data = parse_arguments(args_list)
    return InputData(
        storage=load_storage_from_file_arguments(arg_data.changelists_path, arg_data.workspace_path),
        # Check the Argument Data flags to determine which SortMode to use.
        sort_mode=SortMode.SOURCESET if arg_data.sourceset_sort else SortMode.MODULE,
        remove_empty=arg_data.remove_empty,
        sorting_config=load_sorting_config(arg_data.sort_xml_path),
        generate_sort_xml=arg_data.generate_sort_xml,
    )