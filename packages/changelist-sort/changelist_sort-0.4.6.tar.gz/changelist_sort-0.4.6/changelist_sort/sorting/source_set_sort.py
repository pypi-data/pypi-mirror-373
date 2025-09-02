""" Sorting By Gradle Module Source Set.
    - Builds on the Module Sort, with additional subcategories for Gradle Source Sets.
"""
from changelist_sort.change_data import ChangeData
from changelist_sort.changelist_map import ChangelistMap
from changelist_sort.list_key import ListKey
from changelist_sort.sorting import file_sort, module_sort
from changelist_sort.sorting.module_type import ModuleType
from changelist_sort.sorting.string_operations import capitalize_words, replace_underscores, split_words_on_capitals


def sort_by_source_set(
    cl_map: ChangelistMap,
    file: ChangeData,
) -> bool:
    """ Sort files into Changelists by Source Set.
        - Is Based on Module Sort. Should defer to Module Sort where possible.

    Parameters:
    - cl_map (ChangelistMap): The Map of Changelists to sort into.
    - file (ChangeData): The File change data to be sorted.

    Returns:
    bool - True when the operation succeeds.
    """
    if file_sort.get_module_type(file) == ModuleType.MODULE:
        # Get SourceSet Name
        if (source_set_name := _get_source_set_name(file.sort_path)) is not None:
            file_module = file_sort.get_module_name(file)
            # Merge Module and SourceSet into a Sorting Key
            sort_key = f"{file_module}{source_set_name.lower()}"
            if (cl := cl_map.search(sort_key)) is not None:
                cl.changes.append(file)
                return True
            # Create a new Changelist for this SourceSet
            cl_map.create_changelist(
                capitalize_words(replace_underscores(
                    f"{file_module} {split_words_on_capitals(source_set_name)}"
                ))
            ).changes.append(file)
            return True
    # Fallback to ModuleSort
    return module_sort.sort_file_by_module(cl_map, file)


def is_sorted_by_source_set(
    cl_key: ListKey,
    file: ChangeData,
) -> bool:
    """ Determine whether this file belongs in the given Changelist.
        - Applies Special Module, and Directory equivalencies.

    Parameters:
    - changelist_name (str): The name of the Changelist, used to determine if the file is sorted.
    - file (ChangeData): The File to compare against the Changelist name.

    Returns:
    bool - Whether this file belongs in this Changelist according to Module sort logic.
    """
    if file_sort.get_module_type(file) == ModuleType.MODULE:
        # Get SourceSet Name
        if (source_set_name := _get_source_set_name(file.sort_path)) is not None:
            file_module = file_sort.get_module_name(file)
            # Merge Module and SourceSet into a Sorting Key
            if cl_key.key.startswith(f"{file_module}{source_set_name.lower()}"):
                return True
            return False
    return module_sort.is_sorted_by_module(cl_key, file)


def _get_source_set_name(path: str | None) -> str | None:
    """ Determine the Source Set of the file path, if possible.

    Parameters:
    - path (str): The file path to obtain the Source Set name from.

    Returns:
    str | None - The SourceSet name, or None if not applicable.
    """
    if path is None:
        return None
    # Find the Source Dir
    if (src_start_idx := path.find('/src/') + 5) < 5:
        return None
    # Find the next dir slash
    if (src_end_idx := path.find('/', src_start_idx)) <= src_start_idx:
        return None
    return path[src_start_idx:src_end_idx]
