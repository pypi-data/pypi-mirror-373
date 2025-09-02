import networkx as nx
from networkx import Graph
from precice_config_graph.nodes import ParticipantNode, DataNode

from preciceconfigcheck.rule import Rule
from preciceconfigcheck.rule_utils import format_list
from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation

default_possible_solutions = [
    "Consider splitting up the simulation into multiple configurations to improve maintainability of each simulation.",
]


class DisjointSimulationsRule(Rule):
    name = "Couplings should not be disjoint"

    class CommonDisjointSimulationsViolation(Violation):
        participant_sets: frozenset[frozenset[ParticipantNode]]

        def __init__(self, participant_sets: frozenset[frozenset[ParticipantNode]]):
            super()
            assert len(participant_sets) > 1
            self.participant_sets = participant_sets

        def assemble_from_default_explanation(self, details: str = "") -> str:
            explanation = (
                f"There are {len(self.participant_sets)} simulations that do not interact with each "
                f"other{details}. "
            )

            def format_set(participants: frozenset[ParticipantNode]) -> str:
                return format_list([p.name for p in participants])

            if len(self.participant_sets) == 2:
                [participants_a, participants_b] = list(self.participant_sets)

                participants_a_label = (
                    "Participants" if len(participants_a) > 1 else "Participant"
                )
                do_str = "do" if len(participants_a) > 1 else "does"
                participants_b_label = (
                    "participants" if len(participants_b) > 1 else "participant"
                )

                explanation += (
                    f"{participants_a_label} {format_set(participants_a)} {do_str} not communicate with "
                    f"{participants_b_label} {format_set(participants_b)}."
                )
            else:
                explanation += f"Disjoint groups:"
                for component in self.participant_sets:
                    explanation += f"\n- {format_set(component)}"

            return explanation

    class FullyDisjointSimulationsViolation(CommonDisjointSimulationsViolation):
        severity = Severity.DEBUG

        def __init__(self, participant_sets: frozenset[frozenset[ParticipantNode]]):
            super().__init__(participant_sets)

        def format_explanation(self) -> str:
            return self.assemble_from_default_explanation()

        def format_possible_solutions(self) -> list[str]:
            return default_possible_solutions + [
                "Add some data to be exchanged between these simulations.",
            ]

    class SharedDataDisjointSimulationsViolation(CommonDisjointSimulationsViolation):
        severity = Severity.WARNING
        shared_data: DataNode

        def __init__(
            self,
            shared_data: DataNode,
            participant_sets: frozenset[frozenset[ParticipantNode]],
        ):
            super().__init__(participant_sets)
            self.shared_data = shared_data

        def format_explanation(self) -> str:
            return self.assemble_from_default_explanation(
                f", but share data {self.shared_data.name}"
            )

        def format_possible_solutions(self) -> list[str]:
            return default_possible_solutions + [
                "Exchange the data between these simulations.",
            ]

    def check(self, graph: Graph) -> list[Violation]:
        def is_participant(node) -> bool:
            return isinstance(node, ParticipantNode)

        def is_data_node(node) -> bool:
            return isinstance(node, DataNode)

        def has_participant(component) -> bool:
            return any(is_participant(node) for node in component)

        def get_components_with_participant(graph: Graph):
            components = list(filter(has_participant, nx.connected_components(graph)))
            # if there is just one component, remove it, since having a single component is the regular, valid case
            return components if len(components) > 1 else []

        components = list(nx.connected_components(graph))

        components_with_participant = get_components_with_participant(graph)

        # Take a look at the individual components without data, because using the same data doesn't necessarily mean
        # that the simulations really do talk to each other. In contrast to regular components, we call these dataless
        # components. It must always hold that len(components) <= len(dataless_components).
        dataless_graph = nx.subgraph_view(
            graph, filter_node=lambda node: not is_data_node(node)
        )
        dataless_components = get_components_with_participant(dataless_graph)

        fully_disjoint_participant_sets = frozenset(
            [
                frozenset(filter(is_participant, component))
                for component in components_with_participant
            ]
        )
        shared_data_participant_sets = frozenset(
            [
                frozenset(filter(is_participant, component))
                for component in dataless_components
            ]
        )

        # exclude components that get a violation for fully disjoint from shared data (fully disjoint > shared data)
        shared_data_participant_sets -= fully_disjoint_participant_sets
        fully_disjoint_participant_sets -= shared_data_participant_sets

        violations = []

        if len(fully_disjoint_participant_sets) > 1:
            violations.append(
                self.FullyDisjointSimulationsViolation(fully_disjoint_participant_sets)
            )

        dataless_components_by_data: dict[
            DataNode, set[frozenset[ParticipantNode]]
        ] = {}
        # for each dataless component, find out which data belongs to it (in order to print that information).
        for dataless_component in shared_data_participant_sets:
            # any node of a dataless component can ever only be in one overall component. So just look at the first.
            any_node = list(dataless_component)[0]
            home_component = None

            for potential_home_component in components:
                if any_node in potential_home_component:
                    home_component = potential_home_component

            assert (
                home_component is not None
            ), "Any dataless component is always in an overall component."

            # Now, use this home component to add this dataless component to one or more data names
            related_data = filter(is_data_node, home_component)
            for related_data in related_data:
                if related_data not in dataless_components_by_data:
                    dataless_components_by_data[related_data] = set()
                dataless_components_by_data[related_data].add(
                    frozenset(dataless_component)
                )

        for (data, dataless_components) in dataless_components_by_data.items():
            violations.append(
                self.SharedDataDisjointSimulationsViolation(
                    data, frozenset(dataless_components)
                )
            )

        return violations
