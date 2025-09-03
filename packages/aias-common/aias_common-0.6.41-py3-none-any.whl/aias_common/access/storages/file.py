import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

from aias_common.access.configuration import (AccessType,
                                              FileStorageConfiguration)
from aias_common.access.file import File
from aias_common.access.storages.abstract import AbstractStorage


class FileStorage(AbstractStorage):

    def get_configuration(self) -> FileStorageConfiguration:
        assert isinstance(self.storage_configuration, FileStorageConfiguration)
        return self.storage_configuration

    def get_storage_parameters(self):
        return {}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        return (scheme == "" or scheme == "file") and self.is_path_authorized(href, AccessType.READ)

    def exists(self, href: str):
        return Path(href).exists()

    def get_rasterio_session(self):
        return {}

    def is_path_authorized(self, href: str, action: AccessType) -> bool:
        if action == AccessType.WRITE:
            paths = self.get_configuration().writable_paths
        if action == AccessType.READ:
            paths = list([*self.get_configuration().readable_paths, *self.get_configuration().writable_paths])
        return any(list(map(lambda p: os.path.commonpath([p, href]) == p, paths)))

    def pull(self, href: str, dst: str):
        super().pull(href, dst)

        if not self.is_path_authorized(dst, AccessType.WRITE):
            raise ValueError('The desired output path is not authorized')

        shutil.copy(href, dst)

    def push(self, href: str, dst: str):
        super().push(href, dst)

        if not self.is_path_authorized(dst, AccessType.WRITE):
            raise ValueError('The desired output path is not authorized')

        shutil.copy(href, dst)

    def is_file(self, href: str):
        return os.path.isfile(href)

    def is_dir(self, href: str):
        return os.path.isdir(href)

    def get_file_size(self, href: str):
        return os.stat(href).st_size

    def listdir(self, href: str) -> list[File]:
        return list(map(lambda f: self.__to_file__(base=href, name=f), os.listdir(href)))

    def __to_file__(self, base: str, name: str):
        path = os.sep.join([base.removesuffix("/"), name])
        f = File(name=name, path=path, is_dir=os.path.isdir(path), last_modification_date=os.path.getmtime(path), creation_date=os.path.getctime(path))
        if f.is_dir:
            f.path = f.path.removesuffix("/") + "/"
        return f

    def get_last_modification_time(self, href: str):
        return os.path.getmtime(href)

    def get_creation_time(self, href: str):
        return os.path.getctime(href)

    def makedir(self, href: str, strict=False):
        if not self.is_path_authorized(href, AccessType.WRITE):
            raise ValueError('The desired folder is not authorized')

        if not self.exists(href) or strict:
            os.makedirs(href)

    # @override
    def dirname(self, href: str):
        return os.path.dirname(os.path.abspath(href))

    def clean(self, href: str):
        if self.is_path_authorized(href, AccessType.WRITE):
            if self.is_dir(href):
                shutil.rmtree(href)  # !DELETE!
            else:
                os.remove(href)  # !DELETE!
        else:
            raise ValueError("The given path is read-only")

    def get_gdal_stream_options(self):
        return {}

    def gdal_transform_href_vsi(self, href: str):
        return href
