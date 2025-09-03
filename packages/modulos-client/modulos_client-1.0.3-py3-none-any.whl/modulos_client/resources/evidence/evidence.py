from .upload import Upload
from ..._resource import SyncAPIResource


class Evidence(SyncAPIResource):

    @property
    def upload(self) -> Upload:
        return Upload(self._client)
