import tempfile
from typing import Literal
from typing import Annotated, Union
from pydantic import BaseModel, Field, computed_field
import enum
import json


class AccessType(enum.Enum):
    READ = "read"
    WRITE = "write"


class StorageConfiguration(BaseModel, extra='allow'):
    type: str = Field(title='Storage type', description="Type of the storage used")
    is_local: bool = Field(title='Is a local storage', description="Whether the storage is local or remote")


class FileStorageConfiguration(StorageConfiguration):
    type: Literal["file"] = Field(default="file", title="Type", description="Indicates the storage type, fixed to 'file'")
    is_local: Literal[True] = Field(default=True, title='Is a local storage', description="Whether the storage is local or remote")
    writable_paths: list[str] = Field(default=[], title="Writable Paths", description="List of paths where files can be written")
    readable_paths: list[str] = Field(default=[], title="Readable Paths", description="List of paths from which files can be read")


class GoogleStorageConstants(str, enum.Enum):
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
    UNIVERSE_DOMAIN = "googleapis.com"


class GoogleStorageApiKey(BaseModel):
    type: Literal["service_account"] = Field(default="service_account", title="Type", description="Must be 'service_account'.")
    project_id: str = Field(title="Project ID", description="Google Cloud project identifier")
    private_key_id: str = Field(title="Private Key ID", description="ID of the private key used for authentication")
    private_key: str = Field(title="Private Key", description="The private key content in PEM format")
    client_email: str = Field(title="Client Email", description="Service account email address")
    client_id: str | None = Field(default=None, title="Client ID", description="Optional client ID of the service account")
    auth_uri: Literal[GoogleStorageConstants.AUTH_URI] = Field(default=GoogleStorageConstants.AUTH_URI.value,
        title="Auth URI", description="OAuth2 auth endpoint URI")
    token_uri: Literal[GoogleStorageConstants.TOKEN_URI] = Field(default=GoogleStorageConstants.TOKEN_URI.value,
        title="Token URI", description="OAuth2 token endpoint URI")
    auth_provider_x509_cert_url: Literal[GoogleStorageConstants.AUTH_PROVIDER_CERT_URL] = Field(
        default=GoogleStorageConstants.AUTH_PROVIDER_CERT_URL.value,
        title="Provider X.509 Cert URL", description="URL for the provider's X.509 certificate")
    universe_domain: Literal[GoogleStorageConstants.UNIVERSE_DOMAIN] = Field(default=GoogleStorageConstants.UNIVERSE_DOMAIN.value,
        title="Universe Domain", description="Domain of the target universe (typically 'googleapis.com')")

    @computed_field
    @property
    def client_x509_cert_url(self) -> str:
        return f"https://www.googleapis.com/robot/v1/metadata/x509/{self.client_email.replace('@', '%40')}"


class GoogleStorageConfiguration(StorageConfiguration):
    type: Literal["gs"] = Field(default="gs", title="Type", description="Indicates the storage type, fixed to 'gs'")
    is_local: Literal[False] = Field(default=False, title='Is a local storage', description="Whether the storage is local or remote")
    bucket: str = Field(title="Bucket name", description="Name of the Google Cloud Storage bucket")
    api_key: GoogleStorageApiKey | None = Field(title="API Key", description="API key for storage authentication", default=None)

    @computed_field
    @property
    def is_anon_client(self) -> bool:
        return self.api_key is None

    @computed_field
    @property
    def credentials_file(self) -> str:
        if not self.is_anon_client:
            with tempfile.NamedTemporaryFile("w+", delete=False) as f:
                json.dump(self.api_key.model_dump(exclude_none=True, exclude_unset=True), f)
                f.close()
            credentials = f.name
        else:
            credentials = None
        return credentials


class HttpStorageConfiguration(StorageConfiguration):
    type: Literal["http"] = Field(default="http", title="Type", description="Indicates the storage type, fixed to 'http'")
    is_local: Literal[False] = Field(default=False, title='Is a local storage', description="Whether the storage is local or remote")
    headers: dict[str, str] = Field(default={}, title="Headers", description="Additional HTTP headers to include in each request")
    domain: str = Field(title="Domain", description="Domain used for HTTP storage endpoint, e.g. 'example.com'")
    force_download: bool = Field(default=False, title="Force Download", description="If true, always download the file instead of caching."
    )


class S3ApiKey(BaseModel):
    access_key: str = Field(title="S3 Access API key", description="Access api key for S3 storage authentication")
    secret_key: str = Field(title="S3 Secret API key", description="Secret api key for S3 storage authentication")


class S3StorageConfiguration(StorageConfiguration):
    type: Literal["s3"] = Field(default="s3", title="Type", description="Indicates the storage type, fixed to 's3'")
    is_local: Literal[False] = Field(default=False, title='Is a local storage', description="Whether the storage is local or remote")
    bucket: str = Field(title="Bucket name", description="Name of the S3 bucket")
    region: str = Field(default="auto", title="Region", description="Region of the bucket")
    endpoint: str = Field(title="Endpoint", description="Endpoint to access S3 storage")
    api_key: S3ApiKey | None = Field(title="API Key", description="API key for storage authentication", default=None)
    max_objects: int = Field(default=1000, title="Max object", description="Maximum number of objects to fetch when listing elements in a directory")

    @computed_field
    @property
    def is_anon_client(self) -> bool:
        return self.api_key is None


class HttpsStorageConfiguration(HttpStorageConfiguration):
    type: Literal["https"] = "https"


AnyStorageConfiguration = Annotated[Union[FileStorageConfiguration, GoogleStorageConfiguration, HttpStorageConfiguration, HttpsStorageConfiguration, S3StorageConfiguration], Field(discriminator="type")]


class AccessManagerSettings(BaseModel):
    storages: list[AnyStorageConfiguration] = Field(title="Storage list", description="List of configurations for the available storages")
    tmp_dir: str = Field(title="Temporary directory", description="Temporary directory in which to write files that will be deleted")
