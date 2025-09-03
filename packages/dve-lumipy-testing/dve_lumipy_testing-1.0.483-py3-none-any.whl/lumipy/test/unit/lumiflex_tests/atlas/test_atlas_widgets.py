from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._atlas.widgets import *


class TestAtlasWidgets(SqlTestCase):

    def test_info_and_help_function(self):

        info = info_and_help()
        self.assertEqual('<b style="color:#415464;font-size:16px;">Information & Help</b>', info.name)
        self.assertEqual('info-circle', info.icon)

        intro, arch, tut, ref, how2, prov = info.nodes
        self.assertEqual('<b style="color:#415464;font-size:12px;">Introduction</b> <u>link</u>', intro.name)
        self.assertFalse(intro.disabled)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Platform Architecture</b> <u>link</u>', arch.name)
        self.assertFalse(arch.disabled)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Tutorials</b> <u>link</u>', tut.name)
        self.assertFalse(tut.disabled)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Reference</b> <u>link</u>', ref.name)
        self.assertFalse(ref.disabled)
        self.assertEqual('<b style="color:#415464;font-size:12px;">How-to Guides</b> <u>link</u>', how2.name)
        self.assertFalse(how2.disabled)
        self.assertEqual('<b style="color:#415464;font-size:12px;">Providers</b> <u>link</u>', prov.name)
        self.assertFalse(prov.disabled)

    def test_provider_widget_function_top_line(self):

        meta = self.make_provider_meta('my.test.provider', 10, 2, 1)

        node = provider_widget(meta, True, True)
        self.assertEqual(subtitle('Provider'), node.name)
        self.assertTrue(node.opened)

        self.assertEqual(7, len(node.nodes))
        sql_name, prov_type, cat, descr, docs, cols, params = node.nodes

        self.assertEqual(subsubtitle('SQL Name') + ' ' + code(meta.name), sql_name.name)
        self.assertEqual(subsubtitle('Provider Type') + ' ' + meta.type, prov_type.name)
        self.assertEqual(subsubtitle('Category') + ' ' + meta.category, cat.name)
        self.assertEqual(subsubtitle('Description') + ' ' + meta.description.split('\n')[0], descr.name)
        self.assertEqual(subsubtitle('Documentation') + ' No documentation link available', docs.name)
        self.assertEqual(subsubtitle('Columns'), cols.name)
        self.assertEqual(subsubtitle('Parameters'), params.name)

    def test_provider_widget_function_not_top_line_and_closed(self):

        meta = self.make_provider_meta('my.test.provider', 10, 2, 1)

        node = provider_widget(meta, False, False)
        self.assertEqual('<code>my_test_provider</code>', node.name)
        self.assertFalse(node.opened)
        self.assertEqual(1, len(node.nodes))

    def test_atlas_widget(self):
        atlas = self.make_atlas(None)
        factory = CatalogueFactory(atlas)

        node = factory.build()
        self.assertEqual('<b style="color:#415464;font-size:22px;">Atlas</b><code>domain = nowhere</code>', node.name)
        self.assertEqual('globe', node.icon)
        self.assertEqual(2, len(node.nodes))

        providers, info = node.nodes

        # info
        self.assertEqual('<b style="color:#415464;font-size:16px;">Information & Help</b>', info.name)
        self.assertEqual('info-circle', info.icon)
        self.assertEqual(6, len(info.nodes))

        # providers
        self.assertEqual('<b style="color:#FF5200;font-size:16px;">Providers</b>', providers.name)
        self.assertEqual('bars', providers.icon)
        self.assertEqual(1, len(providers.nodes))  # Loading message

    def test_filtered_atlas_widget(self):

        atlas = self.make_atlas(None).search('*instrument*')
        factory = CatalogueFactory(atlas)

        node = factory.build()
        # Should show the filter string
        self.assertEqual('<b style="color:#415464;font-size:22px;">Atlas</b><code>domain = nowhere</code> <code>filter = \'*instrument*\'</code>', node.name)
        self.assertEqual('globe', node.icon)
        self.assertEqual(2, len(node.nodes))

        providers, info = node.nodes

        # info
        self.assertEqual('<b style="color:#415464;font-size:16px;">Information & Help</b>', info.name)
        self.assertEqual('info-circle', info.icon)
        self.assertEqual(6, len(info.nodes))

        # providers
        # Should have the provider folders loaded in this case
        self.assertEqual('<b style="color:#FF5200;font-size:16px;">Providers</b>', providers.name)
        self.assertEqual('bars', providers.icon)
        self.assertEqual(2, len(providers.nodes))

