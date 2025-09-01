""" Changelist Data Package.
"""
from pathlib import Path
from typing import Generator

from changelist_data.changelist import Changelist
from changelist_data.storage import load_storage, load_any_storage_option, read_storage, read_any_storage_option, \
    generate_changelists_from_storage, _generate_changelists_from_any_storage_option
from changelist_data.storage.changelist_data_storage import ChangelistDataStorage
from changelist_data.storage.storage_type import StorageType, get_default_path
from changelist_data.validation.arguments import validate_string_argument
from changelist_data.xml.changelists import new_tree


def read_storage_from_file_arguments(
    changelists_file: str | None = None,
    workspace_file: str | None = None,
) -> list[Changelist] | None:
    """ Process the Given File Arguments, and read from Storage.
 - Storage is managed by changelist_data package.

**Parameters:**
 - changelists_file (str?): A string path to the Changelists file, if specified.
 - workspace_file (str?): A string path to the Workspace file, if specified.

**Returns:**
 list[Changelist] - The Changelist data from the storage file.
    """
    if validate_string_argument(changelists_file):
        return read_storage(StorageType.CHANGELISTS, Path(changelists_file))
    if validate_string_argument(workspace_file):
        return read_storage(StorageType.WORKSPACE, Path(workspace_file))
    return read_any_storage_option()


def generate_changelists_from_storage_file_arguments(
    changelists_file: str | None = None,
    workspace_file: str | None = None,
) -> Generator[Changelist, None, None]:
    """ Process the Given File Arguments, and generate Changelist data objects from Storage.
 - Storage is managed by changelist_data.storage package.

**Parameters:**
 - changelists_file (str?): A string path to the Changelists file, if specified.
 - workspace_file (str?): A string path to the Workspace file, if specified.

**Yields:**
 Generator[Changelist] - The Changelist data from the storage file.
    """
    if validate_string_argument(changelists_file):
        return generate_changelists_from_storage(StorageType.CHANGELISTS, Path(changelists_file))
    if validate_string_argument(workspace_file):
        return generate_changelists_from_storage(StorageType.WORKSPACE, Path(workspace_file))
    return _generate_changelists_from_any_storage_option()


def load_storage_from_file_arguments(
    changelists_file: str | None = None,
    workspace_file: str | None = None,
) -> ChangelistDataStorage:
    """ Use the given optional parameters and search for the storage file.
 - Changelists_file argument overrides Workspace_file.
 - Defaults to searching Changelists then Workspace file default locations.

**Parameters:**
 - changelists_file (str?): The string path to the Changelists XML Data file.
 - workspace_file (str?): The string path to the Workspace XML file.

**Returns:**
 ChangelistDataStorage - The data class container for Changelist information.
    """
    if validate_string_argument(changelists_file):
        return load_storage(StorageType.CHANGELISTS, Path(changelists_file))
    if validate_string_argument(workspace_file):
        return load_storage(StorageType.WORKSPACE, Path(workspace_file))
    if (existing_storage := load_any_storage_option()) is not None:
        return existing_storage
    # Create a new Changelists Storage file
    return ChangelistDataStorage(
        new_tree(),
        StorageType.CHANGELISTS,
        get_default_path(StorageType.CHANGELISTS)
    )