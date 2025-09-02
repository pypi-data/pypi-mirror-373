from typing import Optional, Tuple

from . import configs


def build_lambda_arn(lambda_url: str, aws_region: str, aws_account_id: str) -> str:
    try:
        lambda_name, lambda_version = lambda_url.split("lambda://")[1].split("/")

        if not lambda_name or not lambda_version:
            raise ValueError()

        full_name = f"{lambda_name}_{lambda_version.replace('.', '_')}_lambda"
        return f"arn:aws:lambda:{aws_region}:{aws_account_id}:function:{full_name}"
    except ValueError as exc:
        raise ValueError(
            "The 'lambda://' url schema must follow the pattern 'lambda://<aws-lambda-name>/<aws-lambda-version>'"
        ) from exc


def get_host_and_port_from_lambda_rie_url(
    lambda_rie_url: str,
) -> Tuple[str, Optional[int]]:
    try:
        host, *port = (
            lambda_rie_url.split("lambda+rie://")[1].replace("/", "").split(":")
        )
        if not host:
            raise ValueError()

        if not port:
            return host, None

        return host, int(port[0])
    except ValueError as exc:
        raise ValueError(
            "The 'lambda+rie://' url schema must follow the pattern 'lambda+rie://<host>:<port>' or 'lambda+rie://<host>'"
        ) from exc


#
# BCI Protocol version checking
#


def parse_semver(semver: str) -> Tuple[int, int, int]:
    major, minor, patch = semver.split(".")
    return int(major), int(minor), int(patch)


def is_semver_gte(version: str, target: str) -> bool:
    v1 = parse_semver(version)
    v2 = parse_semver(target)
    return v1 >= v2


def is_bci_protocol_version_supported(version: str) -> bool:
    return is_semver_gte(version, configs.BCI_PROTO_VERSION_FLOOR)


def build_grpc_url(url: str) -> str:
    return url[7:] if url.startswith("grpc://") else url
