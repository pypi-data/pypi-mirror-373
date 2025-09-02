""" Developer Changelist Settings and Methods
"""
from dataclasses import dataclass

from changelist_sort.change_data import ChangeData
from changelist_sort.list_key import ListKey
from changelist_sort.sorting.module_type import ModuleType
from changelist_sort.sorting.sorting_file_pattern import SortingFilePattern


@dataclass(frozen=True)
class SortingChangelist:
    """ A Changelist data class designed for sorting.

    Parameters:
    - list_key (ListKey): The Key and Name of the Changelist.
    - file_patterns (list[SortingFilePattern]): The FilePatterns
    - module_type (ModuleType): The Type of Module to match Files with. None will allow matching with all modules.
    """
    list_key: ListKey
    file_patterns: list[SortingFilePattern]
    module_type: ModuleType | None = None

    def check_file(self, file: ChangeData) -> bool:
        """ Determine if the File can be added to this Changelist.
            - If the FilePatterns are empty, always returns False.

        Parameters:
        - file (ChangeData): The ChangeData of the File to pattern match.

        Returns:
        True if the File matches all patterns in this Changelist.
        """
        if len(self.file_patterns) == 0:
            return False
        for fp in self.file_patterns:
            if not fp.check_file(file):
                return False
        return True


def filter_by_module(
    module_type: ModuleType | None,
    sorting_cl_list: list[SortingChangelist],
) -> list[SortingChangelist]:
    """ Filter Sorting Changelists by ModuleType.

    This function filters a list of SortingChangelists based on the provided `module_type` argument.
    - SortingCL with a None ModuleType always pass through the filter. This is necessary to preserve file pattern order.
    - When None is passed as ModuleType argument, only SortingCL with None ModuleType pass through.

    Parameters:
    - module_type (ModuleType | None): The target module type to filter by. If None, only SortingChangelists with a None ModuleType will be included.
    - sorting_cl_list (list[SortingChangelist]): The list of SortingChangelists to filter.

    Returns:
    list[SortingChangelist]: A new list containing the filtered SortingChangelists. May be empty.
    """
    if sorting_cl_list is None or len(sorting_cl_list) == 0:
        return []
    if module_type is None:
        iterable = filter(
            lambda scl: scl.module_type is None,
            sorting_cl_list
        )
    else:
        iterable = filter(
            lambda scl: scl.module_type is None or scl.module_type == module_type,
            sorting_cl_list
        )
    return list(iterable)
