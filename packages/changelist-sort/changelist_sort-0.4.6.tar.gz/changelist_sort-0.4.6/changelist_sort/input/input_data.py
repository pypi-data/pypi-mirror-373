""" Valid Input Data Class.
"""
from dataclasses import dataclass, field

from changelist_data.storage import ChangelistDataStorage

from changelist_sort.sorting.sort_mode import SortMode
from changelist_sort.sorting.sorting_changelist import SortingChangelist


@dataclass(frozen=True)
class InputData:
    """ A Data Class Containing Program Input.

**Fields:**
 - storage (ChangelistDataStorage): The Changelist Data Storage.
 - sort_mode (SortMode): The selected Sorting Mode enum value.
 - remove_empty (bool): Whether to remove empty changelists after sort.
 - sorting_config (list[SortingChangelist]?): The sorting configuration data, or None.
 - generate_sort_xml (bool): Flag to create a Sort XML file for the project changelists.
    """
    storage: ChangelistDataStorage
    sort_mode: SortMode = SortMode.MODULE
    remove_empty: bool = False
    sorting_config: list[SortingChangelist] = field(default_factory=lambda:[])
    generate_sort_xml: bool = False