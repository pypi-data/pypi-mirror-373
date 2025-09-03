from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._column.widgets import *


class TestColumnWidget(SqlTestCase):

    def test_column_object_widget_data_column(self):
        col = self.make_table().col0
        node = column_object_widget(col, False)
        self.assertEqual('<b style="color:#415464;font-size:16px;">Column</b>', node.name)
        self.assertEqual('columns', node.icon)
        self.assertFalse(node.opened)
        self.assertEqual(6, len(node.nodes))
        sql_name, sql_type, descr, is_main, is_pk, origin = node.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">SQL Name</b> <code>Col0</code>', sql_name.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">SQL Type</b> <code>Int</code>', sql_type.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Description</b> No description available', descr.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Is Main</b> True', is_main.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Is Primary Key</b> False', is_pk.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Origin Table</b> <code>My.Test.Table</code>', origin.name)

    def test_column_object_widget_column_function(self):
        col = self.make_table().col0 * 10
        node = column_object_widget(col, False)
        self.assertEqual('<b style="color:#415464;font-size:16px;">Column</b>', node.name)
        self.assertEqual('columns', node.icon)
        self.assertFalse(node.opened)
        self.assertEqual(3, len(node.nodes))
        sql_name, sql_type, origin = node.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">SQL</b> <code>[Col0] * 10</code>', sql_name.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">SQL Type</b> <code>Int</code>', sql_type.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Origin Tables</b> <code>My.Test.Table</code>', origin.name)
