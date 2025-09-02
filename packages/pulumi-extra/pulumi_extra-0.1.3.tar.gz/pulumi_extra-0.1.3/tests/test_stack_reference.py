from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest import mock

import pulumi
import pytest

from pulumi_extra import get_stack_outputs, get_stack_reference, re_export

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def mock_stack_reference() -> Iterator[mock.MagicMock]:
    """Mock `pulumi.StackReference`.

    - Returns output `"value:{key}"` for given key.

    """
    with mock.patch("pulumi.StackReference") as m:
        m.return_value.require_output.side_effect = lambda v: pulumi.Output.from_input(f"value:{v}")
        yield m


class Test__get_stack_reference:
    @pytest.mark.parametrize(
        ("ref", "expect"),
        [
            ("dev", "organization/project/dev"),
            ("network/dev", "organization/network/dev"),
            ("organization/management/default", "organization/management/default"),
        ],
    )
    @pulumi.runtime.test
    def test_ref(self, *, ref: str, expect: str) -> Any:
        # Arrange
        # ...

        # Act
        sr = get_stack_reference(ref)

        # Assert
        def check(args: list[Any]) -> None:
            assert args[0] == expect

        return pulumi.Output.all(sr.name).apply(check)

    def test_invalid_ref(self) -> Any:
        # Arrange
        # ...

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid stack reference: 'organization/project/dev/extra'"):
            get_stack_reference("organization/project/dev/extra")


class Test__get_stack_outputs:
    @pytest.mark.parametrize(
        ("ref", "expect"),
        [
            ("dev:ami-id", "value:ami-id"),
            ("dev:{ec2-instance-id,elastic-ip}", ["value:ec2-instance-id", "value:elastic-ip"]),
        ],
    )
    @pytest.mark.usefixtures("mock_stack_reference")
    @pulumi.runtime.test
    def test_ref(self, *, ref: str, expect: Any) -> Any:
        # Arrange
        # ...

        # Act
        outputs = get_stack_outputs(ref)

        # Assert
        def check(args: list[Any]) -> None:
            assert args[0] == expect

        return pulumi.Output.all(outputs).apply(check)

    def test_invalid_ref(self) -> Any:
        # Arrange
        # ...

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid output reference: ':output'"):
            get_stack_outputs(":output")


class Test__re_export:
    @pytest.mark.usefixtures("mock_stack_reference")
    @pulumi.runtime.test
    def test_export(self) -> Any:
        # Arrange
        # ...

        # Act
        with mock.patch("pulumi.export") as m_export:
            re_export("network/dev:{ec2-instance-id,elastic-ip}", "shared:github-repository")

        # Assert
        assert m_export.call_count == 3

        def check(args: list[Any]) -> None:
            assert args[0] == [
                (("ec2-instance-id", "value:ec2-instance-id"), {}),
                (("elastic-ip", "value:elastic-ip"), {}),
                (("github-repository", "value:github-repository"), {}),
            ]

        return pulumi.Output.all(m_export.call_args_list).apply(check)
