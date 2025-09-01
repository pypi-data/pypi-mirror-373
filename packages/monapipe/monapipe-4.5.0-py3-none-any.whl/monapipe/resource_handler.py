# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import glob
import importlib
import os
import shutil
import ssl
import subprocess
import sys
import urllib.request
from typing import Any

CONTAINER = False

try:
    # Check if `monapipe` is available as a library in the environment.
    # If it is, we can directly import the module using the full package name.
    importlib.import_module("monapipe")
    from monapipe.config import DATAVERSE, LOCAL_PATHS

except ModuleNotFoundError:
    # If `monapipe` is not available as a library in the environment (as in container environments),
    # we need to import the module from the local directory.
    if os.path.basename(os.path.dirname(__file__)) == "app":
        from config import DATAVERSE, LOCAL_PATHS

        CONTAINER = True


# Circumnavigate SSL errors when downloading.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


class ResourceHandler:
    """Wrapper class for resources."""

    def __init__(self, ressource_path: str):
        # The path to the resource directory.
        self.resource_path = ressource_path

        # The name of the resource (must be the same as the name of the directory in `resources`).
        self.name = os.path.basename(os.path.normpath(self.resource_path))

        # The path to the data directory.
        if CONTAINER:
            data_path = os.path.join(LOCAL_PATHS["data_path_container"])
        else:
            data_path = os.path.join(LOCAL_PATHS["data_path"])

        self.data_path = os.path.join(data_path, self.name)
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        # The module to load the resource from.
        self.module = _get_resource_module(resource_name=self.name)

        # The resource object.
        self._ = None

    def clear(self):
        """Clear the resource object."""
        self._ = None

    def delete(self):
        """Delete the resource files."""
        dir_contents = os.listdir(self.data_path)
        for content in dir_contents:
            if content not in ["load.py", "__init__.py"]:
                content_path = os.path.join(self.data_path, content)
                if os.path.isdir(content_path):
                    shutil.rmtree(content_path)
                else:
                    os.remove(content_path)

    def download(self):
        """Download the resource files from `data.goettingen-resarch-online.de` using the DOI from `SETTINGS`."""
        doi_key = "doi_" + self.name
        if doi_key in DATAVERSE:
            doi = DATAVERSE[doi_key]

            # check if the resource files have been downloaded/unzipped
            downloaded_and_unzipped = False
            if os.path.exists(os.path.join(self.data_path, "MANIFEST.TXT")):
                downloaded_and_unzipped = True

            if not downloaded_and_unzipped:
                # delete the resource files if download isn't complete/unzipped
                self.delete()

                # download the resource files from `data.goettingen-research-online.de`
                print("Downloading files for %s ..." % self.name)
                url = (
                    "https://data.goettingen-research-online.de/api/access/dataset/:persistentId/?persistentId="
                    + doi
                )
                _download_from_url(url, self.data_path)

                # unzip the `dataverse_files.zip`
                if os.path.exists(os.path.join(self.data_path, "dataverse_files.zip")):
                    print("Unzipping files for %s ..." % self.name)
                    shutil.unpack_archive(
                        os.path.join(self.data_path, "dataverse_files.zip"), self.data_path
                    )

                    # if the files were double-zipped, also unzip the inner directory
                    if self.name + ".zip" in os.listdir(self.data_path):
                        shutil.unpack_archive(
                            os.path.join(self.data_path, self.name + ".zip"), self.data_path
                        )
                        os.remove(os.path.join(self.data_path, self.name + ".zip"))

            # if the files are in an inner directory of the same name as the resource directory,
            # move all files from the inner directory one level up and delete the inner directory
            if os.path.isdir(os.path.join(self.data_path, self.name)):
                try:
                    shutil.copytree(
                        os.path.join(self.data_path, self.name), self.data_path, dirs_exist_ok=True
                    )
                except TypeError:  # Python < 3.8
                    for file_or_dir in os.listdir(os.path.join(self.data_path, self.name)):
                        shutil.move(
                            os.path.join(self.data_path, self.name, file_or_dir),
                            os.path.join(self.data_path, file_or_dir),
                        )
                shutil.rmtree(os.path.join(self.data_path, self.name))

            # sometimes, one or more files are missing in `dataverse_files.zip` because they were too large to be downloaded;
            # this is indicated in `MANIFEST.TXT`
            if os.path.exists(os.path.join(self.data_path, "MANIFEST.TXT")):
                with open(os.path.join(self.data_path, "MANIFEST.TXT")) as file:
                    missing_file_lines = sorted([line for line in file if "skipped" in line])
                    for missing_file_line in missing_file_lines:
                        missing_file = missing_file_line.split()[0]
                        if (
                            len(
                                glob.glob(
                                    os.path.join(self.data_path, "**", missing_file), recursive=True
                                )
                            )
                            == 0
                        ):
                            # if the file is really missing, print instructions to the user for manual download
                            error_msg = missing_file_line + "\n"
                            error_msg += "To download the missing file yourself, perform the following steps:\n"
                            error_msg += (
                                "1. Go to the resource page: https://data.goettingen-research-online.de/dataset.xhtml?persistentId="
                                + doi
                                + "\n"
                            )
                            error_msg += "2. Search the missing file (Files > Change View: Tree) and click on it, which directs you to the file page.\n"
                            error_msg += "3. From the file's metadata, copy the following fields: 'File Path' and 'File Persistent ID' (or, if the latter is missing: 'Download URL').\n"
                            error_msg += "4. Manually download the missing file in Python:\n\n"
                            error_msg += "\timport resource_handler as resources\n\n"
                            error_msg += (
                                '\tresources.get_resource_handler("'
                                + self.name
                                + '").download_resource_file(file_path, file_persistent_id_or_download_url)\n'
                            )
                            raise Exception(error_msg)

    def download_resource_file(self, file_path: str, file_persistent_id_or_download_url: str):
        """Download a (missing) resource file.
            This function is meant to be used when resource files could not be downloaded automatically.

        Args:
            file_path: The destination path of the file, relative to `self.path`.
            file_persistent_id_or_download_url: DOI or URL for download.

        """
        while file_path.startswith(self.name + "/"):
            file_path = file_path[len(self.name) + 1 :]
        path = os.path.join(self.data_path, os.path.normpath(file_path))
        if os.path.exists(path):
            if file_persistent_id_or_download_url.startswith("doi:"):
                url = (
                    "https://data.goettingen-research-online.de/api/access/datafile/:persistentId/?persistentId="
                    + file_persistent_id_or_download_url
                )
            else:
                url = file_persistent_id_or_download_url
            _download_from_url(url, path)

    def provide(self):
        """Load the resource, if not already loaded, and save it in `self._`."""
        if self._ is None:
            self.download()
            self._ = self.module.load()


