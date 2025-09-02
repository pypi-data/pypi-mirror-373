from typing import Any

from pulumi import automation


def resolve_output_values(outputs: automation.OutputMap) -> dict[str, Any]:
    return {k: v.value for k, v in outputs.items()}
