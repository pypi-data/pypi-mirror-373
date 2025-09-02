from networkx import Graph
from precice_config_graph.nodes import (
    CouplingSchemeNode,
    MultiCouplingSchemeNode,
    ParticipantNode,
    ExchangeNode,
    MeshNode,
    MappingNode,
    Direction,
    DataNode,
)

from preciceconfigcheck.rule import Rule
from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation


class CouplingSchemeMappingRule(Rule):
    name = (
        "Exchange in a coupling scheme needs a mapping between involved participants."
    )

    class MissingMappingCouplingSchemeViolation(Violation):
        """
        A coupling scheme with a data exchange between two participants exists, but no mapping between them.
        This means they either need api-access to one-another, or they are missing a mapping.
        In case they are missing a mapping, there is this violation.
        """

        severity = Severity.ERROR

        def __init__(
            self,
            from_participant: ParticipantNode,
            to_participant: ParticipantNode,
            exchange_mesh: MeshNode,
            data: DataNode,
        ):
            self.from_participant = from_participant
            self.to_participant = to_participant
            self.exchange_mesh = exchange_mesh
            if exchange_mesh in from_participant.provide_meshes:
                # from_participant writes to own mesh, sends it to to_participant, who maps it to his own mesh, and reads from it
                self.direction = Direction.READ
                self.mapper = to_participant
                self.non_mapper = from_participant
                self.mesh_owner = from_participant
                self.from_string = f"from {self.exchange_mesh.name}"
                self.to_string = f"to a mesh provided by {to_participant.name}"
            else:
                # from_participant writes to own mesh, maps it to to_participants mesh, sends it to to_participant, who reads from it
                self.direction = Direction.WRITE
                self.mapper = from_participant
                self.non_mapper = to_participant
                self.mesh_owner = to_participant
                self.from_string = f"from a mesh provided by {from_participant.name}"
                self.to_string = f"to {self.exchange_mesh.name}"
            self.data = data

        def format_explanation(self) -> str:
            return (
                f"The exchange of data {self.data.name} belonging to the coupling scheme between participants "
                f"{self.from_participant.name} and {self.to_participant.name} using {self.mesh_owner.name}'s "
                f"mesh {self.exchange_mesh.name} is missing a mapping."
            )

        def format_possible_solutions(self) -> list[str]:
            return [
                f"For this exchange, {self.mapper.name} has to define a {self.direction.value}-mapping "
                f"{self.from_string} {self.to_string}.",
                "Otherwise, change the mesh used in the exchange and make sure that there exists a corresponding "
                "mapping for it.",
            ]

    class MissingMappingAPIAccessCouplingSchemeViolation(Violation):
        """
        A coupling scheme with a data exchange between two participants exists, but no mapping between them.
        This means they either need api-access to one-another, or they are missing a mapping.
        In case they have api-access, there is this violation, as a user can forget to specify a mapping.
        """

        severity = Severity.DEBUG

        def __init__(
            self,
            from_participant: ParticipantNode,
            to_participant: ParticipantNode,
            exchange_mesh: MeshNode,
            data: DataNode,
        ):
            self.from_participant = from_participant
            self.to_participant = to_participant
            self.exchange_mesh = exchange_mesh
            if exchange_mesh in from_participant.provide_meshes:
                # from_participant writes to own mesh, sends it to to_participant, who maps it to his own mesh, and reads from it
                self.direction = Direction.READ
                self.mapper = to_participant
                self.non_mapper = from_participant
                self.mesh_owner = from_participant
            else:
                # from_participant writes to own mesh, maps it to to_participants mesh, sends it to to_participant, who reads from it
                self.direction = Direction.WRITE
                self.mapper = from_participant
                self.non_mapper = to_participant
                self.mesh_owner = to_participant
            self.data = data

        def format_explanation(self) -> str:
            out: str = (
                f"The exchange of data {self.data.name} belonging to the coupling scheme between participants "
                f"{self.from_participant.name} and {self.to_participant.name} using {self.mesh_owner.name}'s "
                f"mesh {self.exchange_mesh.name} does not have a mapping."
            )
            out += (
                f"\nThis is valid, because {self.mapper.name} has api-access to {self.non_mapper.name}'s "
                f"{self.exchange_mesh.name}, but is more prone to errors."
            )
            return out

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Specifying a just-in-time {self.direction.value}-mapping at {self.mapper.name} will make the "
                f"exchange of data more reliable."
            ]

    def check(self, graph: Graph) -> list[Violation]:
        violations: list[Violation] = []

        couplings: list[
            CouplingSchemeNode | MultiCouplingSchemeNode
        ] = filter_coupling_nodes(graph)

        for coupling in couplings:
            # Unknown participants in from=/to= are handled by precice-tools check

            # Check for all exchanges, whether a mapping exists between first and second (in the correct direction)
            exchanges: list[ExchangeNode] = coupling.exchanges
            for exchange in exchanges:
                # Check whose mesh gets used
                exchange_mesh = exchange.mesh
                from_participant = exchange.from_participant
                to_participant = exchange.to_participant
                from_meshes = from_participant.provide_meshes
                to_meshes = to_participant.provide_meshes
                data: DataNode = exchange.data

                # from-participant writes data to from-mesh, exchanges it to to-participant, who maps it to his own
                # mesh and then reads from it => READ-mapping by to-participant required, or api-access to from-mesh
                if exchange_mesh in from_meshes:
                    has_correct_mapping: bool = any(
                        mapping_fits_exchange(
                            mapping,
                            Direction.READ,
                            from_participant,
                            to_participant,
                            exchange_mesh,
                        )
                        for mapping in to_participant.mappings
                    )
                    # Only add a violation if no correct mapping exists
                    if not has_correct_mapping:
                        if has_api_access(to_participant, exchange_mesh):
                            # If the participant has api-access, add a debug-violation
                            violations.append(
                                self.MissingMappingAPIAccessCouplingSchemeViolation(
                                    from_participant,
                                    to_participant,
                                    exchange_mesh,
                                    data,
                                )
                            )
                        else:
                            violations.append(
                                self.MissingMappingCouplingSchemeViolation(
                                    from_participant,
                                    to_participant,
                                    exchange_mesh,
                                    data,
                                )
                            )
                # from-participant writes data to own mesh, maps it to to-mesh, exchanges it to to-participant, who
                # reads from it => WRITE-mapping by from-participant required, or api-access to to-mesh
                elif exchange_mesh in to_meshes:
                    has_correct_mapping: bool = any(
                        mapping_fits_exchange(
                            mapping,
                            Direction.WRITE,
                            from_participant,
                            to_participant,
                            exchange_mesh,
                        )
                        for mapping in from_participant.mappings
                    )
                    # Only add a violation if no correct mapping exists
                    if not has_correct_mapping:
                        if has_api_access(from_participant, exchange_mesh):
                            # If the participant has api-access, add a debug-violation
                            violations.append(
                                self.MissingMappingAPIAccessCouplingSchemeViolation(
                                    from_participant,
                                    to_participant,
                                    exchange_mesh,
                                    data,
                                )
                            )
                        else:
                            violations.append(
                                self.MissingMappingCouplingSchemeViolation(
                                    from_participant,
                                    to_participant,
                                    exchange_mesh,
                                    data,
                                )
                            )

        return violations


