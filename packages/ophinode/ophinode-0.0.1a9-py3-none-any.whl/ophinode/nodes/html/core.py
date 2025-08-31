from ..base import (
    ClosedRenderable,
    OpenRenderable,
    Expandable,
    Preparable,
)
from ophinode.exceptions import InvalidAttributeNameError

_default_escape_ampersands = False
_default_escape_tag_delimiters = True

def default_escape_ampersands(value: bool = True):
    global _default_escape_ampersands
    _default_escape_ampersands = bool(value)

def default_escape_tag_delimiters(value: bool = True):
    global _default_escape_tag_delimiters
    _default_escape_tag_delimiters = bool(value)

class Node:
    pass

class TextNode(Node, ClosedRenderable):
    def __init__(
        self,
        text_content: str,
        *,
        escape_ampersands: bool = None,
        escape_tag_delimiters: bool = None,
    ):
        self._text_content = text_content
        self._escape_ampersands = escape_ampersands
        self._escape_tag_delimiters = escape_tag_delimiters

    def render(self, context: "ophinode.site.BuildContext"):
        text_content = self._text_content

        escape_ampersands = self._escape_ampersands
        if escape_ampersands is None:
            escape_ampersands = _default_escape_ampersands
        if escape_ampersands:
            text_content = text_content.replace("&", "&amp;")

        escape_tag_delimiters = self._escape_tag_delimiters
        if escape_tag_delimiters is None:
            escape_tag_delimiters = _default_escape_tag_delimiters
        if escape_tag_delimiters:
            text_content = text_content.replace("<", "&lt;").replace(">", "&gt;")

        return text_content

    def escape_ampersands(self, value: bool = True):
        self._escape_ampersands = bool(value)
        return self

    def escape_tag_delimiters(self, value: bool = True):
        self._escape_tag_delimiters = bool(value)
        return self

class HTML5Doctype(Node, ClosedRenderable):
    def render(self, context: "ophinode.site.BuildContext"):
        return "<!doctype html>"

class CDATASection(Node, OpenRenderable, Expandable, Preparable):
    def __init__(self, *args):
        self._children = list(args)

    def prepare(self, context: "ophinode.site.BuildContext"):
        for c in self._children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.site.BuildContext"):
        return self._children.copy()

    def render_start(self, context: "ophinode.site.BuildContext"):
        return "<![CDATA[".format(self.tag)

    def render_end(self, context: "ophinode.site.BuildContext"):
        return "]]>".format(self.tag)

    @property
    def children(self):
        return self._children

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

class Comment(Node, OpenRenderable, Expandable, Preparable):
    def __init__(self, *args):
        self._children = list(args)

    def prepare(self, context: "ophinode.site.BuildContext"):
        for c in self._children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.site.BuildContext"):
        return self._children.copy()

    def render_start(self, context: "ophinode.site.BuildContext"):
        return "<!--".format(self.tag)

    def render_end(self, context: "ophinode.site.BuildContext"):
        return "-->".format(self.tag)

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

class Element(Node):
    def render_attributes(self):
        attribute_order = []
        keys = set(self._attributes)
        for k in ["id", "class", "style", "title"]:
            if k in keys:
                attribute_order.append(k)
                keys.remove(k)
        attribute_order += sorted(keys)

        rendered = []
        for k in attribute_order:
            for c in k:
                if c in " \"'>/=":
                    raise InvalidAttributeNameError(k)
            v = self._attributes[k]
            if isinstance(v, bool):
                if v:
                    rendered.append("{}".format(k))
            else:
                escaped = str(v)

                escape_ampersands = self._escape_ampersands
                if escape_ampersands is None:
                    escape_ampersands = _default_escape_ampersands
                if escape_ampersands:
                    escaped = escaped.replace("&", "&amp;")

                escape_tag_delimiters = self._escape_tag_delimiters
                if escape_tag_delimiters is None:
                    escape_tag_delimiters = _default_escape_tag_delimiters
                if escape_tag_delimiters:
                    escaped = escaped.replace("<", "&lt;").replace(">", "&gt;")

                escaped = escaped.replace("\"", "&quot;")
                rendered.append("{}=\"{}\"".format(k, escaped))

        return " ".join(rendered)

    @property
    def attributes(self):
        return self._attributes

    def escape_ampersands(self, value: bool = True):
        self._escape_ampersands = bool(value)
        return self

    def escape_tag_delimiters(self, value: bool = True):
        self._escape_tag_delimiters = bool(value)
        return self

