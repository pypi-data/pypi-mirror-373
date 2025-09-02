#!/usr/bin/python


def main():
    import changelist_foci
    from sys import argv
    # When CL-Data-Storage Field is None, print FOCI
    if not (input_data := changelist_foci.input.validate_input(argv[1:])).changelist_data_storage:
        print(changelist_foci.get_changelist_foci(input_data))
    else: # Insert FOCI into Storage
        changelist_foci.insert_foci_comments(
            input_data.changelist_data_storage,
            input_data.format_options
        )
        input_data.changelist_data_storage.write_to_storage()


if __name__ == "__main__":
    from pathlib import Path
    from sys import path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    current_directory = Path(__file__).resolve().parent.parent
    path.append(str(current_directory)) # Add the directory to sys.path
    main()