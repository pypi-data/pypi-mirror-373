""" Changelist Sorting Methods.
"""
from typing import Callable, Generator

from changelist_sort.change_data import ChangeData
from changelist_sort.changelist_data import ChangelistData
from changelist_sort.list_key import ListKey


def split_changelist(
    changelist: ChangelistData,
    is_sorted: Callable[[ListKey, ChangeData], bool],
) -> list[ChangeData]:
    """ Split the Changelist by checking that all changes are sorted.
 - Removes each element that is returned from the changelist.

**Parameters:**
 - changelist (ChangelistData): The Changelist to split based on sorting function.
 - is_sorted (callable[bool]): A Function that determines whether a Change is Sorted.

**Returns:**
 list[ChangeData] - The List of ChangeData that are Unsorted, now removed from this changelist.
    """
    return list(generate_unsorted_change_data(changelist, is_sorted))


def generate_unsorted_change_data(
    changelist: ChangelistData,
    is_sorted: Callable[[ListKey, ChangeData], bool],
) -> Generator[ChangeData, None, None]:
    """ Iterates through the ChangeData files, popping and yielding those that are unsorted.
- Modifies the ChangelistData by popping any valid number of items from the changes list.

**Parameters:**
 - changelist (ChangelistData): The Changelist containing File Change data to check if sorted.
 - is_sorted (Callable): The callable function that determines whether a FileChange is sorted in this Changelist.

**Yields:**
 Generator[ChangeData] - The ChangeData objects that are not sorted in this Changelist, and have been popped from the list.
    """
    for index in range(len(changelist.changes) - 1, -1, -1):
        if not is_sorted(
            changelist.list_key,
            changelist.changes[index]
        ):
            yield changelist.changes.pop(index)