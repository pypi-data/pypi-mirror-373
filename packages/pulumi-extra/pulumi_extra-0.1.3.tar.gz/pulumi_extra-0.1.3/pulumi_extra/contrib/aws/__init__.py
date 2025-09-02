from .autotag import is_taggable, register_auto_tagging
from .common import is_aws_resource

__all__ = (
    "is_aws_resource",
    "is_taggable",
    "register_auto_tagging",
)
