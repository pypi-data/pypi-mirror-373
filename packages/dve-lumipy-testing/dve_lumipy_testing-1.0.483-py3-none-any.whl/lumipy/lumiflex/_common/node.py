from __future__ import annotations

from typing import Tuple, Callable, List

from pydantic import BaseModel, Field, field_validator
from pydantic import StrictStr

from lumipy.lumiflex._common.str_utils import model_repr


class Node(BaseModel):
    """Base class for all lumiflex node objects. Node objects represent nodes of a directed acyclic graph (DAG).

        https://en.wikipedia.org/wiki/Directed_acyclic_graph

    The node base class contains functionality for constructing, manipulating and analysing DAGs.
    Each node has a label value and a tuple of parents that define its graph edges.

    Lumiflex is designed such that the DAGs end in a single node, this is the terminus node. Graph methods are called on
    the terminus node to manipulate and decompose the graph (apply_map, topological_sort).

    """

    label_: StrictStr = Field(alias='label')
    parents_: Tuple = Field(tuple(), alias='parents')

    class Config:
        frozen = True
        extra = 'forbid'
        arbitrary_types_allowed = True
        validate_assignment = True

    # noinspection PyMethodParameters
    @field_validator('parents_')
    def _validate_parents(cls, val):
        if not all(isinstance(p, Node) for p in val):
            clss_str = ', '.join(type(p).__name__ for p in val)
            raise TypeError(f'Parents must all be Node or a subclass of Node but were ({clss_str}).')

        return val

    def __repr__(self):
        return model_repr(self)

    def get_label(self) -> str:
        """Get the label string value of this node.

        Returns:
            str: the label string.
        """
        return self.label_

    def get_parents(self) -> Tuple[Node, ...]:
        """Get the parents of this node.

        Returns:
            Tuple[Node, ...]: a tuple of nodes that are parents to this one.
        """
        return self.parents_

    def is_leaf(self) -> bool:
        """Test whether this is a leaf node (has no parents)

        Returns:
            bool: whether this is a leaf node or not.
        """
        return len(self.parents_) == 0

    def update_node(self, **kwargs) -> Node:
        """Create a new node instance with different field values.

        Notes:
            Nodes are immutable in lumiflex. Graphs are modified by using node_apply with a function
            that makes new replacement nodes with this function.

        Args:
            **kwargs: the fields to update.

        Returns:
            Node: the node instance with updated field values.

        """
        d = {k: v for k, v in iter(self)}
        d.update(**kwargs)
        # remove duplicates
        for k in kwargs.keys():
            if k + '_' in d:
                del d[k + '_']
        # rename internal fields for compatibility with the input aliasing
        for k in list(d.keys()):
            if k.endswith('_'):
                d[k[:-1]] = d.pop(k)

        return self.model_validate(d)

    def get_ancestors(self) -> List[Node]:
        """Get all ancestor nodes of this node.

        The ancestors are the parents of this node, their parents, and so on. It's a list of every node in the DAG that
        this node depends on.

        Returns:
            List[Node]: a list of all ancestor nodes.
        """
        ancestors = {}

        def walk(n: Node):
            for p in n.get_parents():
                if not isinstance(p, Node):
                    raise TypeError(f'There was a node that had non-node parents! (value = {p})')
                ancestors[hash(p)] = p
                walk(p)

        walk(self)

        return list(ancestors.values())

    def apply_map(self, fn: Callable) -> Node:
        """Apply a node-wise map function to this graph terminus node.

        A node-wise map will take a node as input and return another node as output. This map is then applied to every
        node in the DAG starting from the leaf nodes down to the terminal one, updating each node's parents and reconstructing
        the DAG as it goes.

        Args:
            fn (Callable): the node-wise map that takes a node and returns another updated node.

        Returns:
            Node: the mapped version of this terminal node.
        """
        ancestors = self.get_ancestors()
        mapped = {hash(a): fn(a, parents=tuple()) for a in ancestors if a.is_leaf()}

        n = len(mapped)
        while n != len(ancestors):
            for a in ancestors:
                parents = a.get_parents()
                if hash(a) not in mapped and all(hash(p) in mapped for p in parents):
                    mapped[hash(a)] = fn(a, parents=[mapped[hash(p)] for p in parents])

            # number of mapped nodes must increase by at least one each time
            if n == len(mapped):
                raise ValueError(
                    f'DAG node map failed! Can\'t find parents for one or more of {len(ancestors) - n} remaining nodes'
                )

            n = len(mapped)

        mapped_parents = [mapped[hash(p)] for p in self.get_parents()]
        return fn(self, parents=mapped_parents)

    def topological_sort(self) -> List[Node]:
        """Get a topologically-ordered list of this terminus node and its graph dependencies.

        Notes:
            Topological ordering of a graph gives its nodes in a sequence such that for each edge from node A to node B
            node A comes before node B in the ordering. If other words if a node has a dependency on another it will come
            after the other node in the ordering.
            See:
                https://en.wikipedia.org/wiki/Topological_sorting

        Returns:
            List[Node]: a topologically-ordered list of nodes that make up this graph.
        """
        ancestors = self.get_ancestors()

        visited = [a for a in ancestors if a.is_leaf()]
        visited_hashes = [hash(a) for a in ancestors if a.is_leaf()]

        while len(visited) != len(ancestors):
            for a in ancestors:
                if hash(a) in visited_hashes:
                    continue

                if all(hash(p) in visited_hashes for p in a.get_parents()):
                    visited.append(a)
                    visited_hashes.append(hash(a))

        visited.append(self)
        return visited
