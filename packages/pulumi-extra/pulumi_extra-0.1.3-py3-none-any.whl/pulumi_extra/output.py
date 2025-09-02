"""Utils for outputs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, overload

import pulumi
from jinja2 import StrictUndefined, Template

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


@overload
def render_template(
    template: Path | str,
    *,
    context: Mapping[str, Any],
) -> str: ...  # pragma: no cover


@overload
def render_template(
    template: Path | str,
    *,
    inputs: Mapping[str, pulumi.Input[Any]],
) -> pulumi.Output[str]: ...  # pragma: no cover


def render_template(
    template: Path | str,
    *,
    context: Mapping[str, Any] | None = None,
    inputs: Mapping[str, pulumi.Input[Any]] | None = None,
) -> str | pulumi.Output[str]:
    """Render a template file with the given context.

    Args:
        template: The template file or inline template string.
        context: The context to render the template with. Conflicts with inputs.
        inputs: The inputs to render the template with. Conflicts with context.
    """
    if isinstance(template, Path):
        template = template.read_text()

    jinja_tpl = Template(template, undefined=StrictUndefined)

    # Render with Python values.
    if context is not None and inputs is None:
        return jinja_tpl.render(context)

    # Render with Pulumi inputs.
    if context is None and inputs is not None:
        return pulumi.Output.all(inputs).apply(lambda args: jinja_tpl.render(args[0]))

    # Only one of context or inputs must be provided.
    msg = "Either context or input must be provided."
    raise ValueError(msg)
