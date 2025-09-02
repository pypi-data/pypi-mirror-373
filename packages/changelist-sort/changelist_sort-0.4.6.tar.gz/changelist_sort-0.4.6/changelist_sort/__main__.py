#!/usr/bin/python


def main():
    import changelist_sort
    from sys import argv
    # Validate Args and Load Input Data
    input_data = changelist_sort.input.validate_input(argv[1:])
    # Generate the Sorting Configuration file
    if input_data.generate_sort_xml:
        from changelist_sort.xml.generator import generate_sort_xml
        if generate_sort_xml(None):
            print("The file has been created: .changelists/sort.xml")
        else:
            print("Failed to create the sort.xml file.")
        return None
    # Sort the CL Tree In-Memory
    changelist_sort.sort_changelists(input_data)
      # Write Changelist Data File
    # Todo: Version 0.5, when sort_changelist no longer calls write_to_storage.
    #  input_data.storage.write_to_storage()
    #print(output_data)
    return None


if __name__ == "__main__":
    # Get the directory of the current file (__file__ is the path to the script being executed)
    from pathlib import Path
    current_directory = Path(__file__).resolve().parent.parent
    # Add the directory to sys.path
    from sys import path
    path.append(str(current_directory))
    main()