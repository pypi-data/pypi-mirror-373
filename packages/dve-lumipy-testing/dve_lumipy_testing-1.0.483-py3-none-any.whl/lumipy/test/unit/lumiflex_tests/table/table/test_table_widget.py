from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.widgets import table_widget


class TestTableWidget(SqlTestCase):

    def test_data_provider_table_widget(self):
        node = table_widget(self.make_table(n_tv_params=1), True, True)
        self.assertEqual('<b style="color:#415464;font-size:16px;">Table</b>', node.name)
        self.assertTrue(node.opened)
        self.assertEqual('table', node.icon)

        self.assertEqual(8, len(node.nodes))
        name, ptype, descr, docs, cat, cols, params, deps = node.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">Name</b> <code>My.Test.Table</code>', name.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Type</b> DataProvider', ptype.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Description</b> No description available', descr.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Documentation</b> No documentation link available', docs.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Category</b> Testing', cat.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Columns</b>', cols.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Parameter Assignments</b>', params.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Dependencies</b>', deps.name)

        # Param fields
        self.assertEqual(4, len(params.nodes))

        # Dependencies
        self.assertEqual(1, len(deps.nodes))
        tv1 = deps.nodes[0]
        self.assertEqual('<b style="color:#415464;font-size:12px;">TableVar_0.test.table</b>', tv1.name)

    def test_table_var_table_widget(self):
        tv = self.make_table(n_tv_params=1).select('^').to_table_var('test_table')
        node = table_widget(tv, True, True)

        self.assertEqual('<b style="color:#415464;font-size:16px;">Table</b>', node.name)
        self.assertTrue(node.opened)
        self.assertEqual('table', node.icon)

        self.assertEqual(4, len(node.nodes))
        name, ptype, cols, deps = node.nodes

        self.assertEqual('<b style="color:#415464;font-size:12px;">Name</b> <code>@test_table</code>', name.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Type</b> TableVar', ptype.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Columns</b>', cols.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Dependencies</b>', deps.name)

        self.assertEqual(2, len(deps.nodes))
        t1, t2 = deps.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">My.Test.Table</b>', t1.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">My.Test.Table</b>', t1.name)
