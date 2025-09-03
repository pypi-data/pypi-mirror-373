from typing import Literal
from webbrowser import open as page_open

from ipytree import Node, Tree

min_bullet = 'caret-right'
colours = {
    'slate': '#415464',
    'flame': '#FF5200',
}
fonts = {
    'title': 22,
    'subtitle': 16,
    'subsubtitle': 12,
}


def node_label(
    text,
    label_type: Literal['title', 'subtitle', 'subsubtitle', 'code'],
    colour: Literal['slate', 'flame', 'none'] = 'none'
):
    c_hex = colours[colour]
    font_size = fonts[label_type]
    return f'<b style="color:{c_hex};font-size:{font_size}px;">{text}</b>'


def title(text, colour: Literal['slate', 'flame', 'none'] = 'slate'):
    return node_label(text, 'title', colour)


def subtitle(text, colour: Literal['slate', 'flame', 'none'] = 'slate'):
    return node_label(text, 'subtitle', colour)


def subsubtitle(text, colour: Literal['slate', 'flame', 'none'] = 'slate'):
    return node_label(text, 'subsubtitle', colour)


def code(text):
    return f'<code>{text}</code>'


def loading_node():
    return [Node(subsubtitle('Loading...', 'flame'), icon='cog')]


class WidgetNode(Node):

    def __init__(self, *args, **kwargs):
        name = ' '.join(str(a) for a in args)
        nodes = kwargs.get('nodes', [])
        super().__init__(
            name,
            nodes,
            opened=kwargs.get('opened', False),
            icon=kwargs.get('icon', min_bullet),
            icon_style=kwargs.get('icon_style', 'default'),
            disabled=kwargs.get('disabled', True)
        )


def link_node(label, url):
    if not url.startswith('http'):
        return WidgetNode(subsubtitle(label), url, icon='fas fa-unlink')

    def open_page(event):
        page_open(url)
        root = event['owner']
        root.selected = False

    node = WidgetNode(subsubtitle(label), '<u>link</u>', icon='fas fa-external-link', disabled=False)
    node.observe(open_page, 'selected')
    return node


def display(node, *args, **kwargs):
    tree = Tree()
    tree.add_node(node)
    return tree._repr_mimebundle_(*args, **kwargs)
