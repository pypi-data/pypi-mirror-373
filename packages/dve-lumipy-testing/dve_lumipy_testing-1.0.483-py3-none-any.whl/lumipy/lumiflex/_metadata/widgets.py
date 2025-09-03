from lumipy.lumiflex._common.widgets import WidgetNode, subsubtitle, code, loading_node


def table_parameter_meta_widget(tp, opened) -> WidgetNode:

    if len(tp.columns) > 0:
        cols = [column_meta_widget(c, False) for c in tp.columns]
    else:
        cols = [WidgetNode('No schema', icon='warning')]

    nodes = [WidgetNode(subsubtitle('Columns'), nodes=cols, opened=True, icon='columns')]

    node = WidgetNode(
        code(tp.python_name()), code('table'),
        icon='table',
        icon_style='warning',
        opened=opened,
        nodes=nodes
    )

    return node


def columns_widget(meta) -> WidgetNode:
    node = WidgetNode(subsubtitle('Columns'), icon='columns')

    def on_open(event):
        root = event['owner']
        if meta.columns is not None:
            root.nodes = [column_meta_widget(cm, False) for cm in meta.columns]
        else:
            root.nodes = [WidgetNode(subsubtitle('Column content defined at query time.', 'flame'), icon='warning')]

    node.observe(on_open, 'opened')
    node.nodes = loading_node()
    return node


def column_meta_widget(c, opened: bool) -> WidgetNode:
    node = WidgetNode(code(c.python_name()), code(c.dtype.to_pytype().__name__), opened=opened)

    node.nodes = [
        WidgetNode(subsubtitle('SQL Name'), code(c.field_name)),
        WidgetNode(subsubtitle('SQL Type'), code(c.dtype.name)),
        WidgetNode(subsubtitle('Description'), c.description),
        WidgetNode(subsubtitle('Is Main'), c.is_main),
        WidgetNode(subsubtitle('Is Primary Key'), c.is_primary_key),
    ]
    return node


def parameters_widget(meta) -> WidgetNode:
    node = WidgetNode(subsubtitle('Parameters'), icon='cogs')

    def on_open(event):
        root = event['owner']
        nodes = [parameter_meta_widget(p, False) for p in meta.parameters]
        nodes += [table_parameter_meta_widget(tp, False) for tp in meta.table_parameters]
        root.nodes = nodes

    node.observe(on_open, 'opened')
    node.nodes = loading_node()
    return node


def parameter_meta_widget(meta, opened) -> WidgetNode:
    node = WidgetNode(code(meta.python_name()), code(meta.dtype.to_pytype().__name__), opened=opened)
    node.nodes = [
        WidgetNode(subsubtitle('SQL Name'), code(meta.field_name)),
        WidgetNode(subsubtitle('SQL Type'), code(meta.dtype.name)),
        WidgetNode(subsubtitle('Description'), meta.description),
        WidgetNode(subsubtitle('Default'), meta.default_str),
    ]
    return node
