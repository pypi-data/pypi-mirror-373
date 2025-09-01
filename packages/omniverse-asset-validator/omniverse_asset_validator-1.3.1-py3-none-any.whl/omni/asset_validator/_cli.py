# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import argparse
import asyncio
import gettext
import inspect
import logging
import sys
from collections import Counter
from functools import lru_cache

from pxr import Tf

from ._assets import AssetProgress
from ._base_rule_checker import BaseRuleChecker
from ._capabilities import Capability, CapabilityRegistry
from ._categories import CategoryRuleRegistry
from ._csv_reports import IssueCSVData
from ._engine import ValidationEngine
from ._fix import IssueFixer
from ._issues import IssueGroupsBy, IssuePredicate, IssuePredicates, IssueSeverity
from ._requirements import Requirement, RequirementsRegistry
from ._results import Results, ResultsList
from ._version import __version__

__all__ = [
    "ValidationArgsExec",
    "ValidationNamespaceExec",
    "cli_main",
    "create_validation_parser",
]

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class _ArgFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass


class _ArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        args = {"prog": self.prog, "message": message}
        self.exit(2, gettext.gettext("%(prog)s: error: %(message)s\n") % args)


class _ExplainAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help="Provide descriptions for each argument provided and exit.",
    ):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        registry = CategoryRuleRegistry()
        for rule_name in namespace.rule:
            if rule := registry.find_rule(rule_name):
                print(f"{rule.__name__} : {rule.GetDescription()}\n")
        for rule_name in namespace.disable_rule:
            if rule := registry.find_rule(rule_name):
                print(f"{rule.__name__} : {rule.GetDescription()}\n")
        for category in namespace.category:
            for rule in registry.get_rules(category):
                print(f"{rule.__name__} : {rule.GetDescription()}\n")
        for category in namespace.disable_category:
            for rule in registry.get_rules(category):
                print(f"{rule.__name__} : {rule.GetDescription()}\n")
        parser.exit()


