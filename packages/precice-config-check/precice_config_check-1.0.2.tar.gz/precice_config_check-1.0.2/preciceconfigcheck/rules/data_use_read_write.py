from collections import defaultdict
import networkx as nx
from networkx import Graph
from precice_config_graph.nodes import (
    DataNode,
    MeshNode,
    ReadDataNode,
    WriteDataNode,
    WatchPointNode,
    ExportNode,
    WatchIntegralNode,
    ParticipantNode,
    ExchangeNode,
    ActionNode,
    ReceiveMeshNode,
)
from preciceconfigcheck.rule import Rule
from preciceconfigcheck.rule_utils import format_list
from preciceconfigcheck.severity import Severity
from preciceconfigcheck.violation import Violation


class DataUseReadWriteRule(Rule):
    name = "Utilization of data."

    class DataNotUsedNotReadNotWrittenViolation(Violation):
        """
        This violation handles nobody using, reading or writing a data node.
        """

        severity = Severity.WARNING

        def __init__(self, data_node: DataNode):
            self.data_node = data_node

        def format_explanation(self) -> str:
            return f"Data {self.data_node.name} is declared but never used, read or written."

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Consider using {self.data_node.name} in a mesh and have participants read and write it.",
                "Otherwise please remove it to improve readability.",
            ]

    class DataUsedNotReadNotWrittenViolation(Violation):
        """
        This violation handles someone using a data node, but nobody is reading and writing said data node.
        """

        severity = Severity.WARNING

        def __init__(self, data_node: DataNode, meshes: list[MeshNode]):
            self.data_node = data_node
            self.form = "es" if len(meshes) > 1 else ""
            self.names = format_list([m.name for m in meshes])

        def format_explanation(self) -> str:
            # self.form ensures the correct number (multiplicity) for the word mesh (i.e., mesh or meshes)
            return f"Data {self.data_node.name} gets used in mesh{self.form} {self.names}, but nobody is reading or writing it."

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Consider having a participant read {self.data_node.name}.",
                f"Consider having a participant write {self.data_node.name}.",
                "Otherwise, please remove it to improve readability.",
            ]

    class DataUsedNotReadWrittenViolation(Violation):
        """
        This class handles someone using and writing a data node, but nobody reading said data node.
        """

        severity = Severity.WARNING

        def __init__(
            self, data_node: DataNode, mesh: MeshNode, writers: list[ParticipantNode]
        ):
            self.data_node = data_node
            self.mesh = mesh
            self.writers = writers
            # Correct grammar for output
            self.form = ""
            self.form2 = "is"
            if len(writers) > 1:
                self.form = "s"
                self.form2 = "are"
            self.names = format_list([w.name for w in writers])

        def format_explanation(self) -> str:
            return (
                f"Data {self.data_node.name} is used in mesh {self.mesh.name} and participant{self.form} "
                f"{self.names} {self.form2} writing it, but nobody is reading it."
            )

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Consider having a participant read data {self.data_node.name}.",
                f"Consider exporting {self.data_node.name} by a participant.",
                f"Consider using watchpoints or watch-integrals to keep track of {self.data_node.name}.",
                "Otherwise please remove it to improve readability.",
            ]

    class DataUsedReadNotWrittenViolation(Violation):
        """
        This class handles a mesh using and someone reading a data node, but nobody writing said data node.
        """

        severity = Severity.ERROR

        def __init__(
            self, data_node: DataNode, mesh: MeshNode, readers: list[ParticipantNode]
        ):
            self.data_node = data_node
            self.mesh = mesh
            # Correct grammar for output
            self.form = ""
            self.form2 = "is"
            if len(readers) > 1:
                self.form = "s"
                self.form2 = "are"
            self.names = format_list([r.name for r in readers])

        def format_explanation(self) -> str:
            return (
                f"Data {self.data_node.name} is being used in mesh {self.mesh.name} and participant{self.form} "
                f"{self.names} {self.form2} reading it, but nobody is writing it."
            )

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Consider having a participant write {self.data_node.name}.",
                "Otherwise please remove it to improve readability.",
            ]

    class DataNotExchangedViolation(Violation):
        """
        This class handles data being used in a mesh, read and written by different participants,
        but not being exchanged between them.
        """

        severity = Severity.ERROR

        def __init__(
            self, data_node: DataNode, writer: ParticipantNode, reader: ParticipantNode
        ):
            self.data_node = data_node
            self.writer = writer
            self.reader = reader

        def format_explanation(self) -> str:
            return (
                f"Data {self.data_node.name} gets written by {self.writer.name} and read by {self.reader.name}, "
                f"but not exchanged between them."
            )

        def format_possible_solutions(self) -> list[str]:
            return [
                f"Please exchange {self.data_node.name} in a coupling scheme between {self.writer.name} and "
                f"{self.reader.name}"
            ]

    def check(self, graph: Graph) -> list[Violation]:
        violations: list[Violation] = []
        parents_of_meshes: dict[MeshNode, ParticipantNode] = find_parents_of_meshes(
            graph
        )
        g1 = nx.subgraph_view(graph, filter_node=filter_use_read_write_data)
        for node in g1.nodes:
            # We only need to test data nodes here
            if isinstance(node, DataNode):
                data_node = node
                use_data: bool = False
                read_data: bool = False
                write_data: bool = False
                meshes: list[MeshNode] = []
                writers: list[ParticipantNode] = []
                readers: list[ParticipantNode] = []
                readers_per_writer: dict[ParticipantNode : list[ParticipantNode]] = {}
                readers_per_mesh: dict[MeshNode, list[ParticipantNode]] = {}
                writers_per_mesh: dict[MeshNode, list[ParticipantNode]] = {}

                # Check all neighbors of the data node for use-, reader- and writer-nodes
                for neighbor in g1.neighbors(data_node):
                    # Check if data gets used by a mesh
                    if isinstance(neighbor, MeshNode):
                        try:
                            parent = parents_of_meshes[neighbor]
                        except KeyError:
                            # Is handled in provide_mesh.py
                            continue
                        use_data = True
                        meshes += [neighbor]

                        # Check if Parent owns exports
                        if len(parent.exports) > 0:
                            # If so, the mesh gets read by this export
                            read_data = True
                            readers += [parent]
                            append_participant_to_map(
                                readers_per_mesh, neighbor, parent
                            )

                        mesh_neighbors = g1.neighbors(neighbor)
                        # Check if mesh gets observed by action, watchpoint or watch-integral.
                        # These types of reader nodes do not read the data itself, but only "read" the mesh and all of
                        # its used data.
                        for mesh_neighbor in mesh_neighbors:
                            if isinstance(mesh_neighbor, WatchPointNode):
                                read_data = True
                                readers += [mesh_neighbor.participant]
                                append_participant_to_map(
                                    readers_per_mesh,
                                    neighbor,
                                    mesh_neighbor.participant,
                                )
                            elif isinstance(mesh_neighbor, WatchIntegralNode):
                                read_data = True
                                readers += [mesh_neighbor.participant]
                                append_participant_to_map(
                                    readers_per_mesh,
                                    neighbor,
                                    mesh_neighbor.participant,
                                )
                            elif isinstance(mesh_neighbor, ActionNode):
                                # Check if action reads or writes data (corresponds to source or target data)
                                # Check all source-data nodes if they correspond to the current data node
                                for source in mesh_neighbor.source_data:
                                    if source == data_node:
                                        read_data = True
                                        # Use the participant associated with the action
                                        readers += [mesh_neighbor.participant]
                                        append_participant_to_map(
                                            readers_per_mesh,
                                            neighbor,
                                            mesh_neighbor.participant,
                                        )
                                # Check if the target data corresponds to the current data node
                                if mesh_neighbor.target_data == data_node:
                                    write_data = True
                                    # Use the participant associated with the action
                                    writers += [mesh_neighbor.participant]
                                    append_participant_to_map(
                                        writers_per_mesh,
                                        neighbor,
                                        mesh_neighbor.participant,
                                    )

                    # Check if data gets read by a participant.
                    # Only read-data nodes reading current data_node are connected to it
                    elif isinstance(neighbor, ReadDataNode):
                        read_data = True
                        readers += [neighbor.participant]
                        append_participant_to_map(
                            readers_per_mesh, neighbor.mesh, neighbor.participant
                        )
                    # Check if data gets written by a participant
                    elif isinstance(neighbor, WriteDataNode):
                        write_data = True
                        writers += [neighbor.participant]
                        append_participant_to_map(
                            writers_per_mesh, neighbor.mesh, neighbor.participant
                        )

                # For every writer, identify the corresponding set of readers
                for writer in writers:
                    readers_per_writer[writer] = []
                    # Meshes that the participant provides can be read directly through just-in-time mappings
                    provide_meshes = get_provide_meshes_for_data(writer, data_node)
                    for provide_mesh in provide_meshes:
                        # An export by the writer will directly read from the mesh
                        if len(writer.exports) > 0:
                            readers_per_writer[writer].append(writer)

                        # Check all neighbors of the mesh: A jit-mapping will read directly from it
                        for provide_mesh_neighbor in graph.neighbors(provide_mesh):
                            # Only use read-data if it reads current data_node
                            if (
                                isinstance(provide_mesh_neighbor, ReadDataNode)
                                and provide_mesh_neighbor.data == data_node
                            ):
                                readers_per_writer[writer].append(
                                    provide_mesh_neighbor.participant
                                )
                            # Action, Watchpoint and Watch-Integral are directly connected to the provide-mesh
                            elif isinstance(provide_mesh_neighbor, WatchPointNode):
                                readers_per_writer[writer].append(
                                    provide_mesh_neighbor.participant
                                )
                            elif isinstance(provide_mesh_neighbor, WatchIntegralNode):
                                readers_per_writer[writer].append(
                                    provide_mesh_neighbor.participant
                                )
                            elif isinstance(provide_mesh_neighbor, ActionNode):
                                # Check if action reads or writes data (corresponds to source or target data)
                                # Check all source-data nodes if they correspond to the current data node
                                for source in provide_mesh_neighbor.source_data:
                                    if source == data_node:
                                        # Use the participant associated with the action
                                        readers_per_writer[writer].append(
                                            provide_mesh_neighbor.participant
                                        )

                            # If the provided mesh gets received somewhere, it might get read there
                            elif isinstance(provide_mesh_neighbor, ReceiveMeshNode):
                                potential_reader = provide_mesh_neighbor.participant
                                # Check all potential readers
                                if len(potential_reader.exports) > 0:
                                    readers_per_writer[writer].append(potential_reader)
                                for potential_reader_neighbor in graph.neighbors(
                                    potential_reader
                                ):
                                    if (
                                        isinstance(
                                            potential_reader_neighbor, ReadDataNode
                                        )
                                        and potential_reader_neighbor.data == data_node
                                    ):
                                        readers_per_writer[writer].append(
                                            potential_reader
                                        )
                                    # Watchpoint, Watch-integral and export do not specify data
                                    elif isinstance(
                                        potential_reader_neighbor, WatchPointNode
                                    ):
                                        readers_per_writer[writer].append(
                                            potential_reader
                                        )
                                    elif isinstance(
                                        potential_reader_neighbor, WatchIntegralNode
                                    ):
                                        readers_per_writer[writer].append(
                                            potential_reader
                                        )
                                    elif isinstance(
                                        potential_reader_neighbor, ActionNode
                                    ):
                                        # Actions can have many source data; check for current data_node
                                        for (
                                            source
                                        ) in potential_reader_neighbor.source_data:
                                            if source == data_node:
                                                readers_per_writer[writer].append(
                                                    potential_reader
                                                )

                # Add violations according to use/read/write
                if use_data and read_data and write_data:
                    # If all three, use_data, read_data and write_data, are true, then there must be paths from every
                    # writer to all of his readers
                    data_flow_edges = []
                    # Build a graph from participants involved in exchanges of data node
                    exchanges = [
                        node
                        for node in graph.nodes
                        if isinstance(node, ExchangeNode) and node.data == data_node
                    ]
                    for exchange in exchanges:
                        data_flow_edges += [
                            (exchange.from_participant, exchange.to_participant)
                        ]
                    data_flow_graph = nx.DiGraph()
                    data_flow_graph.add_edges_from(data_flow_edges)
                    writer_s = set(writers)
                    # Check if data gets read and written by the same participant.
                    # If so, then no exchange is needed.
                    # Otherwise, an exchange is needed.
                    for writer in writer_s:
                        reader_s = set(readers_per_writer[writer])
                        for reader in reader_s:
                            # If they are the same, then everything is fine.
                            if reader == writer:
                                continue
                            # Otherwise, there needs to be an exchange of data between them.
                            else:
                                if (
                                    writer not in data_flow_graph.nodes
                                    or reader not in data_flow_graph.nodes
                                ):
                                    # One of writer/reader is not connected through an exchange involving data_node
                                    violations.append(
                                        self.DataNotExchangedViolation(
                                            data_node, writer, reader
                                        )
                                    )
                                else:
                                    # Both writer/reader are connected with an exchange involving data_node
                                    # Check if there exists a path between them
                                    path = nx.has_path(data_flow_graph, writer, reader)
                                    if not path:
                                        violations.append(
                                            self.DataNotExchangedViolation(
                                                data_node, writer, reader
                                            )
                                        )

                elif use_data and read_data and not write_data:
                    for mesh in readers_per_mesh.keys():
                        violations.append(
                            self.DataUsedReadNotWrittenViolation(
                                data_node, mesh, readers_per_mesh[mesh]
                            )
                        )
                elif use_data and not read_data and write_data:
                    for mesh in writers_per_mesh.keys():
                        violations.append(
                            self.DataUsedNotReadWrittenViolation(
                                data_node, mesh, writers_per_mesh[mesh]
                            )
                        )
                elif use_data and not read_data and not write_data:
                    violations.append(
                        self.DataUsedNotReadNotWrittenViolation(data_node, meshes)
                    )

                elif not use_data and read_data and write_data:
                    # This case gets handled by precice-tools check
                    continue
                elif not use_data and read_data and not write_data:
                    # This case gets handled by precice-tools check
                    continue
                elif not use_data and not read_data and write_data:
                    # This case gets handled by precice-tools check
                    continue
                elif not use_data and not read_data and not write_data:
                    violations.append(
                        self.DataNotUsedNotReadNotWrittenViolation(data_node)
                    )
        return violations


