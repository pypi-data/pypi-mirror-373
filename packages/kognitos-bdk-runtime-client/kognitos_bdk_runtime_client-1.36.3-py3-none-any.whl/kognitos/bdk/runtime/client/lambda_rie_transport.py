import base64
from typing import Optional

import requests

from .base_transport import BaseTransport
from .proto.requests.request_pb2 import \
    Request  # pylint: disable=no-name-in-module
from .proto.responses.response_pb2 import \
    Response  # pylint: disable=no-name-in-module
from .transport import TransportError


class LambdaRIETransport(BaseTransport):
    def __init__(self, host: str = "localhost", port: Optional[int] = None):

        if host == "localhost":
            if port is None:
                port = 9000

        if not port:
            self.base_url = f"http://{host}/2015-03-31/functions/function/invocations"
        else:
            self.base_url = (
                f"http://{host}:{port}/2015-03-31/functions/function/invocations"
            )

    def get_url(self) -> str:
        return self.base_url

    def send(self, request: Request) -> Response:
        data_str = request.SerializeToString()

        data = base64.b64encode(data_str).decode("utf-8")

        response = requests.post(self.base_url, json=data, timeout=60)

        response.raise_for_status()

        try:
            response_payload = base64.b64decode(response.json())

            response = Response()
            response.ParseFromString(response_payload)

            return response
        except Exception as e:
            if "response_payload" in locals():
                response = f"response_payload: {locals().get('response_payload')}"
            raise TransportError(
                f"Could not decode the response <<<{response}>>> got by calling(LambdaRIETransport) <<<{self.base_url}>>> with the request <<<{request.WhichOneof('request_discriminator')}>>>"
            ) from e