def create_validation_parser() -> argparse.ArgumentParser:
    """
    Creates an argument parser with common options, this includes:

    For ValidationEngine:

    - init-rules/no-init-rules: Optional. Default True. Sets ValidationEngine, init_rules argument.
    - variants/no-variants: Optional. Default True. Sets ValidationEngine, variants argument.
    - rule/disable-rule: Optional. Enables/Disable rules in ValidationEngine.
    - category/disable-category. Optional. Enable/Disable categories in ValidationEngine.
    - asset. Required. The asset in which to perform validation.

    `enable-rule` and `enable-category` are alias for `rule` and `category` respectively.

    For IssueFixer:

    - predicate: Optional. Issues to filter for IssueFixer.
    - fix/no-fix: Optional. Whether to apply IssueFixer after ValidationEngine.

    Other options:
    - version: Print the version of omni.asset_validator.
    """
    parser = _ArgParser(allow_abbrev=False)
    parser.prog = "validate"
    parser.formatter_class = _ArgFormatter
    parser.description = inspect.cleandoc(
        """
        Utility for USD validation to ensure assets run smoothly across all OpenUSD
        products. Validation is based on the USD ComplianceChecker (i.e. the same
        backend as the usdchecker commandline tool), and has been extended with
        additional rules as follows:

        - Additional rules applicable in the broader OpenUSD ecosystem.
        - Configurable end-user rules that can be specific to individual company
          and/or team workflows.

        Note this level of configuration requires setting the environment,
        prior to launching this tool.
        """
    )
    parser.epilog = "See https://tinyurl.com/omni-asset-validator for more details."
    parser.add_argument(
        "asset",
        metavar="ASSET",
        type=str,
        nargs=1,
        help=inspect.cleandoc(
            """
            A single OpenUSD Asset.
            Note: This can be a file or folder.
            """
        ),
    )
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )
    # Explain
    parser.add_argument(
        "-e",
        "--explain",
        action=_ExplainAction,
    )
    # Rules
    rules: str = "\n".join(cls.__name__ for cls in CategoryRuleRegistry().rules)
    parser.add_argument(
        "-r",
        "--rule",
        "--enable-rule",
        metavar="RULE",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=[cls.__name__ for cls in CategoryRuleRegistry().rules],
        help=inspect.cleandoc(f"Rule to select. Valid options include:\n{rules}"),
    )
    parser.add_argument(
        "-D",  # For backwards compatibility
        "--disable-rule",
        "--disableRules",  # For backwards compatibility
        metavar="RULE",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=[cls.__name__ for cls in CategoryRuleRegistry().rules],
        help=inspect.cleandoc(f"Rule to disable. Valid options include:\n{rules}"),
    )
    # Categories
    categories: str = "\n".join(category for category in CategoryRuleRegistry().categories)
    parser.add_argument(
        "-c",
        "--category",
        "--enable-category",
        metavar="CATEGORY",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=list(CategoryRuleRegistry().categories),
        help=inspect.cleandoc(f"Category to select. Valid options include:\n{categories}"),
    )
    parser.add_argument(
        "--disable-category",
        metavar="CATEGORY",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=list(CategoryRuleRegistry().categories),
        help=inspect.cleandoc(f"Category to disable. Valid options include:\n{categories}"),
    )
    req_codes = list(map(lambda requirement: requirement.code, RequirementsRegistry().requirements))
    req_codes.sort()
    requirements = "\n".join(req_codes)
    parser.add_argument(
        "--requirement",
        metavar="REQUIREMENT",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=req_codes,
        help=inspect.cleandoc(f"Requirement to add. Valid options include:\n{requirements}"),
    )
    # Get capability names with versions for CLI display
    capability_choices = []
    for key in CapabilityRegistry().keys():
        capability_choices.append(f"{key.id}@{key.version}")
    capability_choices.sort()
    capability_arg_help = "\n".join(capability_choices)
    parser.add_argument(
        "--capability",
        metavar="CAPABILITY",
        required=False,
        type=str,
        default=[],
        action="append",
        choices=capability_choices,
        help=inspect.cleandoc(f"Capability to add. Valid options include:\n{capability_arg_help}"),
    )
    # Fixes
    parser.add_argument(
        "-f",  # For backwards compatibility
        "--fix",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Whether to fix issues.",
    )
    # Predicates
    issue_predicates = [
        IssuePredicates.Any.__name__,
        IssuePredicates.IsFailure.__name__,
        IssuePredicates.IsWarning.__name__,
        IssuePredicates.IsError.__name__,
        IssuePredicates.HasRootLayer.__name__,
    ]
    issue_predicates.sort()
    issue_predicates_help = "\n".join(issue_predicates)
    parser.add_argument(
        "-p",
        "--predicate",
        metavar="PREDICATE",
        required=False,
        type=str,
        choices=issue_predicates,
        help=inspect.cleandoc(f"Predicate to select. Valid options include:\n{issue_predicates_help}"),
    )
    # Init rules
    parser.add_argument(
        "-d",  # For backwards compatibility
        "--init-rules",
        "--defaultRules",  # For backwards compatibility
        default=True,
        action=argparse.BooleanOptionalAction,
        help=inspect.cleandoc(
            """
            Whether to use the default enabled validation rules.
            Opt-out of this behavior to gain finer control over
            the rules using the --categories and --rules flags.
            """
        ),
    )
    # Variants
    parser.add_argument(
        "--variants",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Whether to set variants. Note: This can be expensive.",
    )
    # CSV Output
    parser.add_argument(
        "--csv-output",
        metavar="CSV",
        required=False,
        type=str,
        help="Path to the CSV output file.",
    )

    return parser


