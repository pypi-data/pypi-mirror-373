from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.widgets import join_table_widget


class TestJoinTableWidget(SqlTestCase):

    def test_inner_join_table_widget(self):
        t1 = self.make_table('my.table.one')
        t2 = self.make_table('my.table.two')

        join = t1.inner_join(t2, t1.col0 == t2.col0)
        node = join_table_widget(join, True)

        self.assertEqual('<b style="color:#415464;font-size:16px;">Inner Join Table</b>', node.name)

        self.assertEqual(3, len(node.nodes))
        lhs, rhs, on = node.nodes
        self.assertEqual('<code>lhs</code>', lhs.name)
        self.assertEqual('<code>rhs</code>', rhs.name)
        self.assertEqual('<b style="color:#FF5200;font-size:12px;">On</b>', on.name)

        self.assertEqual(1, len(lhs.nodes))
        self.assertEqual(1, len(rhs.nodes))

        lhs_table = lhs.nodes[0]
        rhs_table = rhs.nodes[0]
        self.assertEqual('<b style="color:#415464;font-size:12px;">my.table.one</b>', lhs_table.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">my.table.two</b>', rhs_table.name)

    def test_left_join_table_widget(self):
        t1 = self.make_table('my.table.one')
        t2 = self.make_table('my.table.two')

        join = t1.left_join(t2, t1.col0 == t2.col0)
        node = join_table_widget(join, True)

        self.assertEqual('<b style="color:#415464;font-size:16px;">Left Join Table</b>', node.name)

        self.assertEqual(3, len(node.nodes))
        lhs, rhs, on = node.nodes
        self.assertEqual('<code>lhs</code>', lhs.name)
        self.assertEqual('<code>rhs</code>', rhs.name)
        self.assertEqual('<b style="color:#FF5200;font-size:12px;">On</b>', on.name)

        self.assertEqual(1, len(lhs.nodes))
        self.assertEqual(1, len(rhs.nodes))

        lhs_table = lhs.nodes[0]
        rhs_table = rhs.nodes[0]
        self.assertEqual('<b style="color:#415464;font-size:12px;">my.table.one</b>', lhs_table.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">my.table.two</b>', rhs_table.name)

    def test_chained_join_table_widget(self):
        t1 = self.make_table('my.table.one')
        t2 = self.make_table('my.table.two')
        t3 = self.make_table('my.table.three')

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 't1', 't2'
        ).inner_join(
            t3, t1.col0 == t3.col0, 't3'
        )

        node = join_table_widget(join, True)

        self.assertEqual('<b style="color:#415464;font-size:16px;">Inner Join Table</b>', node.name)
        self.assertEqual(3, len(node.nodes))
        lhs, rhs, on = node.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">Inner Join Table</b>', lhs.name)
        self.assertEqual('<code>t3</code>', rhs.name)
        self.assertEqual('<b style="color:#FF5200;font-size:12px;">On</b>', on.name)

        self.assertEqual(3, len(lhs.nodes))
        lhs, rhs, on = lhs.nodes
        self.assertEqual('<code>t1</code>', lhs.name)
        self.assertEqual('<code>t2</code>', rhs.name)
        self.assertEqual('<b style="color:#FF5200;font-size:12px;">On</b>', on.name)
