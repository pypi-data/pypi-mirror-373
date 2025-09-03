from .logs import Logs

from ..._resource import SyncAPIResource

__all__ = ["Testing"]


class Testing(SyncAPIResource):

    @property
    def logs(self) -> Logs:
        return Logs(self._client)
