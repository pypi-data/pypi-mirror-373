"""from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _client import Modulos"""


class SyncAPIResource:

    def __init__(self, client) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._delete = client.delete
