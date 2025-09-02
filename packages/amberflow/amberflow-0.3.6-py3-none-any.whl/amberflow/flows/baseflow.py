from abc import ABC
import networkx as nx

from amberflow.worknodes import BaseWorkNode, WorkNodeDummy

__all__ = ("BaseFlow",)


class BaseFlow(ABC):
    """
    An abstract base class to represent a reusable workflow of connected WorkNodes.
    All Flows have a root node, and hopefully they'll have a single work node.
    """

    root: BaseWorkNode
    leaf: BaseWorkNode

    def __init__(self, name: str):
        self.name = name

        for node_name in ("root", "leaf"):
            node = WorkNodeDummy(wnid=f"{node_name}_{name}")
            setattr(self, node_name, node)
            self.dag = nx.DiGraph()
            self.dag.add_node(node)
            self.dag_ids = nx.DiGraph()
            self.dag_ids.add_node(node.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (name='{self.name}', nodes={len(self.dag)})>"
