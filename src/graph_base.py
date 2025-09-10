


class Node:
    """Класс описывающий узел графа."""

    def __init__(self, id: str='', ind: int=None):
        self.id = id
        self.ind = ind
        self.edges_in = dict()
        self.edges_out = dict()

    def add_edge_in(self, edge: "Edge"):
        """Добавление входящего ребра."""
        self.edges_in[edge.id] = edge

    def add_edge_out(self, edge: "Edge"):
        """Добавление исходящего ребра."""
        self.edges_out[edge.id] = edge

    def input_flow(self):
        return sum([edge.value for edge in self.edges_in.values()])

    def output_flow(self):
        return sum([edge.value for edge in self.edges_out.values()])

    def debalance(self):
        return self.input_flow() - self.output_flow()


class Edge:

    def __init__(
        self,
        id: str,
        node_src: Node=None,
        node_dst: Node=None,
        value: float=0,
        ind: int=None
    ):
        self.id = id
        self.node_src = node_src
        self.node_dst = node_dst
        self.value = value
        self.ind= ind


class Graph:
    """Граф материальных потоков"""

    def __init__(
        self,
        edges: dict[str, Edge],
        nodes: dict[str, Node]
    ):
        self.edges = edges
        self.nodes = nodes
