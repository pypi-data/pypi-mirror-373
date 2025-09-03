# -*- coding: utf-8 -*-

"""
Base model implementation for AWS Lambda objects.

This module provides the foundational data models for the AWS Lambda library,
implementing common patterns for representing and interacting with AWS Lambda resources.
The models follow three key design patterns:

1. **Raw Data Storage Pattern**:

All models store the original API response data in a `_data` attribute, treating the
API response schema as potentially unstable. Properties provide a stable interface
for accessing the underlying data, making the code more resilient to API changes.

2. **Property-Based Access Pattern**:

All attributes are exposed through properties rather than direct instance attributes.
This approach allows for lazy loading, data validation, and type conversion while
maintaining a clean public interface.

3. **Core Data Extraction Pattern**:

Each model implements a `core_data` property that returns a standardized, minimal
representation of the object. This provides a consistent way to access essential
information across different model types.

These models are designed to be instantiated by the API client methods, not directly
by users of the library. They provide a Pythonic interface to the JSON data returned
by the native boto3 AWS Lambda API.
"""

import typing as T
import dataclasses
from datetime import datetime, timezone

from func_args.api import T_KWARGS, REQ
from iterproxy import IterProxy

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.type_defs import (
        LayersListItemTypeDef,
        LayerVersionsListItemTypeDef,
        GetLayerVersionResponseTypeDef,
        LayerVersionContentOutputTypeDef,
    )


@dataclasses.dataclass(frozen=True)
class Base:
    _data: dict[str, T.Any] = dataclasses.field(default=REQ)

    @property
    def core_data(self) -> T_KWARGS:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class LatestMatchingLayerVersion(Base):
    """
    Represents the latest matching version of a Lambda layer.

    Ref:

    - `list_layers <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layers.html>`_

    :param _data: Raw data structure as returned by AWS SDK

        {
            'LayerVersionArn': 'string',
            'Version': 123,
            'Description': 'string',
            ...
        }
    """

    _data: "LayerVersionsListItemTypeDef" = dataclasses.field(default=REQ)

    @property
    def layer_version_arn(self) -> str | None:
        """The ARN of the layer version."""
        return self._data["LayerVersionArn"]

    @property
    def version(self) -> int | None:
        """The version number of the layer."""
        return self._data["Version"]

    @property
    def description(self) -> str | None:
        """The description of the layer version."""
        return self._data.get("Description")

    @property
    def created_date(self) -> str | None:
        """The date that the layer version was created (ISO 8601 format)."""
        return self._data.get("CreatedDate")

    @property
    def compatible_runtimes(self) -> list[str] | None:
        """The layer's compatible runtimes."""
        return self._data.get("CompatibleRuntimes")

    @property
    def license_info(self) -> str | None:
        """The layer's software license."""
        return self._data.get("LicenseInfo")

    @property
    def compatible_architectures(self) -> list[str] | None:
        """A list of compatible instruction set architectures."""
        return self._data.get("CompatibleArchitectures")

    @property
    def has_python_runtime(self) -> bool:
        """Check if this layer version supports any Python runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("python") for runtime in self.compatible_runtimes)

    @property
    def has_nodejs_runtime(self) -> bool:
        """Check if this layer version supports any Node.js runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("nodejs") for runtime in self.compatible_runtimes)

    @property
    def supports_arm64(self) -> bool:
        """Check if this layer version supports ARM64 architecture."""
        if not self.compatible_architectures:
            return False
        return "arm64" in self.compatible_architectures

    @property
    def supports_x86_64(self) -> bool:
        """Check if this layer version supports x86_64 architecture."""
        if not self.compatible_architectures:
            return False
        return "x86_64" in self.compatible_architectures

    @property
    def core_data(self) -> T_KWARGS:
        """Extract core data for standardized representation."""
        return {
            "layer_version_arn": self.layer_version_arn,
            "version": self.version,
            "description": self.description,
            "created_date": self.created_date,
            "compatible_runtimes": self.compatible_runtimes,
            "compatible_architectures": self.compatible_architectures,
        }


