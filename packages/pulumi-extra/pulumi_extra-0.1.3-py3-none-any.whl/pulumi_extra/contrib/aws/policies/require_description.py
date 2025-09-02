# noqa: D100
import pulumi_policy as policy

from pulumi_extra import resource_has_attribute
from pulumi_extra.contrib.aws import is_aws_resource, is_taggable


class RequireDescription:
    """Policy validator to require description (or tag if unsupported) on resources."""

    def __init__(
        self,
        *,
        require_tag_if_description_unsupported: bool = False,
        description_tag_key: str = "Description",
    ) -> None:
        """Initialize the policy validator.

        Args:
            require_tag_if_description_unsupported: Require a tag if description is unsupported.
                Because AWS tags support human-friendly descriptions,
                in most cases, using a tag for description is recommended.
            description_tag_key: The tag key to use for description.

        """
        self.require_tag_if_description_unsupported = require_tag_if_description_unsupported
        self.description_tag_key = description_tag_key

    def __call__(  # noqa: D102
        self,
        args: policy.ResourceValidationArgs,
        report_violation: policy.ReportViolation,
    ) -> None:
        if not is_aws_resource(args.resource_type):
            return

        if resource_has_attribute(args.resource_type, "description") and args.props.get("description") is None:
            report_violation(
                f"Resource '{args.urn}' is missing required description",
                None,
            )

        if self.require_tag_if_description_unsupported:  # noqa: SIM102
            if is_taggable(args.resource_type):
                tags = args.props.get("tags", {})
                if self.description_tag_key not in tags:
                    report_violation(
                        f"Resource '{args.urn}' is missing required tag '{self.description_tag_key}'",
                        None,
                    )


require_description = policy.ResourceValidationPolicy(
    name="aws:require-description",
    description="Require description (or tag if unsupported) on resources",
    config_schema=policy.PolicyConfigSchema(
        properties={},
    ),
    validate=RequireDescription(),
)
