# -*- coding: utf-8 -*-

import typing as T
import enum
from datetime import datetime, timezone, timedelta

import botocore.exceptions
from func_args.api import OPT, remove_optional

from .model import (
    LayerVersion,
)
from .client import (
    list_layer_versions,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.client import LambdaClient
    from mypy_boto3_lambda.type_defs import (
        AddLayerVersionPermissionResponseTypeDef,
    )


def get_latest_layer_version(
    lambda_client: "LambdaClient",
    layer_name: str,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    _sort_descending: bool = False,
) -> LayerVersion | None:
    """
    Call the AWS Lambda Layer API to retrieve the latest deployed layer version.
    If it returns ``None``, it indicates that no layer has been deployed yet.

    Example: if layer has version 1, 2, 3, then this function return 3.
    If there's no layer version created yet, then this function returns None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_layer_versions
    """
    if _sort_descending:
        max_items = 10
    else:
        max_items = 1
    layer_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        compatible_runtime=compatible_runtime,
        compatible_architecture=compatible_architecture,
        max_items=max_items,
        _sort_descending=_sort_descending,
    ).all()
    if len(layer_versions) == 0:
        return None
    else:
        return layer_versions[0]


def cleanup_old_layer_versions(
    lambda_client: "LambdaClient",
    layer_name: str,
    keep_last_n_versions: int = 5,
    keep_versions_newer_than_seconds: int = 90 * 24 * 60 * 60,
    real_run: bool = False,
    _sort_descending: bool = False,
) -> list[int]:
    """
    Delete old Lambda layer versions based on retention policy.

    Keeps layer versions if they meet ANY of these conditions:

    - Among the last N versions (most recent)
    - Created within the last N seconds

    :param lambda_client: AWS Lambda client
    :param layer_name: Name of the Lambda layer
    :param keep_last_n_versions: Number of most recent versions to keep
    :param keep_versions_newer_than_seconds: Keep versions newer than this many seconds
    :param real_run: If True, actually delete versions. If False, only return what would be deleted

    :returns: List of version numbers that were deleted (or would be deleted in simulation mode)

    Ref:

    - `delete_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/delete_layer_version.html>`_
    """
    # Get all layer versions
    all_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        max_items=9999,
        _sort_descending=True,
    ).all()

    # Only exam versions beyond the last N to keep
    other_versions = all_versions[keep_last_n_versions:]

    if len(other_versions) == 0:
        return []

    # Calculate cutoff date
    delta = timedelta(seconds=keep_versions_newer_than_seconds)
    cutoff_date = datetime.now(timezone.utc) - delta

    versions_to_delete = []

    for version in other_versions:
        # Keep if it's newer than cutoff date
        if version.created_datetime > cutoff_date:  # pragma: no cover
            continue

        # This version should be deleted
        versions_to_delete.append(version.version)

    # Delete the versions (if real_run is True)
    deleted_versions = []
    for version_number in versions_to_delete:
        deleted_versions.append(version_number)
        if real_run:
            try:
                lambda_client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version_number,
                )
            except botocore.exceptions.ClientError:  # pragma: no cover
                # Continue with other versions even if one fails
                pass

    return deleted_versions


class LambdaPermissionActionEnum(str, enum.Enum):
    """
    Enum for different Lambda layer permission actions.

    See: https://docs.aws.amazon.com/lambda/latest/dg/permissions-layer-cross-account.html
    """
    get_layer_version = "lambda:GetLayerVersion"
    list_layer_versions = "lambda:ListLayerVersions"


# Map action to a more human friendly name for statement id naming convention
action_to_name_mapper: T.Dict[str, str] = {
    LambdaPermissionActionEnum.get_layer_version.value: "GetLayerVersion",
    LambdaPermissionActionEnum.list_layer_versions.value: "ListLayerVersions",
}


class LayerPrincipalTypeEnum(str, enum.Enum):
    """
    Enum for different types of layer principals.

    Based on this AWS doc https://docs.aws.amazon.com/lambda/latest/dg/permissions-layer-cross-account.html
    There are only three cross account Lambda layer permission patterns
    The grant_aws_account_or_aws_organization_lambda_layer_version_access
    and revoke_aws_account_or_aws_organization_lambda_layer_version_access
    recipes only support these three patterns.
    """
    public = "public"
    aws_account = "aws_account"
    aws_organization = "aws_organization"


