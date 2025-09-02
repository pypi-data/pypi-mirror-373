"""Pulumi invoke transforms.

Invoke transforms should be register at the runtime level because Pulumi doesn't support
registering invoke transforms per-invoke basis.
"""

from __future__ import annotations

from fnmatch import fnmatch
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable

import pulumi
from braceexpand import braceexpand

_Args = dict[str, pulumi.Input[Any]]


def override_invoke(
    *invoke_tokens: str,
    args: _Args | Callable[[_Args], _Args] | None = None,
    opts: pulumi.InvokeOptions | Callable[[pulumi.InvokeOptions], pulumi.InvokeOptions] | None = None,
) -> pulumi.InvokeTransform:
    """Pulumi transform factory for invoke tokens (`get_*`).

    Args:
        *invoke_tokens: Invoke tokens to match. Supports glob patterns and brace expand.
        args: Invoke arguments to override, or a callable that returns the new arguments from given `args.args` input.
        opts: Invoke options to override, or a callable that returns the new options given `args.opts` input.

    """
    args_ = args

    def transform(args: pulumi.InvokeTransformArgs) -> pulumi.InvokeTransformResult | None:
        nonlocal args_, opts

        for it in chain.from_iterable(map(braceexpand, invoke_tokens)):
            if not fnmatch(args.token, it):
                continue

            # Transform invoke arguments
            if TYPE_CHECKING:
                assert isinstance(args.args, dict)

            if callable(args_):  # noqa: SIM108
                new_args = args_(args.args)
            else:
                new_args = args.args | args_ if args_ is not None else args.args

            # Transform invoke options
            new_opts = opts(args.opts) if callable(opts) else (opts or pulumi.InvokeOptions())
            new_opts = pulumi.InvokeOptions.merge(args.opts, new_opts)

            return pulumi.InvokeTransformResult(args=new_args, opts=new_opts)

        return None

    return transform


def override_invoke_defaults(*invoke_tokens: str, defaults: dict[str, Any]) -> pulumi.InvokeTransform:
    """Pulumi transform factory that provides default arguments to matching invoke tokens.

    Args:
        *invoke_tokens: Invoke tokens to match.
        defaults: Default arguments.

    """
    return override_invoke(
        *invoke_tokens,
        args=lambda args: defaults | args,
    )


def override_invoke_options(*invoke_tokens: str, **options: Any) -> pulumi.InvokeTransform:
    """Pulumi transform factory that overrides the invoke options for matching invoke tokens.

    Args:
        *invoke_tokens: Invoke tokens to match.
        options: Arguments of `pulumi.InvokeOptions`.

    """
    return override_invoke(
        *invoke_tokens,
        opts=pulumi.InvokeOptions(**options),
    )
