import os
from urllib.parse import urlparse, urlunparse

from aias_common.access.configuration import GoogleStorageConfiguration
from aias_common.access.file import File
from aias_common.access.storages.abstract import AbstractStorage
from fastapi_utilities import ttl_lru_cache
from google.cloud.storage import Client
from google.oauth2 import service_account


class GoogleStorage(AbstractStorage):

    def get_configuration(self) -> GoogleStorageConfiguration:
        assert isinstance(self.storage_configuration, GoogleStorageConfiguration)
        return self.storage_configuration

    def get_storage_parameters(self):
        if self.get_configuration().is_anon_client:
            client = Client.create_anonymous_client()
        else:
            credentials = service_account.Credentials.from_service_account_info(self.get_configuration().api_key.model_dump())
            client = Client(project=self.get_configuration().api_key.project_id, credentials=credentials)

        return {"client": client}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        return scheme == "gs" and netloc == self.get_configuration().bucket

    def __get_bucket(self):
        client = self.get_storage_parameters()["client"]

        if self.get_configuration().is_anon_client:
            return client.bucket(self.get_configuration().bucket)
        else:
            # Try to retrieve a bucket (this makes an API request)
            return client.get_bucket(self.get_configuration().bucket)

    def __get_blob(self, href: str):
        bucket = self.__get_bucket()
        return bucket.get_blob(urlparse(href).path.lstrip("/") or "/")

    def __create_blob(self, href: str):
        bucket = self.__get_bucket()
        return bucket.blob(urlparse(href).path.lstrip("/") or "/")

    def exists(self, href: str):
        return self.is_file(href) or self.is_dir(href)

    def get_rasterio_session(self):
        import rasterio.session

        params = {
            "session": rasterio.session.GSSession(self.get_configuration().credentials_file),
            **self.__get_gdal_signed()
        }

        return params

    def __get_gdal_signed(self):
        params = {}
        if self.get_configuration().api_key is None:
            params["GS_NO_SIGN_REQUEST"] = "YES"
        else:
            params["GS_NO_SIGN_REQUEST"] = "NO"

        return params

    def pull(self, href: str, dst: str):
        super().pull(href, dst)

        blob = self.__get_blob(href)
        if blob is None:
            raise LookupError(f"Can't find {href}")

        blob.download_to_filename(dst)

    def push(self, href: str, dst: str):
        super().push(href, dst)

        blob = self.__create_blob(dst)
        if blob is None:
            raise LookupError(f"Can't create blob: {dst}")

        blob.upload_from_filename(href)

    @ttl_lru_cache(ttl=AbstractStorage.cache_tt, max_size=1024)
    def __list_blobs(self, source: str) -> list[File]:
        """
        Return a list of files contained in the specified folder, as well as subfolders
        """
        url = urlparse(source)
        path = url.path.removeprefix("/")
        blobs = self.__get_bucket().list_blobs(prefix=path, delimiter="/")
        files = list(filter(lambda f: f.path != path and f.name != "", map(lambda b: File(name=os.path.basename(b.name), path=self.__update_url__(source=source, path=b.name), is_dir=False, last_modification_date=b.updated, creation_date=b.time_created), blobs)))
        dirs = list(map(lambda b: File(name=os.path.basename(b.removesuffix("/")), path=self.__update_url__(source=source, path=b).removesuffix("/") + "/", is_dir=True), blobs.prefixes))
        return files + dirs

    def __update_url__(self, source: str, path: str):
        url = urlparse(source)
        components = list(url[:])
        if len(components) == 5:
            components.append('')
        components[2] = path
        return urlunparse(tuple(components))

    def is_file(self, href: str):
        files = self.__list_blobs(href)
        return len(list(filter(lambda f: f.path == href and not f.is_dir, files))) == 1

    def is_dir(self, href: str):
        files = self.__list_blobs(href.removesuffix("/") + "/")
        return len(list(filter(lambda f: f.path.removesuffix("/") != href.removesuffix("/"), files))) > 0

    def get_file_size(self, href: str):
        return self.__get_blob(href).size

    def listdir(self, href: str) -> list[File]:
        return self.__list_blobs(href.removesuffix("/") + "/")

    def get_last_modification_time(self, href: str):
        blob = self.__get_blob(href)
        if blob:
            mod_time = blob.updated
            return mod_time.timestamp() if mod_time is not None else 0
        return 0

    def get_creation_time(self, href: str):
        blob = self.__get_blob(href)
        if blob:
            creation_time = blob.time_created
            return creation_time.timestamp() if creation_time is not None else 0
        return 0

    def makedir(self, href: str, strict=False):
        if strict:
            raise PermissionError("Creating a folder on a remote storage is not permitted")

    def clean(self, href: str):
        raise PermissionError("Deleting files on a remote storage is not permitted")

    def get_gdal_stream_options(self):
        params = {
            **self.__get_gdal_signed()
        }

        if not self.get_configuration().is_anon_client:
            params["GS_OAUTH2_PRIVATE_KEY"] = self.get_configuration().api_key.private_key
            params["GS_OAUTH2_CLIENT_EMAIL"] = self.get_configuration().api_key.client_email

        return params

    def gdal_transform_href_vsi(self, href: str):
        return href.replace("gs://", "/vsigs/")
