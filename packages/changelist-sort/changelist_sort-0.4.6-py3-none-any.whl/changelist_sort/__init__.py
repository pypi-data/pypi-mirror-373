""" Main Package Methods.
"""
from typing import Iterable

from changelist_data import ChangelistDataStorage
from changelist_data.changelist import Changelist

from changelist_sort.changelist_data import ChangelistData, generate_simple_changelists, generate_expanded_changelists
from changelist_sort.input.input_data import InputData
from changelist_sort.sorting import sort, SortMode, SortingChangelist


def sort_changelists(
    input_data: InputData,
):
    """ Sort the given Changelists and write them to the Workspace File.

**Parameters:**
 - input_data (InputData): The program input, containing data and options.
    """
    sort_changelist_in_storage(
        input_data.storage,
        input_data.sort_mode,
        input_data.remove_empty,
        input_data.sorting_config,
    )
    #Todo: Remove this write_to_storage in Version 0.5, not within scope
    # The storage call is to be made by main method.
    input_data.storage.write_to_storage()


def sort_changelist_in_storage(
    storage: ChangelistDataStorage,
    sort_mode: SortMode,
    remove_empty: bool,
    sorting_config: list[SortingChangelist],
):
    """ Sort the Changelists in Storage, and update them.

**Parameters:**
 - storage (ChangelistDataStorage): The Storage object with read and write access to changelists data.
 - sort_mode (SortMode): The Sorting Mode to apply during operation.
 - remove_empty (bool): Whether to remove empty Changelists, before writing to storage.
 - sorting_config (list[SortingChangelist]): The configuration for sorting criteria.
    """
    changelists = sort(
        initial_list=generate_expanded_changelists(storage.generate_changelists()),
        sort_mode=sort_mode,
        sorting_config=sorting_config,
    )
    storage.update_changelists(
        generate_simple_changelists(changelists) if not remove_empty else filter(
            lambda x: len(x.changes) > 0, generate_simple_changelists(changelists)
        )
    )


def simplify_changelists(
    data: Iterable[ChangelistData]
) -> list[Changelist]:
    """ Convert to ChangelistData Storage DataClass."""
    return list(generate_simple_changelists(data))


def expand_changelists(
    data: Iterable[Changelist]
) -> list[ChangelistData]:
    """ Convert from ChangelistData Storage DataClass to Sort DataClass."""
    return list(generate_expanded_changelists(data))