from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._common.widgets import *


class TestCommonWidgets(SqlTestCase):

    def test_title_function(self):

        t1 = title('Test Title')
        self.assertEqual('<b style="color:#415464;font-size:22px;">Test Title</b>', t1)

        t2 = title('Test Title', 'flame')
        self.assertEqual('<b style="color:#FF5200;font-size:22px;">Test Title</b>', t2)

    def test_subtitle_function(self):

        t1 = subtitle('Test subtitle')
        self.assertEqual('<b style="color:#415464;font-size:16px;">Test subtitle</b>', t1)

        t2 = subtitle('Test subtitle', 'flame')
        self.assertEqual('<b style="color:#FF5200;font-size:16px;">Test subtitle</b>', t2)

    def test_subsubtitle_function(self):

        t1 = subsubtitle('Test subsubtitle')
        self.assertEqual('<b style="color:#415464;font-size:12px;">Test subsubtitle</b>', t1)

        t2 = subsubtitle('Test subsubtitle', 'flame')
        self.assertEqual('<b style="color:#FF5200;font-size:12px;">Test subsubtitle</b>', t2)

    def test_code_function(self):
        self.assertEqual('<code>print("Hello, World!")</code>', code('print("Hello, World!")'))

    def test_loading_node_function(self):
        nodes = loading_node()
        self.assertEqual(1, len(nodes))

        node = nodes[0]
        self.assertEqual(subsubtitle('Loading...', 'flame'), node.name)
        self.assertEqual('cog', node.icon)

    def test_widget_node_ctor_defaults(self):

        node = WidgetNode('TESTING', '123')
        self.assertEqual('TESTING 123', node.name)
        self.assertEqual(min_bullet, node.icon)
        self.assertEqual(0, len(node.nodes))
        self.assertFalse(node.opened)
        self.assertEqual('default', node.icon_style)
        self.assertTrue(node.disabled)

    def test_widget_node_ctor(self):
        nodes = [WidgetNode('A'), WidgetNode('B')]
        node = WidgetNode('testing', '321', nodes=nodes, opened=True, icon='square', icon_style='warning', disabled=False)
        self.assertEqual('testing 321', node.name)
        self.assertEqual('square', node.icon)
        self.assertEqual(2, len(node.nodes))
        self.assertTrue(node.opened)
        self.assertEqual('warning', node.icon_style)
        self.assertFalse(node.disabled)

    def test_link_node_url(self):
        node = link_node('Docs', 'https://some.docs.com/')
        self.assertEqual('<b style="color:#415464;font-size:12px;">Docs</b> <u>link</u>', node.name)
        self.assertEqual('fas fa-external-link', node.icon)
        self.assertFalse(node.disabled)

    def test_link_node_no_url(self):
        node = link_node('testing', 'Not available')
        self.assertEqual('<b style="color:#415464;font-size:12px;">testing</b> Not available', node.name)
        self.assertEqual('fas fa-unlink', node.icon)
