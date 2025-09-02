""" Module for creating the xml files.
"""
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, indent

from changelist_sort.xml import reader, _ensure_sort_xml_file_exists


def generate_sort_xml(
    sort_xml_file: Path | str | None,
) -> bool:
    """ Create the Sort.xml file in the Changelists directory.
 - Note: it is a hidden directory: .changelists/
 - This method may prompt the user for overwrite-confirmation when the sort.xml already contains something.

**Returns:**
 bool - True if the write operation succeeded.
    """
    sort_xml_tree = create_initial_sort_xml_tree()
    # Check SortXML File argument
    if sort_xml_file is None:
        output_file = _ensure_sort_xml_file_exists(None)
    elif isinstance(sort_xml_file, Path):
        output_file = _ensure_sort_xml_file_exists(sort_xml_file)
    elif isinstance(sort_xml_file, str):
        output_file = _ensure_sort_xml_file_exists(Path(sort_xml_file))
    else:
        raise TypeError
    try:
        with open(output_file, "wb") as f:
            sort_xml_tree.write(f, encoding='utf-8', xml_declaration=True)
        return True
    except OSError as e:
        print(f"File Write Error: {e}")
        return False


def create_initial_sort_xml_tree() -> ElementTree:
    """ The Initial Sort XML Tree:
 - Root Project Changelist
 - Tests Changelist

**Returns:**
 ElementTree - The XML ElementTree containing the Initial Changelists Config Information.
    """
    root = Element(reader.ROOT_TAG)
    root.append(root_project_cl := Element(reader.CHANGELIST_TAG))
    root.append(test_cl := Element(reader.CHANGELIST_TAG))
    root.append(changelists_cl := Element(reader.CHANGELIST_TAG))
    indent(root_project_cl, level=1)
    indent(test_cl, level=1)
    indent(changelists_cl, level=1)
    #
    root_project_cl.set(reader.CHANGELIST_NAME, 'Project Root')
    root_project_cl.append(root_files := Element(reader.FILES_TAG))
    root_files.set(reader.FILES_FIRST_DIR, 'None')
    indent(root_files, level=2)
    #
    test_cl.set(reader.CHANGELIST_NAME, 'Tests')
    test_cl.append(test_dir_files := Element(reader.FILES_TAG))
    test_dir_files.set(reader.FILES_FIRST_DIR, 'test')
    indent(test_dir_files, level=2)
    #
    changelists_cl.set(reader.CHANGELIST_NAME, 'Changelists Config')
    changelists_cl.append(changelist_file_filter_1 := Element(reader.FILES_TAG))
    changelist_file_filter_1.set(reader.FILES_PATH_START, '.changelists')
    indent(changelist_file_filter_1, level=2)
    changelists_cl.append(changelist_file_filter_2 := Element(reader.FILES_TAG))
    changelist_file_filter_2.set(reader.FILES_FILENAME_PREFIX, 'sort')
    indent(changelist_file_filter_2, level=2)
    changelists_cl.append(changelist_file_filter_3 := Element(reader.FILES_TAG))
    changelist_file_filter_3.set(reader.FILES_EXTENSION, 'xml')
    indent(changelist_file_filter_3, level=2)
    return ElementTree(root)