from typing import TYPE_CHECKING, TypeVar, Union

from vmxai.auth.provider import VMXClientAuthProvider

if TYPE_CHECKING:
    from vmxai.client import VMXClient


Injetable = TypeVar("Injetable", bound=Union[list[tuple[str, str]], dict[str, str]])


class VMXClientAPIKey(VMXClientAuthProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def inject_credentials(self, client: "VMXClient", grpc_metadata_or_headers: Injetable) -> Injetable:
        if isinstance(grpc_metadata_or_headers, list):
            grpc_metadata_or_headers.append(("x-api-key", self.api_key))
        elif isinstance(grpc_metadata_or_headers, dict):
            grpc_metadata_or_headers["x-api-key"] = self.api_key

        return grpc_metadata_or_headers
