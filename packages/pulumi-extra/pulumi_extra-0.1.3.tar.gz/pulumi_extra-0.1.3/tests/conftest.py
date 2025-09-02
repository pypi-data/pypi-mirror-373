from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest import mock

import pulumi
import pytest

from pulumi_extra import get_resource_cls, get_stack_reference, resource_has_attribute

if TYPE_CHECKING:
    from collections.abc import Iterator


class ResourceMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs) -> Any:
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs) -> Any:  # noqa: ARG002
        return {}


@pytest.fixture(autouse=True)
def pulumi_mocks() -> None:
    """Set up Pulumi mocks."""
    pulumi.runtime.set_mocks(ResourceMocks(), preview=False)


@pytest.fixture(autouse=True)
def pulumi_organization() -> Iterator[None]:
    """Set up Pulumi organization (unless it is `None`)."""
    with mock.patch("pulumi.get_organization") as m:
        m.return_value = "organization"
        yield


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    """Reset cache for each test."""
    resource_has_attribute.cache_clear()
    get_resource_cls.cache_clear()
    get_stack_reference.cache_clear()
