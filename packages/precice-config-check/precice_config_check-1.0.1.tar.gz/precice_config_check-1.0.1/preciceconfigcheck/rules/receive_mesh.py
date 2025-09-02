import networkx as nx
from networkx import Graph
from precice_config_graph.nodes import (
    ParticipantNode,
    MeshNode,
    ReceiveMeshNode,
    Direction,
)

from preciceconfigcheck.rule import Rule
from preciceconfigcheck.rule_utils import format_list
from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation


class ReceiveMeshRule(Rule):
    name = "Receive mesh."

    class UnusedReceiveMesh(Violation):
        """
        This class handles a participant receiving a mesh, without using it.
        """

        severity = Severity.WARNING

        def __init__(self, participant: ParticipantNode, mesh: MeshNode):
            self.participant = participant
            self.mesh = mesh

        def format_explanation(self) -> str:
            return f"Participant {self.participant.name} is receiving mesh {self.mesh.name}, without using it."

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Please let {self.participant.name} use {self.mesh.name}, by mapping it to a mesh provided by "
                f"{self.participant.name} or operating on it with api-access.",
                "Otherwise, please remove it to improve readability.",
            ]

    class MappedAPIAccessReceiveMesh(Violation):
        """
        This class handles a participant receiving a mesh with api-access, but specifying a mapping on it.
        As this is unusual, a violation will be shown in debug mode.
        """

        severity = Severity.DEBUG

        def __init__(self, participant: ParticipantNode, mesh: MeshNode):
            self.participant = participant
            self.mesh = mesh

        def format_explanation(self) -> str:
            return (
                f"Participant {self.participant.name} is receiving mesh {self.mesh.name}, with api-access, "
                f"but is specifying a mapping on it."
                f"\nThis is valid, but unusual."
            )

        def format_possible_solutions(self) -> list[str]:
            return [
                f"With api-access, {self.participant.name} can directly operate on {self.mesh.name}."
            ]

    def check(self, graph: Graph) -> list[Violation]:
        violations: list[Violation] = []
        participants: list[ParticipantNode] = get_participants(graph)

        # Check all participants for their receive-meshes
        for participant in participants:
            receive_meshes: list[ReceiveMeshNode] = participant.receive_meshes
            # Check all meshes they receive
            for receive_mesh in receive_meshes:
                used: bool = False
                mesh: MeshNode = receive_mesh.mesh

                # Check if they use the receive-mesh:
                # A receive-mesh can be used by reading data from it, writing data to it, exporting it,
                # using an action on it, tracking it with a watchpoint/-integral
                if len(participant.exports) > 0:
                    used = True

                # If the participant has a mapping on the mesh, they definitely use it
                for mapping in participant.mappings:
                    if mapping.to_mesh == mesh or mapping.from_mesh == mesh:
                        used = True
                        # If they have api-access, then having a (regular) mapping is unusual
                        if not mapping.just_in_time and receive_mesh.api_access:
                            violations.append(
                                self.MappedAPIAccessReceiveMesh(participant, mesh)
                            )

                # No need to check if mesh has been used already
                # These are only valid if the participant has api-access:
                if receive_mesh.api_access and not used:
                    for read_data in participant.read_data:
                        if read_data.mesh == mesh:
                            used = True
                            break
                    for write_data in participant.write_data:
                        if write_data.mesh == mesh:
                            used = True
                            break
                    for action in participant.actions:
                        if action.mesh == mesh:
                            used = True
                            break
                    for watchpoint in participant.watchpoints:
                        if watchpoint.mesh == mesh:
                            used = True
                            break
                    for watch_integral in participant.watch_integrals:
                        if watch_integral.mesh == mesh:
                            used = True
                            break

                if not used:
                    violations.append(self.UnusedReceiveMesh(participant, mesh))

        return violations


def get_participants(graph: Graph) -> list[ParticipantNode]:
    """
    This method returns all participant nodes of the given graph.
    :param graph: The graph to get the participants from.
    :return: All participant nodes of the given graph.
    """
    participants: list[ParticipantNode] = []
    for node in graph.nodes():
        if isinstance(node, ParticipantNode):
            participants.append(node)
    return participants