def filter_coupling_nodes(
    graph: Graph,
) -> list[CouplingSchemeNode | MultiCouplingSchemeNode]:
    """
    This function returns all coupling scheme nodes of the given graph.
    :param graph:The graph to check.
    :return: All (multi-)coupling scheme nodes of the graph.
    """
    couplings: list[CouplingSchemeNode | MultiCouplingSchemeNode] = []
    for node in graph.nodes:
        if isinstance(node, CouplingSchemeNode) or isinstance(
            node, MultiCouplingSchemeNode
        ):
            couplings.append(node)
    return couplings


def mapping_fits_exchange(
    mapping: MappingNode,
    direction: Direction,
    from_participant: ParticipantNode,
    to_participant: ParticipantNode,
    exchange_mesh: MeshNode,
) -> bool:
    """
        This function checks, whether the given mapping fits an exchange indicated by the given direction,
        first and second participant and mesh used in the exchange.
    :param mapping: The mapping to check.
    :param direction: The direction the mapping is supposed to have.
    :param to_participant: The to= participant in the exchange.
    :param from_participant: The from= participant in the exchange.
    :param exchange_mesh: The mesh= used in the exchange.
    :return: True, if the mapping has the correct direction and meshes.
    """
    if mapping.direction != direction:
        return False
    if direction == Direction.WRITE:
        # For direction-write, the mesh used in the exchange needs to be by to-participant
        if exchange_mesh not in to_participant.provide_meshes:
            return False
        if exchange_mesh != mapping.to_mesh:
            return False
    elif direction == Direction.READ:
        # For direction-read, the mesh used in the exchange needs to be by from-participant
        if exchange_mesh not in from_participant.provide_meshes:
            return False
        elif exchange_mesh != mapping.from_mesh:
            return False

    return True


def has_api_access(participant: ParticipantNode, mesh: MeshNode) -> bool:
    """
    This function checks, whether the given participant has API access to the given mesh.
    :param participant: The participant to check.
    :param mesh: The mesh to check.
    :return: True, if the participant receives the mesh with api-access=true
    """
    for receive_mesh in participant.receive_meshes:
        if receive_mesh.mesh == mesh and receive_mesh.api_access:
            return True
    return False
