"""Utility functions for working with Pulumi resources.

References:
- https://github.com/tlinhart/pulumi-aws-tags

"""

from __future__ import annotations

from functools import cache
from importlib import import_module
from inspect import signature
from typing import TYPE_CHECKING

import pulumi
from pulumi.runtime.rpc import _RESOURCE_MODULES

from .errors import UnknownResourceTypeError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


@cache
def resource_has_attribute(resource_type: str, attribute: str) -> bool:
    """Determine if a given GCP resource type is labelable."""
    cls = get_resource_cls(resource_type)
    if cls is None:
        msg = f"Unable to resolve resource type {resource_type!r}"
        raise UnknownResourceTypeError(msg)

    sig = signature(cls._internal_init)
    return attribute in sig.parameters


@cache
def get_resource_cls(resource_type: str) -> Any | None:
    """Get the Pulumi resource class for a given resource type.

    Args:
        resource_type: Resource type to get the class for.

    Returns:
        Pulumi resource class if found, otherwise `None`.

    """
    try:
        _, resource = next(filter(lambda k: k[0] == resource_type, _get_resources()))
    except StopIteration:
        pulumi.log.debug(f"Resource type {resource_type} not found")
        return None

    module_name, class_name = resource
    module = import_module(module_name)
    return getattr(module, class_name)


def _get_resources() -> Iterator[tuple[str, tuple[str, str]]]:
    """Return Pulumi resource registry.

    Returns:
        Iterator of tuple containing resource type and resource class.

    """
    # NOTE: This cannot be cached as the underlying registry (`_RESOURCE_MODULES`) gradually populates
    for modules in _RESOURCE_MODULES.values():
        for module in modules:
            mod_info = module.mod_info  # type: ignore[attr-defined]
            fqn, classes = mod_info["fqn"], mod_info["classes"]
            for type_, name in classes.items():
                # e.g. ("gcp:activedirectory/domain:Domain", ("pulumi_gcp.activedirectory", "Domain"))
                yield (type_, (fqn, name))
