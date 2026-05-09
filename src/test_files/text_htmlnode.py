import unittest

from src.htmlnode import HTMLNode, ParentNode, LeafNode


class HTMLNodeTest(unittest.TestCase):
    def test(self):
        node = HTMLNode('p', 'example paragraph test', [], {'<p>', 'example pair paragraph text'})
        node2 = HTMLNode('p', 'example paragraph test', [], {'<p>', 'example pair paragraph text'})
        node3 = HTMLNode('a', 'example paragraph test', [], {'<a>', 'example pair paragraph text'})
        node4 = HTMLNode('p', 'example paragraph test', [], {'<p>', 'example pair paragraph text'})
        self.assertEqual(node, node2)
        self.assertNotEqual(node3, node4, f'\n\bis equal')
        self.assertIsNot(node, node3)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        node2 = LeafNode("a", "Click Me!", {"href": "https://www.google.com"})
        self.assertEqual(node2.to_html(), '<a href="https://www.google.com">Click Me!</a>')


class ParentNodeTest(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        print(child_node.to_html())
        print(type(child_node.to_html()))
        parent_node = ParentNode("div", [child_node])
        print(parent_node)
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        print(parent_node.to_html())
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )


if __name__ == "__main__":
    unittest.main()