class OpenElement(Element, OpenRenderable, Expandable, Preparable):
    tag = "div"
    render_mode = "hierarchy"

    def __init__(
        self,
        *args,
        cls = None,
        className = None,
        class_name = None,
        htmlFor = None,
        html_for = None,
        htmlAs = None,
        html_as = None,
        htmlAsync = None,
        html_async = None,
        accept_charset = None,
        escape_ampersands = None,
        escape_tag_delimiters = None,
        children = None,
        attributes = None,
        **kwargs
    ):
        self._children = list(args)
        if children is not None:
            for c in children:
                self._children.append(c)
        self._attributes = {}
        if attributes is not None:
            for k, v in attributes.items():
                self._attributes[k] = v
        kwargs_copy = dict(kwargs)
        for k, v in kwargs_copy.items():
            self._attributes[k] = v
        if cls is not None:
            self._attributes["class"] = cls
        if className is not None:
            self._attributes["class"] = className
        if class_name is not None:
            self._attributes["class"] = class_name
        if htmlFor is not None:
            self._attributes["for"] = htmlFor
        if html_for is not None:
            self._attributes["for"] = html_for
        if htmlAs is not None:
            self._attributes["as"] = htmlAs
        if html_as is not None:
            self._attributes["as"] = html_as
        if htmlAsync is not None:
            self._attributes["async"] = htmlAsync
        if html_async is not None:
            self._attributes["async"] = html_async
        if accept_charset is not None:
            self._attributes["accept-charset"] = accept_charset
        self._escape_ampersands = escape_ampersands
        self._escape_tag_delimiters = escape_tag_delimiters

    def prepare(self, context: "ophinode.site.BuildContext"):
        for c in self._children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.site.BuildContext"):
        expansion = []
        for c in self._children:
            if isinstance(c, str):
                node = TextNode(c)
                if self._escape_ampersands is not None:
                    node.escape_ampersands(self._escape_ampersands)
                if self._escape_tag_delimiters is not None:
                    node.escape_tag_delimiters(self._escape_tag_delimiters)
                expansion.append(node)
            else:
                expansion.append(c)
        return expansion

    def render_start(self, context: "ophinode.site.BuildContext"):
        rendered_attributes = self.render_attributes()
        if rendered_attributes:
            return "<{} {}>".format(self.tag, rendered_attributes)
        return "<{}>".format(self.tag)

    def render_end(self, context: "ophinode.site.BuildContext"):
        return "</{}>".format(self.tag)

    @property
    def children(self):
        return self._children

    @property
    def auto_newline(self):
        return self.render_mode == "hierarchy"

    @property
    def auto_indent(self):
        return self.render_mode == "phrase" or self.render_mode == "hierarchy"

class ClosedElement(Element, ClosedRenderable):
    tag = "meta"

    def __init__(
        self,
        *,
        cls = None,
        className = None,
        class_name = None,
        htmlFor = None,
        html_for = None,
        htmlAs = None,
        html_as = None,
        htmlAsync = None,
        html_async = None,
        accept_charset = None,
        escape_ampersands = None,
        escape_tag_delimiters = None,
        attributes = None,
        **kwargs
    ):
        self._attributes = {}
        if attributes is not None:
            for k, v in attributes.items():
                self._attributes[k] = v
        kwargs_copy = dict(kwargs)
        for k, v in kwargs_copy.items():
            self._attributes[k] = v
        if cls is not None:
            self._attributes["class"] = cls
        if className is not None:
            self._attributes["class"] = className
        if class_name is not None:
            self._attributes["class"] = class_name
        if htmlFor is not None:
            self._attributes["for"] = htmlFor
        if html_for is not None:
            self._attributes["for"] = html_for
        if htmlAs is not None:
            self._attributes["as"] = htmlAs
        if html_as is not None:
            self._attributes["as"] = html_as
        if htmlAsync is not None:
            self._attributes["async"] = htmlAsync
        if html_async is not None:
            self._attributes["async"] = html_async
        if accept_charset is not None:
            self._attributes["accept-charset"] = accept_charset
        self._escape_ampersands = escape_ampersands
        self._escape_tag_delimiters = escape_tag_delimiters

    def render(self, context: "ophinode.site.BuildContext"):
        rendered_attributes = self.render_attributes()
        if rendered_attributes:
            return "<{} {}>".format(self.tag, rendered_attributes)
        return "<{}>".format(self.tag)

