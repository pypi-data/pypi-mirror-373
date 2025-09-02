""" Valid Input Data Class.
"""
from dataclasses import dataclass
from typing import Iterable

from changelist_data.storage.changelist_data_storage import ChangelistDataStorage
from changelist_data.changelist import Changelist

from changelist_foci.format_options import FormatOptions, DEFAULT_FORMAT_OPTIONS


@dataclass(frozen=True)
class InputData:
    """ A Data Class Containing Program Input.

**Fields:**
 - changelists (Iterable[Changelist]): The Iterable of changelists to process.
 - changelist_name (str): The name of the Changelist, or None.
 - format_options (FormatOptions): The options for output formatting.
 - all_changes (bool): Flag for printing all changes in any Changelist.
 - changelist_data_storage (ChangelistDataStorage): If this field is present, insert FOCI into Changelist Comments instead of printing.
    """
    changelists: Iterable[Changelist]
    changelist_name: str | None = None
    format_options: FormatOptions = DEFAULT_FORMAT_OPTIONS
    all_changes: bool = False
    changelist_data_storage: ChangelistDataStorage | None = None