def identify_principal_type(principal: str) -> LayerPrincipalTypeEnum:
    """
    Identify the type of principal based on its format.

    :param principal: The principal string to identify:
        - "*" for public access
        - "123456789012" for specific AWS account (12-digit account ID)
        - "o-example123456" for AWS organization ID

    :returns: The identified LayerPrincipalTypeEnum
    """
    if principal == "*":
        return LayerPrincipalTypeEnum.public
    elif principal.isdigit() and len(principal) == 12:
        return LayerPrincipalTypeEnum.aws_account
    elif principal.startswith("o-"):
        return LayerPrincipalTypeEnum.aws_organization
    else:  # pragma: no cover
        raise ValueError(f"Invalid principal format: {principal}")


def get_layer_permission_statement_id(
    action: str,
    principal: str,
) -> str:
    """
    Encode the statement ID for Lambda layer permission based on action and principal.
    """
    name = action_to_name_mapper[action]
    return f"allow-{principal}-{name}"


def grant_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client: "LambdaClient",
    layer_name: str,
    version_number: int,
    principal: str,
):
    """
    Grant other AWS accounts Lambda layer access to a specific layer version.

    Idempotent version of the AWS Lambda add_layer_version_permission API that
    automatically handles statement ID generation and manages conflicts by
    allowing existing permissions to remain.

    Grants both GetLayerVersion and ListLayerVersions permissions to the specified
    principal (AWS account, AWS organization, or public access).

    :param lambda_client: AWS Lambda client for the account that owns the layer
    :param layer_name: Name of the Lambda layer
    :param version_number: Version number of the layer to grant access to
    :param principal: Principal to grant access to:
        - "*" for public access
        - "123456789012" for specific AWS account (12-digit account ID)
        - "o-example123456" for AWS organization ID

    Ref:

    - `add_layer_version_permission <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/add_layer_version_permission.html>`_
    """
    layer_principal_type = identify_principal_type(principal)
    if layer_principal_type == LayerPrincipalTypeEnum.public:  # pragma: no cover
        kwargs = {"Principal": principal}
    elif layer_principal_type == LayerPrincipalTypeEnum.aws_account:  # pragma: no cover
        kwargs = {"Principal": principal}
    elif (
        layer_principal_type == LayerPrincipalTypeEnum.aws_organization
    ):  # pragma: no cover
        kwargs = {
            "Principal": "*",
            "OrganizationId": principal,
        }
    else:  # pragma: no cover
        raise ValueError(f"Unsupported principal type: {principal}")

    def add_layer_version_permission(action: str):
        statement_id = get_layer_permission_statement_id(
            action=action,
            principal=principal,
        )
        try:
            lambda_client.add_layer_version_permission(
                LayerName=layer_name,
                VersionNumber=version_number,
                StatementId=statement_id,
                Action=action,
                **kwargs,
            )
        except botocore.exceptions.ClientError as e:  # pragma: no cover
            if e.response["Error"]["Code"] == "ResourceConflictException":
                pass
            else:
                raise

    add_layer_version_permission(LambdaPermissionActionEnum.get_layer_version.value)
    add_layer_version_permission(LambdaPermissionActionEnum.list_layer_versions.value)


def revoke_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client: "LambdaClient",
    layer_name: str,
    version_number: int,
    principal: str,
):
    """
    Revoke AWS accounts Lambda layer access from a specific layer version.

    Idempotent version of the AWS Lambda remove_layer_version_permission API that
    automatically handles statement ID generation and gracefully handles cases
    where permissions don't exist.

    Removes both GetLayerVersion and ListLayerVersions permissions from the
    specified principal (AWS account, AWS organization, or public access).

    :param lambda_client: AWS Lambda client for the account that owns the layer
    :param layer_name: Name of the Lambda layer
    :param version_number: Version number of the layer to revoke access from
    :param principal: Principal to revoke access from:
        - "*" for public access
        - "123456789012" for specific AWS account (12-digit account ID)
        - "o-example123456" for AWS organization ID

    Ref:

    - `remove_layer_version_permission <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/remove_layer_version_permission.html>`_
    """
    identify_principal_type(principal)

    def remove_layer_version_permission(action: str):
        statement_id = get_layer_permission_statement_id(
            action=action,
            principal=principal,
        )
        try:
            lambda_client.remove_layer_version_permission(
                LayerName=layer_name,
                VersionNumber=version_number,
                StatementId=statement_id,
            )
        except botocore.exceptions.ClientError as e:  # pragma: no cover
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                pass
            else:
                raise

    remove_layer_version_permission(LambdaPermissionActionEnum.get_layer_version.value)
    remove_layer_version_permission(
        LambdaPermissionActionEnum.list_layer_versions.value
    )
