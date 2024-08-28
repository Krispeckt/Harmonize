from harmonize.connection.cache.nodes import DLLNode

__all__ = (
    "DLL",
)


class DLL:
    __slots__ = ("head", "tail")

    def __init__(self) -> None:
        self.head: DLLNode = DLLNode()
        self.tail: DLLNode = DLLNode()

        self.head.later, self.tail.previous = self.tail, self.head

    def append(self, node: DLLNode) -> None:
        tail_prev: DLLNode | None = self.tail.previous
        tail: DLLNode | None = self.tail

        assert tail_prev and tail

        tail_prev.later = node
        tail.previous = node

        node.later = tail
        node.previous = tail_prev

    def popleft(self) -> DLLNode | None:
        node: DLLNode | None = self.head.later
        if node is None:
            return

        self.remove(node)
        return node

    def remove(self, node: DLLNode | None) -> None:
        if node is None:
            return

        node_prev: DLLNode | None = node.previous
        node_later: DLLNode | None = node.later

        assert node_prev and node_later

        node_prev.later = node_later
        node_later.previous = node_prev

        node.later = None
        node.previous = None

    def __bool__(self) -> bool:
        return self.head.later != self.tail