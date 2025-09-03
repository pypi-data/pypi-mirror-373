import unittest

from lumipy.lumiflex._common.node import Node
from pydantic import ValidationError


class NodeTests(unittest.TestCase):

    def test_node_ctor_default(self):
        a = Node(label='abc')
        self.assertEqual(a.get_label(), 'abc')
        self.assertEqual(a.get_parents(), tuple())

    def test_node_ctor_set_param_values(self):
        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        self.assertEqual(c.get_label(), 'c')
        self.assertEqual(c.get_parents(), (a, b))

    def test_node_ctor_value_must_be_given(self):
        with self.assertRaises(ValidationError) as ve:
            Node()

        self.assertIn(
            "Node\nlabel\n  Field required [type=missing, input_value={}, input_type=dict]",
            str(ve.exception)
        )

    def test_node_ctor_value_must_be_str(self):
        with self.assertRaises(ValidationError) as ve:
            Node(label=list())

        self.assertIn(
            "Node\nlabel\n  Input should be a valid string [type=string_type, input_value=[], input_type=list]",
            str(ve.exception)
        )

    def test_node_ctor_parents_must_be_tuple_of_nodes(self):
        with self.assertRaises(ValidationError) as ve:
            Node(label='42', parents=False)

        self.assertIn(
            "1 validation error for Node\nparents\n  Input should be a valid tuple [type=tuple_type, input_value=False, input_type=bool]",
            str(ve.exception)
        )

        with self.assertRaises(TypeError) as ve:
            Node(label='42', parents=[1, 2])

        self.assertIn(
            "Parents must all be Node or a subclass of Node but were (int, int)",
            str(ve.exception)
        )

    def test_node_ctor_extra_kwargs_not_allowed(self):
        with self.assertRaises(ValidationError) as ve:
            Node(label='42', is_not_a_field=3)

        self.assertIn(
            "1 validation error for Node\nis_not_a_field\n  Extra inputs are not permitted",
            str(ve.exception)
        )

    def test_node_hash(self):
        a = Node(label='a')
        b = Node(label='a')
        c = Node(label='c')
        d = Node(label='c', parents=(b, c))

        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(b), hash(c))
        self.assertNotEqual(hash(c), hash(d))

    def test_node_get_parents(self):
        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        self.assertEqual(c.get_parents(), (a, b))

    def test_node_get_ancestors(self):
        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        d = Node(label='d')
        e = Node(label='e', parents=(c, d))
        self.assertSequenceEqual([c, a, b, d], e.get_ancestors())

    def test_node_is_leaf(self):
        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        self.assertTrue(a.is_leaf())
        self.assertTrue(b.is_leaf())
        self.assertFalse(c.is_leaf())

    def test_node_is_immutable(self):
        with self.assertRaises(ValidationError) as ve:
            a = Node(label='2')
            a.label_ = '1'

        self.assertIn(
            "Instance is frozen [type=frozen_instance, input_value='1', input_type=str]",
            str(ve.exception)
        )

    def test_map(self):

        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        d = Node(label='d')
        e = Node(label='e', parents=(c, d))

        def fn(x: Node, parents) -> Node:
            return Node(label=x.get_label().upper(), parents=parents)

        e_mod = e.apply_map(fn)
        self.assertNotEqual(e_mod, e)

        exp = sorted([n.get_label().upper() for n in e.get_ancestors()])
        obs = sorted([n.get_label() for n in e_mod.get_ancestors()])
        self.assertSequenceEqual(exp, obs)

    def test_topological_sort(self):

        a = Node(label='a')
        b = Node(label='b')
        c = Node(label='c', parents=(a, b))
        d = Node(label='d')
        e = Node(label='e', parents=(c, d))
        f = Node(label='f', parents=(b, e))

        topo_sort = f.topological_sort()
        exp = [b, a, d, c, e, f]
        self.assertSequenceEqual(exp, topo_sort)
