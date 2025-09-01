# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache
from typing import Protocol, TypeVar, runtime_checkable

__all__ = [
    "Requirement",
    "RequirementsRegistry",
    "register_requirements",
]

# TypeVar for BaseRuleChecker to avoid circular import
BaseRuleChecker = TypeVar("BaseRuleChecker")


@runtime_checkable
class Requirement(Protocol):
    """
    A protocol definition of requirement.

    Attributes:
        code: A unique identifier of the requirement
        display_name: The name of the requirement (optional)
        message: A basic description of the requirement (optional)
        path: Relative path in documentation (optional)
        tags: Tags of the requirement (optional)
    """

    code: str
    display_name: str | None
    message: str | None
    path: str | None
    tags: tuple[str, ...]


@dataclass(frozen=True)
class _RequirementKey:
    """
    Internal. Stable key to be able to use a requirement in a dictionary.
    """

    requirement: Requirement

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _RequirementKey):
            return False
        return (
            self.requirement.code == other.requirement.code
            and self.requirement.display_name == other.requirement.display_name
            and self.requirement.message == other.requirement.message
            and self.requirement.path == other.requirement.path
            and self.requirement.tags == other.requirement.tags
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.requirement.code,
                self.requirement.display_name,
                self.requirement.message,
                self.requirement.path,
                self.requirement.tags,
            )
        )


@cache
@dataclass
class RequirementsRegistry:
    """
    A singleton class that maps requirements to rules.
    """

    _req_to_rule: dict[_RequirementKey, type[BaseRuleChecker]] = field(init=False, default_factory=dict)
    _rule_to_req: dict[type[BaseRuleChecker], list[Requirement]] = field(init=False, default_factory=dict)

    @property
    def requirements(self) -> list[Requirement]:
        """
        Returns:
            The list of registered requirements.
        """
        return list(key.requirement for key in self._req_to_rule.keys())

    @property
    def rules(self):
        """
        Returns:
            The list of rules mapped to the registered requirements.
        """
        return list(self._rule_to_req.keys())

    def _add_validator_requirements(
        self, rule: type[BaseRuleChecker], requirements: list[Requirement], override: bool = False
    ) -> None:
        for requirement in requirements:
            requirement_key = _RequirementKey(requirement)
            if requirement_key not in self._req_to_rule or override:
                self._req_to_rule[requirement_key] = rule
            else:
                raise ValueError(f"Requirement {requirement} already declared in {self._req_to_rule[requirement_key]}")
        self._rule_to_req[rule] = requirements

    def get_requirements(self, rule: type[BaseRuleChecker]) -> list[Requirement]:
        """
        Args:
            rule: A validator rule

        Returns:
            A list of requirements the rules implements.
        """
        return self._rule_to_req.get(rule, [])

    def get_validator(self, requirement: Requirement) -> type[BaseRuleChecker] | None:
        """
        Args:
            requirement: A requirement.

        Returns:
            The validator implementing this requirement or None.
        """
        requirement_key = _RequirementKey(requirement)
        return self._req_to_rule.get(requirement_key)

    def get_validators(self, requirements: list[Requirement]) -> list[type[BaseRuleChecker]]:
        """
        Args:
            requirements: The list of requirements.

        Returns:
            The list of rules implementing all requirements.
        """
        rules: set[type[BaseRuleChecker]] = set()
        for requirement in requirements:
            if validator := self.get_validator(requirement):
                rules.add(validator)
        return list(rules)

    def is_implemented(self, requirement: Requirement) -> bool:
        """
        Args:
            requirement: A requirement.

        Returns:
            True if the requirement is implemented.
        """
        return self.get_validator(requirement) is not None

    def all_implemented(self, requirements: list[Requirement]) -> bool:
        """
        Args:
            requirements: The list of requirements.

        Returns:
            True if all requirements are implemented.
        """
        return all(map(self.is_implemented, requirements))

    def is_registered(self, rule: type[BaseRuleChecker], requirement: Requirement) -> bool:
        """
        Args:
            rule: A rule.
            requirement: A requirement.

        Returns:
            True if the rule is registered to the requirement.
        """
        return self.get_validator(requirement) == rule

    def get_requirement_from_code(self, requirement_code: str) -> Requirement | None:
        reqs = self.requirements
        return next((req for req in reqs if req.code == requirement_code), None)


def register_requirements(
    *requirements: Requirement, override: bool = False
) -> Callable[[type[BaseRuleChecker]], type[BaseRuleChecker]]:
    """Decorator. Register a new :py:class:`BaseRuleChecker` to a set of requirements.

    .. code-block:: python

        @register_requirements(Requirement1, Requirement2)
        class MyRule(BaseRuleChecker):
            ...

    To override a registered rule, use the ``override`` parameter.

    .. code-block:: python

        @register_requirements(Requirement1, override=True)
        class MyRule(BaseRuleChecker):
            ...
    """

    def _register_requirements(rule_class: type[BaseRuleChecker]) -> type[BaseRuleChecker]:
        RequirementsRegistry()._add_validator_requirements(rule_class, list(requirements), override=override)
        return rule_class

    return _register_requirements
