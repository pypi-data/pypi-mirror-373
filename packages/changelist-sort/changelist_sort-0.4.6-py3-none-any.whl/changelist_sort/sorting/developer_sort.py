""" Sort With Developer's SortingChangelist FilePatterns.
"""
from changelist_sort.change_data import ChangeData
from changelist_sort.changelist_map import ChangelistMap
from changelist_sort.list_key import ListKey
from changelist_sort.sorting import file_sort, module_sort, sorting_changelist
from changelist_sort.sorting.sorting_changelist import SortingChangelist


def sort_file_by_developer(
    cl_map: ChangelistMap,
    file: ChangeData,
    sorting_config: list[SortingChangelist] | None,
) -> bool:
    """ Apply the SortingChangelist FilePattern Settings to Sort a single File into the Changelist Map.
        - Filters Patterns by matching ModuleType before checking files.
        - Fallback to Module Sort
    """
    if sorting_config is None:
        return module_sort.sort_file_by_module(cl_map, file)
    # Filter Sorting Changelists
    filtered_scl_patterns = sorting_changelist.filter_by_module(
        file_sort.get_module_type(file),
        sorting_config,
    )
    # Check Changelists in Order
    for scl_pattern in filtered_scl_patterns:
        if scl_pattern.check_file(file): # Pattern Matched.
            # Search Map. Add File to Changelist.
            if (cl := cl_map.search(scl_pattern.list_key.key)) is not None:
                cl.changes.append(file)
                return True
            # Create Changelist. Add File to Changelist
            cl_map.create_changelist(scl_pattern.list_key.changelist_name).changes.append(file)
            return True
    # Fallback to Module Sort
    return module_sort.sort_file_by_module(cl_map, file)


def is_sorted_by_developer(
    changelist_key: ListKey,
    file: ChangeData,
    sorting_config: list[SortingChangelist] | None,
) -> bool:
    """ Determines if this File matches the ChangeList Key or Name.
        - Finds the First SortingCL FilePattern match
        - Fallback to Module Sort
    """
    if sorting_config is None:
        return module_sort.is_sorted_by_module(changelist_key, file)
    # Filter Sorting Changelists
    filtered_scl_patterns = sorting_changelist.filter_by_module(
        file_sort.get_module_type(file),
        sorting_config,
    )
    # Check Changelists in Order
    for scl_pattern in filtered_scl_patterns:
        if scl_pattern.check_file(file): # Pattern Matched
            if scl_pattern.list_key.key == changelist_key.key or\
                scl_pattern.list_key.changelist_name == changelist_key.changelist_name:
                return True
            return False # File could be higher in the Sorting order
    # Fallback to Module Sort
    return module_sort.is_sorted_by_module(changelist_key, file)
