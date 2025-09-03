from lumipy.lumiflex._column.widgets import column_object_widget
from lumipy.lumiflex._common.widgets import subtitle, subsubtitle, code, WidgetNode, link_node
from lumipy.lumiflex._metadata.widgets import columns_widget


def join_table_widget(join, top_line=True):
    join_type = join.join_type_.capitalize()
    label = subtitle(f'{join_type} Join Table', 'slate') if top_line else subsubtitle(f'{join_type} Join Table', 'slate')
    lhs, rhs, on = join.get_parents()

    lhs_is_join = lhs.get_label() == 'join_table'
    if lhs_is_join:
        main_node = join_table_widget(lhs, False)
    else:
        lhs_label = code(lhs.meta_.alias)
        lhs_nodes = [table_widget(lhs, False, False)]
        main_node = WidgetNode(lhs_label, nodes=lhs_nodes, opened=lhs_is_join)

    nodes = [
        main_node,
        WidgetNode(code(rhs.meta_.alias), nodes=[table_widget(rhs, False, False)]),
        WidgetNode(subsubtitle('On', 'flame'), nodes=column_object_widget(join.get_join_condition(), True).nodes[:1], opened=True)
    ]
    node = WidgetNode(label, nodes=nodes, opened=True, icon='table', icon_style='warning', disabled=False)
    return node


def table_widget(table, opened, top_line=True) -> WidgetNode:
    meta = table.meta_
    name = '@' + meta.name if meta.type == 'TableVar' else meta.name

    if not top_line:
        nodes = [WidgetNode(subsubtitle('Type'), meta.type)]
    else:
        nodes = [
            WidgetNode(subsubtitle('Name'), code(name)),
            WidgetNode(subsubtitle('Type'), meta.type),
        ]

    if table.meta_.type != 'TableVar':
        nodes += [
            WidgetNode(subsubtitle('Description'), meta.description.split('\n')[0]),
            link_node('Documentation', meta.documentation_link),
            WidgetNode(subsubtitle('Category'), meta.category),
        ]

    if table.meta_.alias is not None:
        nodes.append(WidgetNode(subsubtitle('Alias'), code(table.meta_.alias)))

    nodes.append(columns_widget(meta))

    def param_code(val):
        if val.get_label() == 'data_table':
            return code('@' + val.meta_.name)
        else:
            return code(val.sql)

    # Param value assignments
    p_assigns = [WidgetNode(code(p.meta.python_name()), param_code(p.parents_[0])) for p in table.parameters_]
    if len(p_assigns) > 0:
        nodes.append(WidgetNode(subsubtitle('Parameter Assignments'), nodes=p_assigns, opened=True))

    # Provider Dependencies
    ancs = [table_widget(a, False, False) for a in table._get_table_ancestors() if a.meta_.type == 'DataProvider' and a.meta_.alias is None]
    if len(ancs) > 0:
        nodes.append(WidgetNode(subsubtitle('Dependencies'), nodes=ancs, icon='list-ul', opened=False))

    label = subtitle('Table', 'slate') if top_line else subsubtitle(name, 'slate')
    node = WidgetNode(label, nodes=nodes, opened=opened, icon='table', icon_style='warning', disabled=False)
    return node
