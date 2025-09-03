# -*- coding: utf-8 -*-

"""
Improve the original redshift boto3 API.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
"""

import typing as T

import botocore.exceptions
from func_args.api import OPT, remove_optional

from .model import (
    LatestMatchingLayerVersion,
    Layer,
    LayerContent,
    LayerVersion,
    LayerIterproxy,
    LayerVersionIterproxy,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.client import LambdaClient


def list_layers(
    lambda_client: "LambdaClient",
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
    page_size: int = 50,
) -> LayerIterproxy:
    """
    List available AWS Lambda layers in the account.

    Ref:

    - `list_layers <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layers.html>`_
    """

    def func():
        paginator = lambda_client.get_paginator("list_layers")
        response_iterator = paginator.paginate(
            **remove_optional(
                CompatibleRuntime=compatible_runtime,
                CompatibleArchitecture=compatible_architecture,
                PaginationConfig={
                    "MaxItems": max_items,
                    "PageSize": page_size,
                },
            )
        )
        for response in response_iterator:
            for _data in response.get("Layers", []):
                yield Layer(_data=_data)

    return LayerIterproxy(func())


def list_layer_versions(
    lambda_client: "LambdaClient",
    layer_name: str,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
    page_size: int = 50,
    _sort_descending: bool = False,
) -> LayerVersionIterproxy:
    """
    List all versions of Lambda layers in the account.

    :param _sort_descending: if True, load all layer versions in to memory and
        then sort them in memory in descending order by version number. This is
        the default behavior of official AWS API. However, the test tool moto does not
        implement it correctly (it returns in ascending order). So this parameter
        is a workaround for moto only. You don't need to set this parameter
        when you run against real AWS API.

    .. note::

        this API always returns the latest version first.

    Ref:

    - `list_layer_versions <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layer_versions.html>`_
    """

    def func():
        paginator = lambda_client.get_paginator("list_layer_versions")
        response_iterator = paginator.paginate(
            **remove_optional(
                LayerName=layer_name,
                CompatibleRuntime=compatible_runtime,
                CompatibleArchitecture=compatible_architecture,
                PaginationConfig={
                    "MaxItems": max_items,
                    "PageSize": page_size,
                },
            )
        )
        for response in response_iterator:
            for _data in response.get("LayerVersions", []):
                yield LayerVersion(_data=_data)

    if _sort_descending:
        return LayerVersionIterproxy(
            sorted(
                func(),
                key=lambda v: v.version,
                reverse=True,
            )
        )
    else:
        return LayerVersionIterproxy(func())



def get_layer_version(
    lambda_client: "LambdaClient",
    layer_name: str,
    version_number: int,
) -> LayerVersion | None:
    """
    Retrieve details for a specific Lambda layer version.

    Ref:

    - `get_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_layer_version.html>`_
    """
    try:
        response = lambda_client.get_layer_version(
            LayerName=layer_name,
            VersionNumber=version_number,
        )
        return LayerVersion(_data=response)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        raise  # pragma: no cover
