from typing import Literal

from aias_common.access.storages.http import HttpStorage


class HttpsStorage(HttpStorage):
    type: Literal["https"] = "https"
