# noqa: D100
import pulumi_policy as policy

from pulumi_extra.contrib.gcp import is_gcp_resource, is_labelable


class RequireLabels:
    """Policy validator to require specific labels on resources."""

    def __call__(  # noqa: D102
        self,
        args: policy.ResourceValidationArgs,
        report_violation: policy.ReportViolation,
    ) -> None:
        config = args.get_config()
        required_labels = config["required-labels"]
        if not required_labels or not is_gcp_resource(args.resource_type):
            return

        if is_labelable(args.resource_type):
            labels = args.props.get("labels", {})
            for rl in required_labels:
                if not labels or rl not in labels:
                    report_violation(
                        f"Resource '{args.urn}' is missing required label '{rl}'",
                        None,
                    )


require_labels = policy.ResourceValidationPolicy(
    name="gcp:require-labels",
    description="Require specific labels on resources",
    config_schema=policy.PolicyConfigSchema(
        properties={
            "required-labels": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    ),
    validate=RequireLabels(),
)