def access(resource_name: str, clear_resource: bool = False) -> Any:
    """Returns a resource object.

    Args:
        resource_name: Name of the resource.
        clear_resource: If True, the resource is cleared and loaded again.

    Returns:
        The resource loaded from `resources.[name]`.

    """
    resource_handler = get_resource_handler(resource_name=resource_name)
    if clear_resource:
        resource_handler.clear()
    resource_handler.provide()
    return resource_handler._


def get_resource_handler(resource_name: str) -> ResourceHandler:
    """Get the resource handler by resource name.

    Args:
        resource_name: Name of the resource directory.

    Returns:
        The corresponding resource handler.

    """
    load_module = _get_resource_module(resource_name=resource_name)
    return getattr(load_module, "RESOURCE_HANDLER")


def _get_resource_module(resource_name: str) -> Any:
    """Get the resource module by resource name.

    Args:
        resource_name: Name of the resource directory.

    Returns:
        The corresponding resource module.

    """
    if CONTAINER:
        # If `monapipe` is not available as a library in the environment (as in container environments),
        # we need to import the module from the local directory.

        # Construct the full module name and import it, as before.
        module_name = f"resources.{resource_name}.load"
        return importlib.import_module(module_name)
    else:
        importlib.import_module("monapipe")

        # Construct the full module name and import it.
        module_name = f"monapipe.resources.{resource_name}.load"

        return importlib.import_module(module_name)


def _download_from_url(url: str, path: str):
    """Download a file from a given URL.

    Args:
        url: The URL.
        path: The destination path.

    """
    api_key = DATAVERSE["api_token"]
    if api_key != "":
        print("DOWNLOADING WITH CURL")
        curl_args = ["curl", "-L", "-O", "-J"]
        curl_args.extend(["-H", "X-Dataverse-key:" + api_key])
        subprocess.run(curl_args + [url], cwd=path, shell=False, check=False)
    else:
        try:
            print("DOWNLOADING WITH URLLIB")
            urllib.request.urlretrieve(url=url, filename=os.path.join(path, "dataverse_files.zip"))
        except Exception as e:
            error_msg = f"Download failed for {url}\n{repr(e)}"
            sys.exit(error_msg)
