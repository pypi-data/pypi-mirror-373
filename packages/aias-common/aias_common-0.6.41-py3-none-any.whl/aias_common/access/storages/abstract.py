import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from aias_common.access.configuration import AnyStorageConfiguration
from aias_common.access.file import File


class AbstractStorage(ABC):
    cache_tt = 60 * 5
    cache_size = 2048

    def __init__(self, storage_configuration: AnyStorageConfiguration):
        self.storage_configuration = storage_configuration

    @abstractmethod
    def get_configuration(self) -> AnyStorageConfiguration:
        """Returns the storage configuration

        Returns:
            AnyStorageConfiguration: storage configuration
        """
        ...

    @abstractmethod
    def get_storage_parameters(self) -> dict:
        """Based on the type of storage and its characteristics, gives storage-specific parameters to use to access data

        Args:
            href (str): Href of the file to consult
        """
        ...

    @abstractmethod
    def supports(self, href: str) -> bool:
        """Return whether the provided href can be handled by the storage.

        Args:
            href (str): Href of the file to consult

        Returns:
            bool: True if the storage can handle href, False otherwise
        """
        ...

    @abstractmethod
    def exists(self, href: str) -> bool:
        """Return whether the file given exists in the storage

        Args:
            href (str): Href of the file to consult

        Returns:
            bool: True if the file exists, False otherwise
        """
        ...

    @abstractmethod
    def get_rasterio_session(self) -> dict:
        """Return a rasterio Session and potential variables to access data remotely

        Args:
            href (str): Href od the file to stream

        Returns:
            dict
        """
        ...

    @abstractmethod
    def pull(self, href: str, dst: str):
        """Copy/Download the desired file from the file system to write it locally

        Args:
            href (str): File to fetch
            dst (str): Destination of the file
        """
        # Check that dst is local
        scheme = urlparse(dst).scheme
        if scheme != "" and scheme != "file":
            raise ValueError("Destination must be on the local filesystem")

    @abstractmethod
    def push(self, href: str, dst: str):
        """Copy/upload the desired file from local to write it on the file system

        Args:
            href (str): File to upload
            dst (str): Destination of the file
        """
        # Check that href is local
        scheme = urlparse(href).scheme
        if scheme != "" and scheme != "file":
            raise ValueError("Source file to upload must be on the local filesystem")

    @abstractmethod
    def is_file(self, href: str) -> bool:
        """Returns whether the specified href is a file

        Args:
            href(str): The href to test

        Returns:
            bool: Whether the input is a file
        """
        ...

    @abstractmethod
    def is_dir(self, href: str) -> bool:
        """Returns whether the specified href is a directory

        Args:
            href(str): The href to test

        Returns:
            bool: Whether the input is a directory
        """
        ...

    @abstractmethod
    def get_file_size(self, href: str) -> int | None:
        """Returns the size of the specified href

        Args:
            href(str): The href to examine
        """
        ...

    @abstractmethod
    def listdir(self, href: str) -> list[File]:
        """Returns the list of files and folders in the specified directory

        Args:
            href(str): The directory to examine
        """
        ...

    @abstractmethod
    def get_last_modification_time(self, href: str) -> float:
        """Returns the last modification time of the specified href

        Args:
            href(str): The href to examine

        Returns:
            float: the timestamp in seconds of last modification time
        """
        ...

    @abstractmethod
    def get_creation_time(self, href: str) -> float:
        """Returns the creation time of the specified href

        Args:
            href(str): The href to examine

        Returns:
            float: the timestamp in seconds of creation time
        """
        ...

    @abstractmethod
    def makedir(self, href: str, strict=False):
        """Create if needed (and possible) the specified dir

        Args:
            href(str): The href to the dir to create
            strict(bool): Whether to force the creation
        """
        ...

    def dirname(self, href: str):
        """Return the name of the directory containing the specified href

        Args:
            href(str): The href to examine
        """
        return os.path.dirname(href)

    @abstractmethod
    def clean(self, href: str):
        """If authorized, remove the given file

        Args:
            href(str): The href to delete
        """
        ...

    @abstractmethod
    def get_gdal_stream_options(self) -> dict:
        """Return the options to use to stream a GDAL file through its virtual file systems
        """
        ...

    @abstractmethod
    def gdal_transform_href_vsi(self, href: str):
        """Transform the archive's href into a format manageable by GDAL's virtual file systems

        Args:
            href(str): The href to examine
        """
        ...

    def get_gdal_src(self, href: str):
        """Return the archive's dataset through GDAL's virtual file systems

        Args:
            href(str): The href to examine
        """
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly

        with gdal.config_options(self.get_gdal_stream_options()):
            src_ds = gdal.Open(self.gdal_transform_href_vsi(href), GA_ReadOnly)
        return src_ds

    def get_gdal_info(self, href: str, gdal_options):
        """Return the archive's info through GDAL's virtual file systems

        Args:
            href(str): The href to examine
        """
        from osgeo import gdal

        with gdal.config_options(self.get_gdal_stream_options()):
            return gdal.Info(self.gdal_transform_href_vsi(href), options=gdal_options)
