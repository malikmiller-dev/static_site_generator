class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if not self.props:
            return ""
        return "".join(f' {k}="{v}"' for k, v in self.props.items())

    def __repr__(self):
        return f'Tag: {self.tag} Value: {self.value} Children: {self.children} Props: {self.props}'

    def __eq__(self, other):
        return (
                self.tag == other.tag
                and self.value == other.value
                and self.children == other.children
                and self.props == other.props
        )


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super(LeafNode, self).__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError('node must have value')

        if self.tag is None:
            return self.value

        props_html = ''

        if self.props:
            props_html = "".join(f' {k}="{v}"' for k, v in self.props.items())

        return f"<{self.tag}{props_html}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f'Tag: {self.tag} Value: {self.value} Props: {self.props}'


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError('node must have tag')
        if not self.children:
            raise ValueError('node must have children')

        children_html = "".join(child.to_html() for child in self.children)
        return f'<{self.tag}>{children_html}</{self.tag}>'