# Helper functions


def get_provide_meshes_for_data(
    participant: ParticipantNode, data: DataNode
) -> list[MeshNode]:
    """
    This method returns all meshes provided by the given participant that use the given data.
    :param participant: The participant from which to get the meshes.
    :param data: The data that the meshes use.
    :return: A list of all meshes provided by the given participant using the given data.
    """
    provide_meshes = []
    for mesh in participant.provide_meshes:
        if data in mesh.use_data:
            provide_meshes.append(mesh)
    return provide_meshes


def filter_use_read_write_data(node) -> bool:
    """
    This method filters nodes, that could potentially use data, read data or write data.

    A mesh is the only node that can "use" data.

    A read-data node, export, watchpoint, watch-integral or action are considered to "read" data.

    A write-data- or action-node is considered to "write" data.

    Args:
         node: The node to check.

    Returns:
        True, if the node is a data-, read-/write-, action- or mesh node.
    """
    return (
        isinstance(node, DataNode)
        or isinstance(node, MeshNode)
        or isinstance(node, ReadDataNode)
        or isinstance(node, ExportNode)
        or isinstance(node, WatchPointNode)
        or isinstance(node, WatchIntegralNode)
        or isinstance(node, WriteDataNode)
        or isinstance(node, ActionNode)
    )


