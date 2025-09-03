from abc import ABC, abstractmethod

from networkx import Graph

from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation


class Rule(ABC):
    """
    Abstract Class 'Rule'. Checking a 'Rule' for violations and producing formatted output.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """@abstract property: Name of the rule in readable style."""
        pass

    def __init__(self) -> None:
        """
        Initializes a Rule object.
        """

    @abstractmethod
    def check(self, graph: Graph) -> list[Violation]:
        """
        @abstractmethod: Defines how a 'Rule' should be checked

        Args:
            graph (Graph): that must be checked according to this rule.

        Returns:
            list[Violation]: found.

        Hint: Implement Violations as inner classes in the rule of type Violation.
        """
        pass

    def satisfied(self, violations: list[Violation], debug: bool) -> bool:
        """
        Checks if a rule is satisfied.
        If debug mode is enabled, violations with severity level DEBUG are also considered.

        Args:
            violations (list[Violation]): that need to be checked.
            debug (bool): for debug mode.

        Returns:
            bool: True, if a rule is satisfied.
        """
        if debug and len(violations) > 0:
            return False
        for violation in violations:
            if violation.severity != Severity.DEBUG:
                return False
        return True
