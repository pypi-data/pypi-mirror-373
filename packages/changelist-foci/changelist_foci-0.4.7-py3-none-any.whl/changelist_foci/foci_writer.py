""" Methods for Writing FOCI formatted text
"""
from changelist_data.changelist import Changelist
from changelist_data.file_change import FileChange

from changelist_foci.format_options import FormatOptions, DEFAULT_FORMAT_OPTIONS


def generate_foci(
    changelist: Changelist,
    format_options: FormatOptions = DEFAULT_FORMAT_OPTIONS,
) -> str:
    """ Obtain the FOCI of a Changelist.
    - Note: is not a generator method.

    Parameters:
    - changelist (Changelist): The Changelist to process and format.
    - format_options (FormatOptions): The Options controlling text and line formatting.

    Returns:
    str - The FOCI string.
    """
    return f"{changelist.name}:\n" + "\n".join(
        map(
            lambda x: f"* {get_file_subject(x, format_options)}",
            changelist.changes
        )
    )


def get_file_subject(
    file: FileChange,
    format_options: FormatOptions = DEFAULT_FORMAT_OPTIONS,
) -> str:
    """ Obtain the FOCI Subject, categorizing the change and applying Format Options.

    Parameters:
    - file (FileChange): The FileChange to process and format.
    - format_options (FormatOptions): A dataclass collection of format flags.

    Returns:
    str - The Subject Line for this Change Data.
    """
    if file.before_path is None:
        if file.after_path is None:
            return ''
        # Only the After Path exists
        return f"Create {format_options.format(file.after_path)}"
    # Process and Format the Before Path
    name_before = format_options.format(file.before_path)
    # Check for the After Path
    if file.after_path is None:
        return f"Remove {name_before}"
    # Compare Both Full Paths
    if file.before_path == file.after_path:
        return f"Update {name_before}"
    # Different Before and After Paths
    name_after = format_options.format(file.after_path)
    return f"Move {name_before} to {name_after}"