from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._window.widgets import window_object_widget


class TestWindowWidget(SqlTestCase):

    def test_window_widget(self):
        table = self.make_table()
        window = self.make_window(table).filter(table.col0 > 4)
        node = window_object_widget(window, True)

        self.assertEqual('<b style="color:#415464;font-size:16px;">Window</b>', node.name)
        self.assertEqual('fal fa-window-restore', node.icon)
        self.assertTrue(node.opened)

        self.assertEqual(4, len(node.nodes))
        part, order, frame, fltr = node.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">Partition</b> <code>PARTITION BY [Col0], [Col1], [Col2], [Col3]</code>', part.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Ordering</b> <code>ORDER BY [Col0] ASC, [Col1] ASC</code>', order.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Frame</b> <code>ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS</code>', frame.name)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Filter</b> <code>FILTER(WHERE ([Col0] > 4))</code>', fltr.name)
