from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from harmonize.enums import NodeStatus

if TYPE_CHECKING:
    from harmonize.connection.node import Node

__all__ = (
    "Pool",
)


class Pool:
    __nodes: dict[str, Node] = {}

    @classmethod
    def load_nodes(cls, nodes: list[Node]) -> None:
        """
        Loads multiple nodes into the pool.

        Args:
            nodes (list[Node]): A list of nodes to load.

        Returns:
            None
        """
        for node in nodes:
            cls.load_node(node)

    @classmethod
    def load_node(cls, node: Node) -> None:
        """
        Loads a node into the pool.

        Args:
            node (Node): The node to load.

        Returns:
            None
        """
        node.connect()
        cls.__nodes[node.identifier] = node

    @classmethod
    def get_nodes(cls) -> list[Node]:
        """
        Retrieves a list of connected nodes from the pool.

        Returns:
            list[Node]: A list of connected nodes.
        """
        return [
            i for i in cls.__nodes.values()
            if i.status == NodeStatus.CONNECTED
        ]

    @classmethod
    def get_node(cls, identifier: str) -> Node:
        """
        Retrieves a node from the pool by its identifier.

        Args:
            identifier (str): The identifier of the node to retrieve.

        Returns:
            Node: The node with the specified identifier.
        """
        return cls.__nodes[identifier]

    @classmethod
    def get_best_node(cls) -> Optional[Node]:
        """
        Get the best node from the pool based on the number of players.

        Returns:
            Optional[Node]: The node with the least number of players, or None if there are no nodes in the pool.
        """
        if cls.get_nodes():
            return min(cls.get_nodes(), key=lambda x: len(x.players))

    @classmethod
    def close_all(cls) -> None:
        """
        Close all the nodes in the pool.

        This method iterates over all the nodes in the pool and calls the `close()` method on each node.

        Returns:
            None
        """
        for node in cls.get_nodes():
            node.close()

    @classmethod
    def close_node(cls, node: Node) -> None:
        """
        Closes a node in the pool.

        Args:
            node (Node): The node to close.

        Returns:
            None
        """
        node.close()
