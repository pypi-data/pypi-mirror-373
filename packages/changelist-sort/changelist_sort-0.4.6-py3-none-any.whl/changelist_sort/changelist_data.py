"""The Data Class for a ChangeList.
"""
from dataclasses import dataclass, field
from typing import Iterable, Generator

from changelist_data.changelist import Changelist

from changelist_sort import list_key, change_data
from changelist_sort.change_data import ChangeData
from changelist_sort.list_key import ListKey


@dataclass(frozen=True)
class ChangelistData:
    """ The complete Data class representing a ChangeList.
    
**Properties:**
 - id (str): The unique id of the changelist.
 - name (str): The name of the changelist.
 - changes (list[ChangeData]): The list of file changes in the changelist.
 - comment (str): The comment associated with the changelist.
 - is_default (bool): Whether this is the active changelist.

**Post Init Properties:**
 - list_key (ListKey): A key helping to identify this Changelist while sorting.
    """
    id: str
    name: str
    changes: list[ChangeData] = field(default_factory=lambda: [])
    comment: str = ''
    is_default: bool = False
    list_key: ListKey = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'list_key', list_key.compute_key(self.name))


def expand(cl: Changelist) -> ChangelistData:
    return ChangelistData(
        id=cl.id,
        name=cl.name,
        changes=[ change_data.expand(x) for x in cl.changes ],
        comment=cl.comment,
        is_default=cl.is_default,
    )


def simplify(cl: ChangelistData) -> Changelist:
    return Changelist(
        id=cl.id,
        name=cl.name,
        changes=[ change_data.simplify(x) for x in cl.changes ],
        comment=cl.comment,
        is_default=cl.is_default,
    )


def generate_simple_changelists(
    data: Iterable[ChangelistData]
) -> Generator[Changelist, None, None]:
    for x in data:
        yield simplify(x)


def generate_expanded_changelists(
    data: Iterable[Changelist]
) -> Generator[ChangelistData, None, None]:
    for x in data:
        yield expand(x)