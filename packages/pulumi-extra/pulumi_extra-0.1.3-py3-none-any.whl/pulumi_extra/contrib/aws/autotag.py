# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING

import pulumi
import pulumi_aws  # noqa: F401 ; Required to detect resources otherwise `is_taggable` will always return `False`

from pulumi_extra import resource_has_attribute

from .common import is_aws_resource

_NOT_TAGGABLE_RESOURCES: set[str] = {
    "aws:autoscaling/group:Group",
    "aws:devopsguru/resourceCollection:ResourceCollection",
}


def register_auto_tagging(
    *,
    exclude: set[str] | None = None,
    extra: dict[str, str] | None = None,
) -> None:
    """Register a Pulumi stack transform that automatically tags resources.

    Args:
        exclude: Resources to exclude from tagging.
        extra: Extra tags to add.
    """
    tags = {}
    extra = extra or {}
    exclude = exclude or set()

    # Pulumi tags
    org = pulumi.get_organization()
    project = pulumi.get_project()
    stack = pulumi.get_stack()
    tags.update(
        {
            "pulumi:Organization": org,
            "pulumi:Project": project,
            "pulumi:Stack": stack,
            "Managed-By": "Pulumi",
        },
    )
    tags.update(extra)

    def transform(
        args: pulumi.ResourceTransformArgs,
    ) -> pulumi.ResourceTransformResult | None:
        if args.type_ not in exclude and is_taggable(args.type_):
            if TYPE_CHECKING:
                assert isinstance(args.props, dict)
            args.props["tags"] = {
                **tags,
                **(args.props.get("tags", {})),
            }
            return pulumi.ResourceTransformResult(props=args.props, opts=args.opts)

        return None

    pulumi.runtime.register_resource_transform(transform)


def is_taggable(resource_type: str) -> bool:
    """Determine if a given AWS resource type is taggable."""
    if not is_aws_resource(resource_type):
        pulumi.log.debug(f"Resource type {resource_type} is not a AWS resource")
        return False

    if resource_type in _NOT_TAGGABLE_RESOURCES:
        pulumi.log.info(
            f"Resource type {resource_type} is set not-taggable explicitly",
        )
        return False

    return resource_has_attribute(resource_type, "tags")
