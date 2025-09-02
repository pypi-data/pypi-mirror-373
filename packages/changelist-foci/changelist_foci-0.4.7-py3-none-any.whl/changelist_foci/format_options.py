""" The Detailed Options for FOCI Formatting.
"""
from dataclasses import dataclass
from os.path import basename, splitext


@dataclass(frozen=True)
class FormatOptions:
    """ The detailed options for FOCI formatting.

**Fields:**
 - full_path (bool): Whether to display the full path to the file. Default: False.
 - no_file_ext (bool): Whether to filter file extensions (except move with different extensions). Default: False.
 - file_name (bool): Whether to display the file name. Removes any parent directories. Default: False.
    """
    full_path: bool = False
    no_file_ext: bool = False
    file_name: bool = False

    def format(self, path: str) -> str:
        """ Format a Path String, applying the given options.

    **Parameters:**
     - path (str): The relative (project root) path string in Change Data.

    **Returns:
     str - Formatted File Information.
        """
        if self.full_path:
            if self.no_file_ext: # Filter FileExt
                return splitext(path)[0]
            else: # No Change Necessary
                return path
        if self.file_name:
            filename = basename(path)
            if self.no_file_ext: # Filter FileExt
                return splitext(filename)[0]
            return filename
        path = path.lstrip('/') # Remove initial slash char
        if self.no_file_ext: # Filter FileExt
            return splitext(path)[0]
        return path


""" The Default FormatOptions: All fields are False.
"""
DEFAULT_FORMAT_OPTIONS: FormatOptions = FormatOptions()