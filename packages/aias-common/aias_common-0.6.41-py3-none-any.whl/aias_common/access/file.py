from pydantic import BaseModel
from datetime import datetime


class File(BaseModel):
    name: str
    path: str
    is_dir: bool
    last_modification_date: datetime | None = None
    creation_date: datetime | None = None
    metadata: dict[str, str] = {}