@dataclasses.dataclass(frozen=True)
class Layer(Base):
    """
    Represents an AWS Lambda layer.

    Ref:

    - `list_layers <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layers.html>`_

    :param _data: Raw data structure as returned by AWS SDK:

    .. code-block:: python

        {
            'LayerName': 'string',
            'LayerArn': 'string',
            'LatestMatchingVersion': {
                ...
            }
        }
    """

    _data: "LayersListItemTypeDef" = dataclasses.field(default=REQ)

    @property
    def layer_name(self) -> str:
        """The name of the layer."""
        return self._data["LayerName"]

    @property
    def layer_arn(self) -> str:
        """The Amazon Resource Name (ARN) of the layer."""
        return self._data["LayerArn"]

    @property
    def latest_matching_version(self) -> LatestMatchingLayerVersion | None:
        """The latest matching version of the layer."""
        version_data = self._data.get("LatestMatchingVersion")
        if version_data:
            return LatestMatchingLayerVersion(_data=version_data)
        return None

    @property
    def has_latest_version(self) -> bool:
        """Check if this layer has a latest matching version."""
        return self.latest_matching_version is not None

    @property
    def core_data(self) -> T_KWARGS:
        """Extract core data for standardized representation."""
        return {
            "layer_name": self.layer_name,
            "layer_arn": self.layer_arn,
        }


class LayerIterproxy(IterProxy[Layer]):
    """
    Iterator proxy for collections of Layer objects with enhanced iteration capabilities.
    """


@dataclasses.dataclass(frozen=True)
class LayerContent(Base):
    """
    Represents the content details of a Lambda layer version.

    :param _data: Raw data structure as returned by AWS SDK:

    .. code-block:: python

        {
            'Location': 'string',
            'CodeSha256': 'string',
            'CodeSize': 123,
            'SigningProfileVersionArn': 'string',
            'SigningJobArn': 'string'
        }
    """

    _data: "LayerVersionContentOutputTypeDef" = dataclasses.field()

    @property
    def location(self) -> str | None:
        """A link to the layer archive in Amazon S3 that is valid for 10 minutes."""
        return self._data.get("Location")

    @property
    def code_sha256(self) -> str | None:
        """The SHA-256 hash of the layer archive."""
        return self._data.get("CodeSha256")

    @property
    def code_size(self) -> int | None:
        """The size of the layer archive in bytes."""
        return self._data.get("CodeSize")

    @property
    def signing_profile_version_arn(self) -> str | None:
        """The Amazon Resource Name (ARN) for a signing profile version."""
        return self._data.get("SigningProfileVersionArn")

    @property
    def signing_job_arn(self) -> str | None:
        """The Amazon Resource Name (ARN) of a signing job."""
        return self._data.get("SigningJobArn")

    @property
    def core_data(self) -> T_KWARGS:
        """Extract core data for standardized representation."""
        return {
            "location": self.location,
            "code_sha256": self.code_sha256,
            "code_size": self.code_size,
        }


