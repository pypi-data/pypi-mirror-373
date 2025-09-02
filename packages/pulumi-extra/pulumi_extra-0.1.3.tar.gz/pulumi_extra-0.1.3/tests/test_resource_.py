from __future__ import annotations

import pytest

from pulumi_extra import get_resource_cls, resource_has_attribute
from pulumi_extra.errors import UnknownResourceTypeError


class Test__resource_has_attribute:
    @pytest.mark.forked
    def test(self) -> None:
        # Arrange
        import pulumi_random  # noqa: F401, PLC0415

        # Act & Assert
        assert resource_has_attribute("random:index/randomId:RandomId", "byte_length") is True
        assert resource_has_attribute("random:index/randomId:RandomId", "keepers") is True
        assert resource_has_attribute("random:index/randomId:RandomId", "my-attribute") is False

    def test_unknown_resource_type(self) -> None:
        # Arrange
        # ...

        # Act & Assert
        with pytest.raises(
            UnknownResourceTypeError,
            match="Unable to resolve resource type 'random:unknown/unknown:Unknown'",
        ):
            resource_has_attribute("random:unknown/unknown:Unknown", "whatever")


class Test__get_resource_cls:
    @pytest.mark.forked
    def test(self) -> None:
        # Arrange
        import pulumi_random  # noqa: F401, PLC0415

        # Act
        cls = get_resource_cls("random:index/randomId:RandomId")

        # Assert
        assert cls is not None
        assert f"{cls.__module__}.{cls.__name__}" == "pulumi_random.random_id.RandomId"

    @pytest.mark.forked
    def test_registry_not_initialized(self) -> None:
        """If registry not initialized, it will return `None`."""
        # Arrange
        # ...

        # Act & Assert
        assert get_resource_cls("random:index/randomId:RandomId") is None

    def test_unknown_resource_type(self) -> None:
        # Arrange
        # ...

        # Act & Assert
        assert get_resource_cls("random:unknown/unknown:Unknown") is None
