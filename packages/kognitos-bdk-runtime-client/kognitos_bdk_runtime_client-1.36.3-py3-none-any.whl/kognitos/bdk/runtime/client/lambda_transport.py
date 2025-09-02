import base64
import time
from functools import wraps
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from kognitos.bdk.runtime.client.base_transport import BaseTransport

from .proto.requests.request_pb2 import \
    Request  # pylint: disable=no-name-in-module
from .proto.responses.response_pb2 import \
    Response  # pylint: disable=no-name-in-module
from .transport import TransportError

# Extend timeouts & enable keep-alive
DEFAULT_CONFIG = Config(
    retries={"max_attempts": 0},  # No automatic retries
    connect_timeout=900,  # Max Lambda runtime (15 min)
    read_timeout=900,  # Wait up to 15 min for response
)


class RetryLimitExceededException(Exception):
    """Exception raised when the maximum number of retries is exceeded."""


def retry(backoff_factor, max_retries):
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    if "lambda is initializing your function" in str(e).lower():
                        sleep_time = backoff_factor**retries
                        time.sleep(sleep_time)
                        retries += 1
                    else:
                        raise
            raise RetryLimitExceededException(
                f"Failed to invoke function after {max_retries} retries"
            )

        return wrapper

    return decorator_retry


class LambdaTransport(BaseTransport):
    def __init__(
        self,
        function_name: str,
        sleep_retry_time: float = 10.0,
        config: Optional[Config] = None,
    ):
        self.lambda_client = boto3.client("lambda", config=config or DEFAULT_CONFIG)
        self.function_name = function_name
        self.sleep_retry_time = sleep_retry_time

    def get_url(self) -> str:
        return self.function_name

    def send(self, request: Request) -> Response:
        invoke_function = retry(backoff_factor=self.sleep_retry_time, max_retries=3)(
            self._invoke_function
        )
        return invoke_function(request)

    def _invoke_function(self, request: Request) -> Response:
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            Payload=f'"{base64.b64encode(request.SerializeToString()).decode("utf-8")}"',
        )

        try:
            raw_response = response["Payload"].read().decode("utf-8").replace('"', "")

            response_payload = base64.b64decode(raw_response, validate=True)

            return Response.FromString(response_payload)
        except Exception as e:
            if "response_payload" in locals():
                response = f"response_payload: {locals().get('response_payload')}"
            elif "raw_response" in locals():
                response = f"raw_response: {locals().get('raw_response')}"
            raise TransportError(
                f"Could not decode the response <<<{response}>>> got by calling(LambdaTransport) <<<{self.function_name}>>> with the request <<<{request.WhichOneof('request_discriminator')}>>>"
            ) from e
