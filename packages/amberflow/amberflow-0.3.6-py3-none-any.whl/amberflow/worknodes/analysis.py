from amberflow.worknodes import BaseSingleWorkNode
from amberflow.worknodes.baseworknode import BaseWorkNode

__all__ = (
    "BaseAnalysis",
    "BaseOptimizer",
)


class BaseAnalysis(BaseSingleWorkNode):
    pass


class BaseOptimizer(BaseWorkNode):
    pass
