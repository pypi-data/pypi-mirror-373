from lumipy.lumiflex._common.widgets import WidgetNode, subsubtitle, code, subtitle


def column_object_widget(column, opened):
    if column.meta is not None:
        nodes = list(column.meta.widget(True).nodes)
        nodes.append(WidgetNode(subsubtitle('Origin Table'), code(column.meta.table_name)))
    else:
        nodes = [
            WidgetNode(subsubtitle('SQL'), code(column.sql.replace('\n', ' '))),
            WidgetNode(subsubtitle('SQL Type'), code(column.dtype.name)),
        ]
        origins = sorted(set(c.meta.table_name for c in column._get_data_col_dependencies()))
        origins = [code(o) for o in origins]
        nodes.append(WidgetNode(subsubtitle('Origin Tables'), *origins))

    label = subtitle('Column', 'slate')
    node = WidgetNode(label, nodes=nodes, opened=opened, icon='columns', icon_style='warning', disabled=False)
    return node
