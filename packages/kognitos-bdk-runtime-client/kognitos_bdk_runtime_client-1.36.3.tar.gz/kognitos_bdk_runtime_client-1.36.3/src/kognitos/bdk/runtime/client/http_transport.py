import base64

import requests

from .base_transport import BaseTransport
from .proto.requests.request_pb2 import \
    Request  # pylint: disable=no-name-in-module
from .proto.responses.response_pb2 import \
    Response  # pylint: disable=no-name-in-module
from .transport import TransportError


class HTTPTransport(BaseTransport):
    def __init__(self, url: str, insecure: bool):
        if url.startswith("http://") and not insecure:
            raise ValueError(
                "You're trying to establish an insecure connection which by default is not allowd. Set the `insecure` flag to True if you intend to use an insecure (http) connection"
            )
        self.url = url

    def get_url(self) -> str:
        return self.url

    def send(self, request: Request) -> Response:
        data_str = request.SerializeToString()
        data = base64.b64encode(data_str).decode("utf-8")
        response = requests.post(self.url, data=data, timeout=900)  # 15 minutes
        response.raise_for_status()

        try:
            response_payload = base64.b64decode(response.text)
            proto_response = Response()
            proto_response.ParseFromString(response_payload)

            return proto_response
        except Exception as e:
            if "response_payload" in locals():
                response = f"response_payload: {locals().get('response_payload')}"
            raise TransportError(
                f"Could not decode the response <<<{response}>>> got by calling(HTTPTransport) <<<{self.url}>>> with the request <<<{request.WhichOneof('request_discriminator')}>>>"
            ) from e
