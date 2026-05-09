from enum import Enum
from htmlnode import LeafNode


class TextType(Enum):
    TEXT = 'text'
    ITALIC = 'italic'
    CODE = 'code'
    LINK = 'link'
    IMAGE = 'image'
    BOLD = 'bold'


class BlockType(Enum):
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'


class TextNode:
    def __init__(self, text, text_type=None, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
                self.text == other.text
                and self.text_type == other.text_type
                and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def text_node_to_html_node(text_node):
    if TextType.TEXT == text_node.text_type:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode('b', text_node.text, None)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode('i', text_node.text, None)
    if text_node.text_type == TextType.CODE:
        return LeafNode('code', text_node.text, None)
    if text_node.text_type == BlockType.HEADING:
        if text_node.tag == 'h1':
            return LeafNode('h1', text_node.text, None)
        if text_node.tag == 'h2':
            return LeafNode('h2', text_node.text, None)
        if text_node.tag == 'h3':
            return LeafNode('h3', text_node.text, None)
        if text_node.tag == 'h4':
            return LeafNode('h4', text_node.text, None)
        if text_node.tag == 'h5':
            return LeafNode('h5', text_node.text, None)
        if text_node.tag == 'h6':
            return LeafNode('h6', text_node.text, None)
    if text_node.text_type == TextType.LINK:
        return LeafNode('a', text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode('img', '', {"src": text_node.url, "alt": text_node.text})

    raise Exception('Text Type not found')
