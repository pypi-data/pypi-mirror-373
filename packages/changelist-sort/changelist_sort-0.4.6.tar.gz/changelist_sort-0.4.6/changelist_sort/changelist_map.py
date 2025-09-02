"""The Changelist Map.
"""
from typing import Generator

from changelist_sort.changelist_data import ChangelistData
from changelist_sort.list_key import ListKey


class ChangelistMap:
    """ The Map containing all of the Changelists.
    """

    def __init__(self):
        self.mapping = {}
        self.changelist_ids = set()
    
    def insert(self, changelist: ChangelistData) -> bool:
        """ Insert a Changelist into the Map.
            - Uses the Changelist Simple name as a key.

        Parameters:
        - changelist (ChangelistData): The Changelist Data to insert into the Map.

        Returns:
        bool - True when Changelist Name and Id are not already in the Map.
        """
        if changelist.id in self.changelist_ids or\
            changelist.list_key.key in self.mapping:
            return False
        self.changelist_ids.add(changelist.id)
        self.mapping[changelist.list_key.key] = changelist
        return True

    def search(self, key: str) -> ChangelistData | None:
        """ Search the Map dict for the Changelist with the given simple name.
            - Expects the Changelist Simple Name to match the key.
        """
        return self.mapping.get(key)

    def contains_id(self, id: str) -> bool:
        """ Determine whether the Map contains the given id.
        """
        return id in self.changelist_ids

    def get_lists(self) -> list[ChangelistData]:
        """ Obtain all Changelists in the Map as a List.
        """
        return list(self.mapping.values())

    def generate_lists(self) -> Generator[ChangelistData, None, None]:
        """ Generate Changelists from the Map.
        """
        for k, cl in self.mapping.items():
            yield cl

    def generate_nonempty_lists(self) -> Generator[ChangelistData, None, None]:
        """ Obtain only non-empty Changelists in the Map.
        """
        for k, cl in self.mapping.items():
            if len(cl.changes) > 0:
                yield cl

    def _generate_new_id(self) -> str:
        """ Create a new Changelist Id that does not appear in this map.
        """
        from random import choices
        chars = list(_hex_char_generator())
        def generate_id():
            return '-'.join(''.join(choices(chars, k=x)) for x in (8, 4, 4, 4, 12))
        test_id = generate_id()
        while self.contains_id(test_id):
            test_id = generate_id()
        return test_id

    def create_changelist(self, cl_name: ListKey | str) -> ChangelistData:
        """ Create a new empty Changelist with a new Id, and insert it into the Map.

        Parameters:
        - name (str): The Name of the new Changelist.

        Returns:
        ChangelistData - The Changelist that was recently created and added to the Map.
        """
        if isinstance(cl_name, ListKey):
            cl_name = cl_name.changelist_name 
        elif isinstance(cl_name, str):
            pass
        else:
            raise TypeError
        new_cl = ChangelistData(
            id=self._generate_new_id(),
            name=cl_name,
        )
        if self.insert(new_cl):
            return new_cl
        if (existing_cl := self.search(new_cl.list_key.key)) is not None:
            return existing_cl
        exit(f"Failed to create new Changelist(name={new_cl.list_key.changelist_name})")


def _hex_char_generator() -> Generator[str, None, None]:
    """ Generator yielding all possible hexadecimal characters.
    """
    for i in range(16):
        if i < 10:
            yield str(i) # Yield lowercase digits (0-9)
        else:
            yield chr(ord('a') + i - 10) # Yield uppercase letters (A-F)