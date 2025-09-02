# noqa: D100
import pulumi_policy as policy

from pulumi_extra import resource_has_attribute
from pulumi_extra.contrib.gcp import is_gcp_resource, is_labelable


class RequireDescription:
    """Policy validator to require description (or label if unsupported) on resources."""

    def __init__(
        self,
        *,
        require_label_if_description_unsupported: bool = False,
        description_label_key: str = "description",
    ) -> None:
        """Initialize the policy validator.

        Args:
            require_label_if_description_unsupported: Require a label if description is unsupported.
                Because GCP labels does not support human-friendly descriptions,
                in most cases, using a label for description is not recommended.
            description_label_key: The label key to use for description.

        """
        self.require_label_if_description_unsupported = require_label_if_description_unsupported
        self.description_label_key = description_label_key

    def __call__(  # noqa: D102
        self,
        args: policy.ResourceValidationArgs,
        report_violation: policy.ReportViolation,
    ) -> None:
        if not is_gcp_resource(args.resource_type):
            return

        if resource_has_attribute(args.resource_type, "description") and args.props.get("description") is None:
            report_violation(
                f"Resource '{args.urn}' is missing required description",
                None,
            )

        if self.require_label_if_description_unsupported:  # noqa: SIM102
            if is_labelable(args.resource_type):
                labels = args.props.get("labels", {})
                if self.description_label_key not in labels:
                    report_violation(
                        f"Resource '{args.urn}' is missing required label '{self.description_label_key}'",
                        None,
                    )


require_description = policy.ResourceValidationPolicy(
    name="gcp:require-description",
    description="Require description (or label if unsupported) on resources",
    config_schema=policy.PolicyConfigSchema(
        properties={},
    ),
    validate=RequireDescription(),
)
