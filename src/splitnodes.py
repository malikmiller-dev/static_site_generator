import re

from htmlnode import ParentNode, LeafNode, HTMLNode
from textnode import TextNode, TextType, BlockType, text_node_to_html_node


def split_nodes_delimiter(old_nodes, delimiter, text_type=None):
    result = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        pieces = node.text.split(delimiter)

        for i, piece in enumerate(pieces):
            if i % 2 == 0:
                result.append(TextNode(piece, TextType.TEXT))
            else:
                result.append(TextNode(piece, text_type))
    return result


def extract_markdown_images(text):
    regex_text = re.findall(r'!\[([^\[\]]*)]\(([^()]*)\)', text)
    return regex_text


def extract_markdown_links(text):
    regex_text = re.findall(r'(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)', text)
    return regex_text


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    node = [TextNode(text, TextType.TEXT)]
    node = split_nodes_delimiter(node, '**', TextType.BOLD)
    node = split_nodes_delimiter(node, '_', TextType.ITALIC)
    node = split_nodes_delimiter(node, '`', TextType.CODE)
    node = split_nodes_image(node)
    node = split_nodes_link(node)
    return node


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == '':
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(tn) for tn in text_nodes]


def convert_block_to_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        text = block.replace('\n', ' ')
        return ParentNode('p', text_to_children(text))
    elif block_type == BlockType.HEADING:
        hash_len = block.split(' ', 1)
        hash_count = len(hash_len[0])
        heading = f'h{hash_count}'
        return ParentNode(heading, text_to_children(hash_len[1]))
    elif block_type == BlockType.CODE:
        lines = block.split('\n')
        inner = '\n'.join(lines[1:-1]) + '\n'
        text_node = TextNode(inner, TextType.TEXT)
        code_leaf = text_node_to_html_node(text_node)
        return ParentNode('pre', [ParentNode('code', [code_leaf])])
    elif block_type == BlockType.QUOTE:
        lines = block.split('\n')
        cleaned = []
        for line in lines:
            cleaned.append(line.lstrip('>').strip())
        text = ' '.join(cleaned)
        return ParentNode('blockquote', text_to_children(text))
    elif block_type == BlockType.ORDERED_LIST:
        items = []
        for line in block.split('\n'):
            text = re.sub(r'^[ \t]*\d+\.[ \t]+', '', line)
            items.append(ParentNode('li', text_to_children(text)))
        return ParentNode('ol', items)
    elif block_type == BlockType.UNORDERED_LIST:
        items = []
        for line in block.split('\n'):
            text = re.sub(r'^[ \t]*[-*+][ \t]+', '', line)
            items.append(ParentNode('li', text_to_children(text)))
        return ParentNode('ul', items)
    raise NotImplementedError('block type not found')


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = [convert_block_to_node(b) for b in blocks]
    return ParentNode('div', children)