@dataclasses.dataclass(frozen=True)
class LayerVersion(Base):
    """
    Represents a specific version of an AWS Lambda layer.

    Ref:

    - `list_layer_versions <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layer_versions.html>`_
    - `get_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_layer_version.html>`_

    :param _data: Raw data structure as returned by AWS SDK:

    .. code-block:: python

        {
            'LayerVersionArn': 'string',
            'Version': 123,
            'Description': 'string',
            ...
        }
        # or (from get_layer_version)
        {
            'Content': {
                'Location': 'string',
                'CodeSha256': 'string',
                'CodeSize': 123,
                'SigningProfileVersionArn': 'string',
                'SigningJobArn': 'string'
            },
            'LayerArn': 'string',
            'LayerVersionArn': 'string',
            'Description': 'string',
            ...
        }
    """

    # fmt: off
    _data: T.Union["LayerVersionsListItemTypeDef", "GetLayerVersionResponseTypeDef"] = dataclasses.field(default=REQ)
    # fmt: on

    @property
    def layer_version_arn(self) -> str:
        """The ARN of the layer version."""
        return self._data["LayerVersionArn"]

    @property
    def version(self) -> int:
        """The version number of the layer."""
        return self._data["Version"]

    @property
    def description(self) -> str | None:
        """The description of the layer version."""
        return self._data.get("Description")

    @property
    def created_date(self) -> str | None:
        """The date that the layer version was created (ISO 8601 format)."""
        return self._data.get("CreatedDate")

    @property
    def compatible_runtimes(self) -> list[str] | None:
        """The layer's compatible runtimes."""
        return self._data.get("CompatibleRuntimes")

    @property
    def license_info(self) -> str | None:
        """The layer's software license."""
        return self._data.get("LicenseInfo")

    @property
    def compatible_architectures(self) -> list[str] | None:
        """A list of compatible instruction set architectures."""
        return self._data.get("CompatibleArchitectures")

    @property
    def layer_arn(self) -> str | None:
        """The ARN of the layer (only available from get_layer_version)."""
        return self._data.get("LayerArn")

    # Content-related properties (only available from get_layer_version)
    @property
    def content(self) -> LayerContent | None:
        """Information about the layer's deployment package (only from get_layer_version)."""
        content_data = self._data.get("Content")
        if content_data:
            return LayerContent(_data=content_data)
        return None

    @property
    def created_datetime(self) -> datetime:
        """
        Convert the created_date string to a datetime object.
        """
        dt = datetime.fromisoformat(self.created_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    @property
    def layer_name(self) -> str:
        """Extract the layer name from the layer version ARN."""
        return self.layer_version_arn.split(":")[-2]

    @property
    def has_content_details(self) -> bool:
        """Check if this layer version includes content details (from get_layer_version)."""
        return self.content is not None

    # Computed properties for runtime and architecture checks
    @property
    def has_python_runtime(self) -> bool:
        """Check if this layer version supports any Python runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("python") for runtime in self.compatible_runtimes)

    @property
    def has_nodejs_runtime(self) -> bool:
        """Check if this layer version supports any Node.js runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("nodejs") for runtime in self.compatible_runtimes)

    @property
    def has_java_runtime(self) -> bool:
        """Check if this layer version supports any Java runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("java") for runtime in self.compatible_runtimes)

    @property
    def has_dotnet_runtime(self) -> bool:
        """Check if this layer version supports any .NET runtime."""
        if not self.compatible_runtimes:
            return False
        return any(
            runtime.startswith("dotnetcore") or runtime.startswith("dotnet")
            for runtime in self.compatible_runtimes
        )

    @property
    def has_go_runtime(self) -> bool:
        """Check if this layer version supports Go runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("go") for runtime in self.compatible_runtimes)

    @property
    def has_ruby_runtime(self) -> bool:
        """Check if this layer version supports any Ruby runtime."""
        if not self.compatible_runtimes:
            return False
        return any(runtime.startswith("ruby") for runtime in self.compatible_runtimes)

    @property
    def has_provided_runtime(self) -> bool:
        """Check if this layer version supports provided runtime."""
        if not self.compatible_runtimes:
            return False
        return any(
            runtime.startswith("provided") for runtime in self.compatible_runtimes
        )

    @property
    def supports_arm64(self) -> bool:
        """Check if this layer version supports ARM64 architecture."""
        if not self.compatible_architectures:
            return False
        return "arm64" in self.compatible_architectures

    @property
    def supports_x86_64(self) -> bool:
        """Check if this layer version supports x86_64 architecture."""
        if not self.compatible_architectures:
            return False
        return "x86_64" in self.compatible_architectures

    @property
    def supports_multi_arch(self) -> bool:
        """Check if this layer version supports multiple architectures."""
        return self.supports_arm64 and self.supports_x86_64

    @property
    def runtime_count(self) -> int:
        """Number of compatible runtimes."""
        return len(self.compatible_runtimes) if self.compatible_runtimes else 0

    @property
    def architecture_count(self) -> int:
        """Number of compatible architectures."""
        return (
            len(self.compatible_architectures) if self.compatible_architectures else 0
        )

    @property
    def core_data(self) -> T_KWARGS:
        """Extract core data for standardized representation."""
        return {
            "layer_version_arn": self.layer_version_arn,
            "layer_arn": self.layer_arn,
            "version": self.version,
            "description": self.description,
            "created_date": self.created_date,
            "compatible_runtimes": self.compatible_runtimes,
            "compatible_architectures": self.compatible_architectures,
        }


class LayerVersionIterproxy(IterProxy[LayerVersion]):
    """
    Iterator proxy for collections of LayerVersion objects with enhanced iteration capabilities.
    """