def filter_data_exchange(node) -> bool:
    """
    This method filters data- and exchange-nodes.
    :param node: The node to check.
    :return: True, if the node is a data- or exchange-node, False otherwise.
    """
    return isinstance(node, DataNode) or isinstance(node, ExchangeNode)


def append_participant_to_map(
    dictionary: dict[MeshNode : list[ParticipantNode]], mesh, participant
):
    """
    This method appends the given participant to the given map for an entry 'mesh'.
    If the map entry for mesh is none, then a new entry is created.
    :param dictionary: The map to append to.
    :param mesh: The mesh which entries should be appended.
    :param participant: The participant to append to the mesh.
    """
    try:
        dictionary[mesh] += [participant]
    except KeyError:
        dictionary[mesh] = [participant]


def find_parents_of_meshes(graph: Graph) -> dict[MeshNode, ParticipantNode]:
    """
    This method finds all parents (participants providing the mesh) of all meshes from the given graph.
    :param graph: The graph to find parents of meshes of.
    :return: A dictionary mapping mesh nodes to their parents.
    """
    parents_of_meshes: dict[MeshNode, ParticipantNode] = {}
    for node in graph.nodes:
        if isinstance(node, ParticipantNode):
            for mesh in node.provide_meshes:
                parents_of_meshes[mesh] = node
    return parents_of_meshes
