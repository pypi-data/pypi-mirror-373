from lumipy.lumiflex._common.widgets import WidgetNode, subsubtitle, code, subtitle


def window_object_widget(window, opened):
    w_groups, w_order, w_frame, w_filter = window.get_parents()
    nodes = [
        WidgetNode(subsubtitle('Partition'), code(w_groups.get_sql() if w_groups.has_content() else 'None')),
        WidgetNode(subsubtitle('Ordering'), code(w_order.get_sql() if w_order.has_content() else 'None')),
        WidgetNode(subsubtitle('Frame'), code(w_frame.get_sql())),
        WidgetNode(subsubtitle('Filter'), code(w_filter.get_sql() if w_filter.has_content() else 'None')),
    ]
    node = WidgetNode(subtitle('Window', 'slate'), nodes=nodes, opened=opened, icon='fal fa-window-restore', icon_style='warning', disabled=False)
    return node
