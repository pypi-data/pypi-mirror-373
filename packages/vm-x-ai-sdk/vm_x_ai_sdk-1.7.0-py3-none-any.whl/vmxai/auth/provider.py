from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vmxai.client import VMXClient


class VMXClientAuthProvider(ABC):

    @abstractmethod
    def inject_credentials(self, client: "VMXClient", grpc_metadata: list[tuple[str, str]]) -> list[tuple[str, str]]:
        raise NotImplementedError("Must implement inject_credentials")
