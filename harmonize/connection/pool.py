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

        Parameters
        ----------
            nodes : list[:class:`harmonize.connection.Node`]
                A list of nodes to load.

        Returns
        -------
            None
        """
        for node in nodes:
            cls.load_node(node)

    @classmethod
    def load_node(cls, node: Node) -> None:
        """
        Loads a single node into the pool.

        Parameters
        ----------
            node : :class:`harmonize.connection.Node`
                The node to load into the pool.

        Returns
        -------
            None
        """
        node.connect()
        cls.__nodes[node.identifier] = node

    @classmethod
    def get_nodes(cls) -> list[Node]:
        """
        Retrieves a list of connected nodes from the pool.

        Returns
        -------
            list[:class:`harmonize.connection.Node`]
        """
        return [
            i for i in cls.__nodes.values()
            if i.status == NodeStatus.CONNECTED
        ]

    @classmethod
    def get_node(cls, identifier: str) -> Node:
        """
        Retrieves a node from the pool by its identifier.

        Parameters
        ----------
            identifier : str
                The identifier of the node to retrieve.

        Returns
        -------
            :class:`harmonize.connection.Node`
        """
        return cls.__nodes[identifier]

    @classmethod
    def get_best_node(cls) -> Optional[Node]:
        """
        Get the best node from the pool based on the number of players.

        Returns
        -------
            Optional[:class:`harmonize.connection.Node`]
        """
        if cls.get_nodes():
            return min(cls.get_nodes(), key=lambda x: len(x.players))

    @classmethod
    def close_all(cls) -> None:
        """
        Close all the nodes in the pool.

        Returns
        -------
            None
        """
        for node in cls.get_nodes():
            node.close()
