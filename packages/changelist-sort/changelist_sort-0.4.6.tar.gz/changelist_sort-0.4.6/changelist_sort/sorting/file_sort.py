""" Methods of Sorting Change Data.
    This Module aims to make Change Data easy to sort.
"""
from changelist_sort.change_data import ChangeData
from changelist_sort.sorting.module_type import ModuleType

_GRADLE_FILE_SUFFIXES = ('gradle', 'gradle.kts', 'properties')


def get_module_name(data: ChangeData) -> str | None:
    """
    Obtain the name of the module from the File path.
    """
    module_type = get_module_type(data)
    if module_type is None:
        return None
    if module_type == ModuleType.ROOT:
        return 'root'
    if module_type == ModuleType.GRADLE:
        return 'gradle'
    return data.first_dir.lower().lstrip('.')


def get_module_type(file: ChangeData) -> ModuleType | None:
    """
    Determine the ModuleType of the File.
    """
    if file.first_dir is None:
        if file.sort_path is None:
            return None
        if file.file_ext in _GRADLE_FILE_SUFFIXES:
            return ModuleType.GRADLE
        return ModuleType.ROOT
    if file.first_dir == 'gradle':
        return ModuleType.GRADLE
    if file.first_dir.startswith('.'):
        return ModuleType.HIDDEN
    if file.file_ext in _GRADLE_FILE_SUFFIXES:
        return ModuleType.GRADLE
    return ModuleType.MODULE
