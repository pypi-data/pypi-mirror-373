"""Runtime-level transforms for Pulumi programs."""

from __future__ import annotations

import pulumi

from .invoke import override_invoke_options
from .resource_ import override_resource_options


def override_default_provider(
    *rt_or_it: str,
    provider: pulumi.ProviderResource,
) -> None:
    """Override the default provider for resources and invokes of given types.

    Args:
        *rt_or_it: Resource types or invoke tokens to match.
        provider: Provider to override.

    """
    pulumi.runtime.register_resource_transform(override_resource_options(*rt_or_it, provider=provider))
    pulumi.runtime.register_invoke_transform(override_invoke_options(*rt_or_it, provider=provider))
