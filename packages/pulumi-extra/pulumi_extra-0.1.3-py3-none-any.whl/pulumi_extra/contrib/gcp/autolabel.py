# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING

import pulumi
import pulumi_gcp  # noqa: F401 ; Required to detect resources otherwise `is_labelable` will always return `False`

from pulumi_extra import resource_has_attribute

from .common import is_gcp_resource

_NOT_LABELABLE_RESOURCES: set[str] = set()


def register_auto_labeling(
    *,
    exclude: set[str] | None = None,
    extra: dict[str, str] | None = None,
) -> None:
    """Register a Pulumi stack transform that automatically labels resources.

    Args:
        exclude: Resources to exclude from labeling.
        extra: Extra labels to add.
    """
    labels = {}
    extra = extra or {}
    exclude = exclude or set()

    # Pulumi labels
    # NOTE: Labels transformed because of strict restrictions GCP enforces
    org = pulumi.get_organization()
    project = pulumi.get_project()
    stack = pulumi.get_stack()
    labels.update(
        {
            "pulumi-organization": org,
            "pulumi-project": project.replace(".", "-"),
            "pulumi-stack": stack,
            "managed-by": "pulumi",
        },
    )
    labels.update(extra)

    def transform(
        args: pulumi.ResourceTransformArgs,
    ) -> pulumi.ResourceTransformResult | None:
        if args.type_ not in exclude and is_labelable(args.type_):
            if TYPE_CHECKING:
                assert isinstance(args.props, dict)
            args.props["labels"] = {
                **labels,
                **(args.props.get("labels", {})),
            }
            return pulumi.ResourceTransformResult(props=args.props, opts=args.opts)

        return None

    pulumi.runtime.register_resource_transform(transform)


def is_labelable(resource_type: str) -> bool:
    """Determine if a given GCP resource type is labelable."""
    if not is_gcp_resource(resource_type):
        pulumi.log.debug(f"Resource type {resource_type} is not a GCP resource")
        return False

    if resource_type in _NOT_LABELABLE_RESOURCES:
        pulumi.log.info(
            f"Resource type {resource_type} is set not-labelable explicitly",
        )
        return False

    return resource_has_attribute(resource_type, "labels")
