""" Sorting By Module.
    An option of SortMode.
"""
from changelist_sort.list_key import ListKey
from changelist_sort.sorting import file_sort
from changelist_sort.change_data import ChangeData
from changelist_sort.changelist_map import ChangelistMap
from changelist_sort.sorting.module_type import ModuleType
from changelist_sort.sorting.string_operations import capitalize_words, replace_underscores


MODULE_ROOT_CL_TUPLE = (
    ListKey('projectroot', 'Project Root'),
    ListKey('root', 'Project Root'),
)

MODULE_GRADLE_CL_TUPLE = (
    ListKey('buildupdates', 'Build Updates'),
    ListKey('gradle', 'Build Updates'),
)


def get_module_keys(module_type: ModuleType) -> tuple[str, ...]:
    """
    Obtain a tuple containing the Keys for the Changelists.

    Parameters:
    - module_type (ModuleType): The type of Module.

    Returns
    tuple[str] - a tuple containing keys to lists of a given type of module.
    """
    if module_type == ModuleType.ROOT:
        return tuple(x.key for x in MODULE_ROOT_CL_TUPLE)
    elif module_type == ModuleType.GRADLE:
        return tuple(x.key for x in MODULE_GRADLE_CL_TUPLE)
    else:
        return tuple()


def sort_file_by_module(
    cl_map: ChangelistMap,
    file: ChangeData,
) -> bool:
    """
    Sort files into Changelists by Module.

    Parameters:
    - cl_map (ChangelistMap): The Map of Changelists to sort into.
    - file (ChangeData): The File change data to be sorted.

    Returns:
    bool - True when the operation succeeds.
    """
    if (module_type := file_sort.get_module_type(file)) is None:
        return False
    if module_type == ModuleType.ROOT:
        return _sort_root_module(cl_map, file)
    elif module_type == ModuleType.GRADLE:
        return _sort_gradle_module(cl_map, file)
    else:
        return _sort_module(cl_map, file)


def is_sorted_by_module(
    cl_key: ListKey,
    file: ChangeData,
) -> bool:
    """
    Determine whether this file belongs in the given Changelist.
        Applies Special Module, and Directory equivalencies.

    Parameters:
    - changelist_name (str): The name of the Changelist, used to determine if the file is sorted.
    - file (ChangeData): The File to compare against the Changelist name.

    Returns:
    bool - Whether this file belongs in this Changelist according to Module sort logic.
    """
    if (module_type := file_sort.get_module_type(file)) == ModuleType.ROOT:
        if cl_key.key.startswith(get_module_keys(ModuleType.ROOT)):
            return True
        # File Extension Checks
        if file.file_ext is None:
            # No FileExt Should Sort into Root CL
            return False
        # Check for Gradle FileExt
        return file.file_ext.endswith(
            file_sort._GRADLE_FILE_SUFFIXES
        ) and cl_key.key.startswith(
            get_module_keys(ModuleType.GRADLE)
        )
    if module_type == ModuleType.GRADLE:
        return cl_key.key.startswith(get_module_keys(ModuleType.GRADLE))
    # Starts with or Equals
    return cl_key.key.startswith(
        file_sort.get_module_name(file)
    )


def _sort_root_module(
    cl_map: ChangelistMap,
    file: ChangeData,
) -> bool:
    # Find CL
    for module_cl in MODULE_ROOT_CL_TUPLE:
        if (existing_cl := cl_map.search(module_cl.key)) is not None:
            existing_cl.changes.append(file)
            return True
    # Create New ChangeList and Append File
    cl_map.create_changelist(
        MODULE_ROOT_CL_TUPLE[0],
    ).changes.append(file)
    return True


def _sort_gradle_module(
    cl_map: ChangelistMap,
    file: ChangeData,
) -> bool:
    # Find CL
    for module_cl in MODULE_GRADLE_CL_TUPLE:
        if (existing_cl := cl_map.search(module_cl.key)) is not None:
            existing_cl.changes.append(file)
            return True
    # Create New ChangeList and Append File
    cl_map.create_changelist(
        MODULE_GRADLE_CL_TUPLE[0]
    ).changes.append(file)
    return True


def _sort_module(
    cl_map: ChangelistMap,
    file: ChangeData,
) -> bool:
    # Get Module Name from File Path data
    if (file_module := file_sort.get_module_name(file)) is None or len(file_module) == 0:
        return False
    if (cl := cl_map.search(file_module)) is not None:
        cl.changes.append(file)
        return True
    # Create Changelist and Append File
    cl_map.create_changelist(
        capitalize_words(replace_underscores(file_module))
    ).changes.append(file)
    return True
