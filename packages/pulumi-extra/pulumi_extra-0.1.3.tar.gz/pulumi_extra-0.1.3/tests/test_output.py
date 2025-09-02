from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pulumi
import pytest

from pulumi_extra import render_template

if TYPE_CHECKING:
    from collections.abc import Iterator

_TEMPLATE = "docker run --detach {{ image }} {{ command }}"


class Test__render_template:
    @pytest.fixture(
        params=[
            {"content": _TEMPLATE, "file": True},
            {"content": _TEMPLATE, "file": False},
        ],
    )
    def template(self, request: pytest.FixtureRequest) -> Iterator[Path | str]:
        if request.param["file"]:
            with tempfile.NamedTemporaryFile(mode="w") as tmpfile:
                file = Path(tmpfile.name)
                file.write_text("docker run --detach {{ image }} {{ command }}")
                yield file
        else:
            yield _TEMPLATE

    def test_context(self, template: Path | str) -> Any:
        """Render template with Python values."""
        # Arrange
        image = "busybox:latest"
        command = "echo 'Hello, World!'"

        # Act
        result = render_template(template, context={"image": image, "command": command})

        # Assert
        assert result == "docker run --detach busybox:latest echo 'Hello, World!'"

    @pulumi.runtime.test
    def test_inputs(self, template: Path | str) -> Any:
        """Render template with Pulumi inputs."""
        # Arrange
        image = pulumi.Output.from_input("busybox:latest")
        command = pulumi.Output.from_input("echo 'Hello, World!'")

        # Act
        result = render_template(
            template,
            inputs={"image": image, "command": command},
        )

        # Assert
        def check(args: list[Any]) -> None:
            assert args[0] == "docker run --detach busybox:latest echo 'Hello, World!'"

        return pulumi.Output.all(result).apply(check)

    def test_inputs_and_context_mutually_exclusive(self) -> None:
        """Test mutually exclusive arguments."""
        # Arrange
        # ...

        # Act & Assert
        with pytest.raises(ValueError, match="Either context or input must be provided."):
            render_template(  # type: ignore[call-overload]
                "docker run --detach {{ image }} {{ command }}",
                context={"don't-care": "yes"},
                inputs={"don't-care": "yes"},
            )
