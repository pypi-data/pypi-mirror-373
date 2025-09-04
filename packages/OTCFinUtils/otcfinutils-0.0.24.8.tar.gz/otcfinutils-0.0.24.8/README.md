# Intro

This project contains code for interacting with the Dataverse and with Sharepoint.

# File Structure

The code is segmented into the following files and folders.

### `update-version.sh`

A Bash script for publishing a new version of the library to PYPI.

- Runs the `setup.py` script, which creates the needed files for PYPI.
- Removes the files that are not needed for the version-change.
- Uploads the needed files to PYPI.
- Removes all files created in this process - cleanup.

### `setup.py`

Contains the metadata for the library, like the name, version number,
description, author information, dependencies, etc. Used every time when the version is updated.

### `Library Usage.md`

Contains a list of the main functions that are available in the library. Might be missing the latest functions and changes.

### `HISTORY.md`

Contains the version history of the library. Every time when the version is updated, it's good practice to document what the applied changes were. Can be useful when checking the status of the latest or previous version.

### `.gitignore`

A list of files and folders that can be used locally but should not be pushed to the public project. For example, testing files, local configuration, etc.

## `tests/`

A work-in-progress folder that contains unit tests and draft tests for testing the code.

## `OTCFinUtils/`

The main code folder. Contains several files.

### `__init__.py`

A list of the functions and classes that are publicly available for usage when the library is imported into a project.

### `buffer.py`

A helper class used in the `DataMapper` class, for storing data in a buffered format, before executing bulk reading and writing operations to the Dataverse.

### `data_structs.py`

Contains helper classes, constants and enums used throughout the rest of the code.

### `dataverse_handler.py`

Contains code for seting up and using a `DVHandler` object. Used for reading from and writing to the Dataverse.

### `mapper_loading.py`

Contains helper functions used by the `DataMapper` for reading in data from the Dataverse. Separated for readability.

### `mapper.py`

Contains the `DataMapper` class that is used for loading data into the Dataverse by using mappings from the `File Mappings` table.

### `security.py`

Functions and helper functions for creating tokens for accessing the Dataverse, SharePoint, etc.

### `sharepoint_client.py`

Not used anymore... Can be removed.

### `sharepoint.py`

Functions for reading and writing files from and to SharePoint.

### `utils.py`

Smaller helper functions used in different locations in the code.