"""Utils for stack references."""

from __future__ import annotations

from functools import cache
from itertools import chain
from typing import Any, overload

import pulumi
from braceexpand import braceexpand


@cache
def get_stack_reference(ref: str) -> pulumi.StackReference:
    """Resolve given stack reference shorthand to fully qualified stack reference.

    The shorthand can be one of the following:

    - `"{stack}"`

        Returns the stack reference for the current project and organization.

    - `"{project}/{stack}"`

        Returns the stack reference for the current organization.

    - `"{organization}/{project}/{stack}"`

        No change is made to the stack reference.

    """
    fqr = _resolve_stack_ref(ref)
    return pulumi.StackReference(fqr)


def _resolve_stack_ref(ref: str) -> str:
    components = ref.split("/")
    num_components = len(components)
    if num_components == 1:
        org = pulumi.get_organization()
        project = pulumi.get_project()
        fqr = f"{org}/{project}/{ref}"
    elif num_components == 2:  # noqa: PLR2004
        org = pulumi.get_organization()
        fqr = f"{org}/{ref}"
    elif num_components == 3:  # noqa: PLR2004
        fqr = ref
    else:
        msg = f"Invalid stack reference: {ref!r}"
        raise ValueError(msg)

    return fqr


@overload
def get_stack_outputs(ref: str) -> pulumi.Output[Any]: ...  # pragma: no cover


@overload
def get_stack_outputs(*refs: str) -> list[pulumi.Output[Any]]: ...  # pragma: no cover


def get_stack_outputs(  # type: ignore[misc]
    *refs: str,
) -> pulumi.Output[Any] | list[pulumi.Output[Any]]:
    """Get outputs from a output reference shorthands. Supports brace expansion.

    - Single output reference: (`"<stack_ref>:<output_key>"`).
    - Multiple outputs using brace expansion: (`"<stack_ref>:{<output_key_1>,<output_key_2>}"`).

    Args:
        *refs: Output references.

    """
    outputs = _get_stack_outputs(*refs)
    output_values = list(outputs.values())
    if len(output_values) == 1:
        return output_values[0]

    return output_values


def re_export(*refs: str) -> None:
    """Re-export outputs from a output reference shorthands.

    Args:
        *refs: Output references.

    """
    outputs = _get_stack_outputs(*refs)
    for (_, output_key), output in outputs.items():
        pulumi.export(output_key, output)


def _get_stack_outputs(*refs: str) -> dict[tuple[str, str], pulumi.Output[Any]]:
    expand_refs = list(chain.from_iterable(map(braceexpand, refs)))
    pulumi.log.debug(f"Expanded output references ({refs!r}): {expand_refs!r}")

    fqr: list[tuple] = []
    for ref in expand_refs:
        stack_ref, output_key = _resolve_output_ref(ref)
        fqr.append((stack_ref, output_key))

    outputs: dict[tuple[str, str], pulumi.Output[Any]] = {}
    for stack_ref, output_key in fqr:
        sr = get_stack_reference(stack_ref)
        outputs[(stack_ref, output_key)] = sr.require_output(output_key)

    return outputs


def _resolve_output_ref(ref: str) -> tuple[str, str]:
    components = ref.split(":")
    stack_ref, output_key = components
    if not stack_ref or not output_key:
        msg = f"Invalid output reference: {ref!r}"
        raise ValueError(msg)

    return stack_ref, output_key
