import attrs
from pydantic import BaseModel, Field


class RESTException(BaseModel):
    """
    Model of an exception during a request handling. Used for validation
    """
    type: str
    status: int
    title: str | None = Field(default=None)
    detail: str | None = Field(default=None)
    instance: str | None = Field(default=None)


# Can't use BaseModel due to conflicting inheritances
@attrs.define
class OGCException(Exception):
    """
    Generic python Exception that is OGC API Processes compliant
    """
    type: str
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


@attrs.define
class BadRequest(OGCException):
    type: str = "bad request"
    status: int = 400


@attrs.define
class NotFound(OGCException):
    type: str = "not found"
    status: int = 404


@attrs.define
class Conflict(OGCException):
    type: str = "conflict"
    status: int = 409


@attrs.define
class ServerError(OGCException):
    type: str = "server error"
    status: int = 500
