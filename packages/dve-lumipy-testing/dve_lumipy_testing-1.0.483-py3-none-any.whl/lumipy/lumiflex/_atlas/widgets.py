from lumipy.lumiflex._common.widgets import title, subtitle, code, WidgetNode, loading_node, subsubtitle, \
    link_node
from lumipy.lumiflex._metadata.widgets import columns_widget, parameters_widget


def folder(name, content, opened) -> WidgetNode:
    if name == '$':
        node = WidgetNode(subtitle('Providers', 'flame'), opened=opened, icon='bars')
    else:
        node = WidgetNode(name, opened=opened, icon='folder-o')

    def children():
        nodes = []
        keys = sorted(content.keys())
        for k in keys:
            v = content[k]
            if k != '_MetaData':
                nodes.append(folder(k, v, False))
            else:
                nodes = [provider_widget(p, False, False) for p in v]
        return nodes

    if opened:
        node.nodes = children()
    else:
        def on_open(event):
            root = event['owner']
            root.nodes = children()

        node.observe(on_open, 'opened')
        node.nodes = loading_node()

    return node


class CatalogueFactory:

    def __init__(self, atlas):

        self.atlas = atlas
        self.filter_str = atlas._filter_str
        tree_map = {'$': {}}

        for meta in atlas._provider_metas:

            head = tree_map['$']
            chunks = meta.name.split('.')

            for i, chunk in enumerate(chunks):

                if chunk not in head:
                    head[chunk] = {}

                if i == meta.namespace_level:
                    if '_MetaData' not in head[chunk]:
                        head[chunk]['_MetaData'] = [meta]
                    else:
                        head[chunk]['_MetaData'].append(meta)
                    break

                head = head[chunk]

        self.tree = tree_map

    def build(self):

        providers = folder('$', self['$'], self.filter_str is not None)
        info = info_and_help()

        domain = self.atlas.get_client().get_domain()
        atlas_header = [title(f'Atlas', 'slate') + code(f'domain = {domain}')]
        if self.filter_str is not None:
            atlas_header.append(code(f"filter = \'{self.filter_str}\'"))

        top = WidgetNode(
            *atlas_header,
            nodes=[providers, info],
            icon='globe',
            opened=True
        )
        return top

    def __getitem__(self, key):

        parts = key.split('.')

        head = self.tree[parts[0]]
        for part in parts[1:]:
            head = head[part]

        return head


def info_and_help() -> WidgetNode:
    fields = {
        'Introduction': 'https://support.lusid.com/knowledgebase/article/KA-01677/en-us',
        'Platform Architecture': 'https://support.lusid.com/knowledgebase/article/KA-01707/en-us',
        'Tutorials': 'https://support.lusid.com/knowledgebase/category/?id=CAT-01056',
        'Reference': 'https://support.lusid.com/knowledgebase/category/?id=CAT-01059',
        'How-to Guides': 'https://support.lusid.com/knowledgebase/category/?id=CAT-01061',
        'Providers': 'https://support.lusid.com/knowledgebase/category/?id=CAT-01099',
    }

    lumi_nodes = [link_node(label, url) for label, url in fields.items()]
    node = WidgetNode(subtitle("Information & Help", 'slate'), nodes=lumi_nodes, icon='info-circle')
    return node


def provider_widget(meta, opened, top_line=True) -> WidgetNode:

    def child_nodes():
        nodes = [
            WidgetNode(subsubtitle('SQL Name'), code(meta.name)),
            WidgetNode(subsubtitle('Provider Type'), meta.type),
            WidgetNode(subsubtitle('Category'), meta.category),
            WidgetNode(subsubtitle('Description'), meta.description.split('\n')[0]),
            link_node('Documentation', meta.documentation_link),
            columns_widget(meta),
        ]
        if len(meta.parameters + meta.table_parameters) > 0:
            nodes.append(parameters_widget(meta))
        return nodes

    def on_open(event):
        event['owner'].nodes = child_nodes()

    label = subtitle('Provider', 'slate') if top_line else code(meta.python_name())
    node = WidgetNode(label, opened=opened, icon='database', icon_style='warning', disabled=False)
    if opened:
        node.nodes = child_nodes()
    else:
        node.observe(on_open, 'opened')
        node.nodes = loading_node()

    return node
