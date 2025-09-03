import base64
import json
import os
from typing import Any, Optional
from typing import BinaryIO
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Union

import urllib3  # type: ignore
import yarl

from _h2o_mlops_client.bytestream import api
from _h2o_mlops_client.bytestream import api_client
from _h2o_mlops_client.bytestream import exceptions
from _h2o_mlops_client.bytestream import models
from _h2o_mlops_client.bytestream.exceptions import *  # noqa: F403, F401


def stream_write_messages(
    resource_name: str, file: BinaryIO, chunk_size: int
) -> Generator[Dict[str, Union[str, int]], None, None]:
    """Generates message for the stream of chunks for ByteStream API."""

    write_offset = 0
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield {
            "resourceName": resource_name,
            "writeOffset": write_offset,
            "data": base64.b64encode(data).decode("ascii"),
        }
        write_offset += len(data)

    yield {
        "resourceName": resource_name,
        "writeOffset": write_offset,
        "finishWrite": True,
    }


def stream_write_json(
    resource_name: str, file: BinaryIO, chunk_size: int
) -> Generator[str, None, None]:
    """Generates newline separated chunks of serialized  data chunks
    for the ByteStream API.
    """

    for message in stream_write_messages(
        resource_name=resource_name, file=file, chunk_size=chunk_size
    ):
        yield json.dumps(message) + "\n"


class ExtendedByteStreamApi(api.ByteStreamApi):
    """Extends generated api.ByteStreamApi with methods implementing streamed
    upload and download.
    """

    def upload_file(
        self, resource_name: str, file: BinaryIO, *, chunk_size: int = 32 * 1024
    ) -> models.BytestreamWriteResponse:
        """Uploads the content of the file as a blob.

        Data are streamed to the gateway in chunks.

        Args:
            resource_name: Identifier of the entity the upload belongs to.
            file: Readable BinaryIO with the content to be uploaded.
            chunk_size: Size of the chunk used for the streaming upload.
        """
        headers: Dict[str, str] = {}
        self.api_client.update_params_for_auth(headers, None, None)
        url = yarl.URL(self.api_client.configuration.host)
        url = url / "google.bytestream.ByteStream/Write"

        try:
            resp = self.api_client.rest_client.pool_manager.request(
                method="POST",
                url=str(url),
                body=stream_write_json(
                    resource_name=resource_name, file=file, chunk_size=chunk_size
                ),
                headers=headers,
                chunked=True,
            )
        except urllib3.exceptions.SSLError as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            raise exceptions.ApiException(status=0, reason=msg)

        if not 200 <= resp.status <= 299:
            raise exceptions.ApiException(http_resp=resp)

        return self.api_client.deserialize(resp, "BytestreamWriteResponse")

    def download_file(self, resource_name: str, file: BinaryIO) -> None:
        """Downloads the the blob from the server and saves it to the file.

        Args:
            resource_name: Identifier of the entity blob is associated with.
            file: Writable BinaryIO that will be used to save the blob content.
        """

        headers: Dict[str, str] = {}
        self.api_client.update_params_for_auth(headers, None, None)
        url = yarl.URL(self.api_client.configuration.host)
        url = url / "google.bytestream.ByteStream/Read"

        resp = self.api_client.rest_client.request(
            method="POST",
            url=str(url),
            body={"resourceName": resource_name},
            headers=headers,
            _preload_content=False,
        )

        for line in resp.readlines():
            msg = json.loads(line)
            file.write(base64.b64decode(msg["result"]["data"]))


class ApiClient(api_client.ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

    def __init__(
        self, configuration: api_client.Configuration, token_provider: Callable[[], str]
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self, headers: Any, querys: Any, auth_settings: Any, request_auth: Any = None
    ) -> None:
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"


class Client:
    """The composite client for accessing Google Bytestream services in storage."""

    def __init__(
        self,
        host: str,
        token_provider: Callable[[], str],
        verify_ssl: bool = True,
        ssl_cacert: Optional[str] = None,
    ):
        configuration = api_client.Configuration(
            host=host,
        )
        configuration.verify_ssl = verify_ssl
        ssl_ca_cert = ssl_cacert or os.getenv("MLOPS_AUTH_CA_FILE_OVERRIDE")
        if ssl_ca_cert:
            configuration.ssl_ca_cert = ssl_ca_cert

        client = ApiClient(
            configuration=configuration,
            token_provider=token_provider,
        )

        self._bytestream = ExtendedByteStreamApi(api_client=client)

    @property
    def bytestream(self) -> ExtendedByteStreamApi:
        return self._bytestream
