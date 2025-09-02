# noqa: D100
def is_gcp_resource(resource_type: str) -> bool:
    """Determine if a given resource type is an AWS resource."""
    return resource_type.startswith("gcp:")
