from collections.abc import Iterator
from pathlib import Path

import pulumi
import pytest
from pulumi import automation

from pulumi_extra import override_resource, override_resource_defaults
from tests._helpers import resolve_output_values

pytestmark = pytest.mark.integration


def pulumi_program() -> None:
    import pulumi_docker as docker  # noqa: PLC0415

    busybox = docker.RemoteImage(
        "busybox",
        opts=pulumi.ResourceOptions(
            transforms=[
                # Modify default
                override_resource_defaults("*", defaults={"platform": "linux/amd64"}),
                # This will not have any effect (no match)
                override_resource("_", props={"platform": "linux/arm64"}),
                # Will modify argument
                override_resource("*", props={"name": "busybox"}),
            ],
        ),
        name="scratch",
        keep_locally=True,
    )

    for attr in ("name", "platform"):
        pulumi.export(attr, getattr(busybox, attr))


@pytest.fixture
def pulumi_stack(tmpdir: Path) -> Iterator[automation.Stack]:
    stack = automation.create_or_select_stack(
        stack_name="test",
        project_name="test",
        program=pulumi_program,
        opts=automation.LocalWorkspaceOptions(
            env_vars={
                "PULUMI_BACKEND_URL": f"file://{tmpdir}",
                "PULUMI_CONFIG_PASSPHRASE": "test",
            },
        ),
    )
    stack.up(on_output=print)
    yield stack
    stack.destroy(on_output=print, remove=True)


class Test__override_resource:
    @pytest.mark.forked
    def test(self, pulumi_stack: automation.Stack) -> None:
        # Arrange
        # ...

        # Act
        outputs = pulumi_stack.outputs()

        # Assert
        assert resolve_output_values(outputs) == {
            "name": "busybox",
            "platform": "linux/amd64",  # Original default value is ""
        }


# TODO(lasuillard): `override_resource_options` has not been tested, currently I'm not aware of a way (inspect resource's options) to test it.  # noqa: E501