class ValidationNamespaceExec:
    """
    Uses Argument Parser Namespace to run validation. Useful for CLI tools.
    """

    def __init__(self, namespace: argparse.Namespace):
        self._namespace = namespace
        self._results = []

    @property
    def variants(self) -> bool:
        """
        Returns:
            The `variants` option value.
        """
        return self._namespace.variants

    @property
    def init_rules(self) -> bool:
        """
        Returns:
            The `init_rules` option value.
        """
        return (
            self._namespace.init_rules
            and not self.category_rules
            and not self.rules
            and not self.requirements
            and not self.capabilities
        )

    @property
    def asset(self) -> str | None:
        """
        Returns:
            The `asset` option value.
        """
        return self._namespace.asset[0] if self._namespace.asset else None

    @property
    def fix(self) -> bool:
        """
        Returns:
            The `fix` option value.
        """
        return self._namespace.fix

    @property
    def predicate(self) -> IssuePredicate:
        return (
            getattr(IssuePredicates, self._namespace.predicate)()
            if self._namespace.predicate
            else IssuePredicates.Any()
        )

    @property
    def rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `rules` option value.
        """
        return self.enabled_rules

    @property
    def requirements(self) -> list[Requirement]:
        """
        Returns:
            The `requirements` option value.
        """
        registry = RequirementsRegistry()
        requirements = []
        for req_code in self._namespace.requirement:
            if req := registry.get_requirement_from_code(req_code):
                requirements.append(req)
        return requirements

    @property
    def capabilities(self) -> list[Capability]:
        """
        Returns:
            The `capabilities` option value.
        """
        registry = CapabilityRegistry()
        capabilities = []
        for cap_spec in self._namespace.capability:
            if "@" in cap_spec:
                cap_id, version = cap_spec.split("@", 1)
            else:
                cap_id, version = cap_spec, None
            if cap := registry.find_capability(cap_id, version):
                capabilities.append(cap)
        return capabilities

    @property
    def enabled_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `enable_rules` option value.
        """
        registry = CategoryRuleRegistry()
        rules = []
        for rule_name in self._namespace.rule:
            rule: type[BaseRuleChecker] | None = registry.find_rule(rule_name)
            if rule:
                rules.append(rule)
        return rules

    @property
    def disabled_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `disable_rules` option value.
        """
        registry = CategoryRuleRegistry()
        rules = []
        for rule_name in self._namespace.disable_rule:
            rule: type[BaseRuleChecker] | None = registry.find_rule(rule_name)
            if rule:
                rules.append(rule)
        return rules

    @property
    def category_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `category` options value.
        """
        return self.enabled_category_rules

    @property
    def enabled_category_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `enable_category` options value.
        """
        registry = CategoryRuleRegistry()
        rules = []
        for category in self._namespace.category:
            for rule in registry.get_rules(category):
                rules.append(rule)
        return rules

    @property
    def disable_category_rules(self) -> list[type[BaseRuleChecker]]:
        """
        Returns:
            The `disable_category` option value.
        """
        registry = CategoryRuleRegistry()
        rules = []
        for category in self._namespace.disable_category:
            for rule in registry.get_rules(category):
                rules.append(rule)
        return rules

    @property
    def csv_output(self) -> str | None:
        """
        Returns:
            The `csv-output` option value.
        """
        return self._namespace.csv_output

    def _create_engine(self) -> ValidationEngine:
        return ValidationEngine(init_rules=self.init_rules, variants=self.variants)

    def _populate_engine(self, engine: ValidationEngine) -> None:
        for rule in self.rules:
            engine.enable_rule(rule)
        for rule in self.enabled_category_rules:
            engine.enable_rule(rule)
        for requirement in self.requirements:
            engine.enable_requirement(requirement)
        for capability in self.capabilities:
            engine.enable_capability(capability)
        for rule in self.disabled_rules:
            engine.disable_rule(rule)
        for rule in self.disable_category_rules:
            engine.disable_rule(rule)

    def create_engine(self) -> ValidationEngine:
        if not self.asset:
            raise ValueError("Asset not given")
        engine = self._create_engine()
        self._populate_engine(engine)
        return engine

    @classmethod
    def _asset_progress_fn(cls, progress: AssetProgress) -> None:
        logger = logging.getLogger(__name__)

        @lru_cache(maxsize=16)
        def func(asset, percent) -> None:
            logger.info(f"Processing {asset}........{percent}%")

        func(progress.asset, int(progress.progress * 100))

    def _asset_validated_fn(self, result: Results) -> None:
        fix: bool = self.fix
        predicate: IssuePredicate = self.predicate
        logger = logging.getLogger(__name__)
        logger.info(f"Results for Asset '{result.asset}'")
        for issue in result.issues(IssuePredicates.And(IssuePredicates.IsError(), predicate)):
            logger.exception(str(issue), exc_info=False)
        for issue in result.issues(IssuePredicates.And(IssuePredicates.IsFailure(), predicate)):
            logger.error(str(issue))
        for issue in result.issues(IssuePredicates.And(IssuePredicates.IsWarning(), predicate)):
            logger.warning(str(issue))
        for issue in result.issues(IssuePredicates.And(IssuePredicates.IsInfo(), predicate)):
            logger.info(str(issue))
        if fix:
            fixer = IssueFixer(result.asset)
            for item in fixer.fix(result.issues(predicate)):
                logger.warning(f"{item.issue.message}........{item.status}")
            try:
                fixer.save()
            except (OSError, Tf.ErrorException) as e:
                logger.error(f"Failed to save fixes: {e}")

        # Store all issues for final csv report
        self._results.append(result)

    def _export_csv(self) -> None:
        csv_data = IssueCSVData.from_(ResultsList(self._results))
        csv_data.export_csv(self.csv_output)

    async def _validate(self) -> bool:
        logger = logging.getLogger(__name__)
        engine = self.create_engine()
        asset: str = self.asset

        await engine.validate_with_callbacks(
            asset=asset,
            asset_progress_fn=self._asset_progress_fn,
            asset_validated_fn=self._asset_validated_fn,
        )
        results = ResultsList(self._results)

        logger.info("-" * 128)
        has_issues: bool = results.issues()
        if not has_issues:
            logger.info("No issues found.")
        else:
            # Group by rule and severity
            logger.info("Summary per Rule:")
            for group in results.issues().group_by(IssueGroupsBy.rule()):
                mapper = Counter()
                for subgroup in group.group_by(IssueGroupsBy.severity()):
                    mapper[subgroup.name] += len(subgroup)
                logger.info(
                    f"{group.name.__name__ if group.name else 'No rules'}: "
                    f"{mapper[IssueSeverity.FAILURE]} Failures / "
                    f"{mapper[IssueSeverity.WARNING]} Warnings / "
                    f"{mapper[IssueSeverity.ERROR]} Errors / "
                    f"{mapper[IssueSeverity.INFO]} Infos "
                )
            # Group by severity
            logger.info("-" * 128)
            logger.info("Summary per Severity:")
            mapper = Counter()
            for group in results.issues().group_by(IssueGroupsBy.severity()):
                mapper[group.name] += len(group)
            logger.info(f"Failures: {mapper[IssueSeverity.FAILURE]}")
            logger.info(f"Warnings: {mapper[IssueSeverity.WARNING]}")
            logger.info(f"Errors: {mapper[IssueSeverity.ERROR]}")
            logger.info(f"Infos: {mapper[IssueSeverity.INFO]}")

        # Time per rule
        logger.debug("-" * 128)
        logger.debug("Time per Rule:")
        total_time: float = 0.0
        for rule, time in engine.stats.get_rule_times():
            logger.debug(f"{rule.__name__}: {round(time, 3)} s.")
            total_time += time
        logger.debug(f"Total Time: {round(total_time, 3)} s.")

        # Saving reports
        if self.csv_output:
            self._export_csv()
        return not has_issues

    def run_validation(self) -> bool:
        return asyncio.run(self._validate())


ValidationArgsExec = ValidationNamespaceExec
"""
For backwards compatibility.
"""


def cli_main(args: list[str] | None = None):
    """
    Main method in command line interface.
    """
    parser = create_validation_parser()
    args = ValidationNamespaceExec(parser.parse_args(args))
    successful: bool = args.run_validation()
    if not successful:
        sys.exit(1)
