import networkx as nx
from networkx import Graph
from precice_config_graph.nodes import (
    CouplingSchemeNode,
    MultiCouplingSchemeNode,
    ParticipantNode,
    CouplingSchemeType,
)
from preciceconfigcheck.rule import Rule
from preciceconfigcheck.rule_utils import format_list
from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation


class CompositionalCouplingRule(Rule):
    # A compositional coupling between participants can lead to a deadlock and will cause errors.
    name = "Coupling schemes cannot be circularly dependent."

    class CompositionalDeadlockViolation(Violation):
        """
        This class handles participants exchanging data through coupling schemes in a circular way, which leads
        to a deadlock.
        """

        severity = Severity.ERROR

        def __init__(self, participants: list[ParticipantNode]) -> None:
            self.names = format_list([p.name for p in participants])

        def format_explanation(self) -> str:
            return f"Participants {self.names} are involved in a circularly dependent (serial) coupling."

        def format_possible_solutions(self) -> list[str]:
            return [f"Please change the structure of couplings between {self.names}."]

    def check(self, graph: Graph) -> list[Violation]:
        violations = []
        coupling_edges = []
        # Only coupling schemes are important for this evaluation
        g1 = nx.subgraph_view(graph, filter_node=filter_coupling_scheme_nodes)
        for coupling in g1.nodes():
            if (
                coupling.type == CouplingSchemeType.SERIAL_EXPLICIT
                or coupling.type == CouplingSchemeType.SERIAL_IMPLICIT
            ):
                # Directed edge between first and second participant
                coupling_edges += [
                    (coupling.first_participant, coupling.second_participant)
                ]

        # Create a new graph from edges connecting participants
        coupling_graph = nx.DiGraph()
        for node_a, node_b in coupling_edges:
            coupling_graph.add_edge(node_a, node_b)

        # Detect all cycles
        cycles = list(nx.simple_cycles(coupling_graph))
        for cycle in cycles:
            # If there are cycles, then their nodes are the participants involved
            violations.append(self.CompositionalDeadlockViolation(cycle))

        return violations


# Helper functions
def filter_coupling_scheme_nodes(node) -> bool:
    """
    A function filtering coupling scheme nodes in the graph.

    Args:
        node: the node to check

    Returns:
        True, if the node is a coupling scheme node.
    """
    return isinstance(node, CouplingSchemeNode)
