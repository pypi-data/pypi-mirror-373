import collections
from typing import Union

from ophinode.nodes.base import *

class RenderNode:
    def __init__(self, value: Union[OpenRenderable, ClosedRenderable, None]):
        self._value = value
        self._children = []
        self._parent = None

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    def render(self, context: "ophinode.site.BuildContext"):
        result = []
        depth = 0
        stk = collections.deque()
        stk.append((self, False))
        no_auto_newline_count = 0
        no_auto_indent_count = 0
        total_text_content_length = 0
        text_content_length_stk = collections.deque()
        while stk:
            render_node, revisited = stk.pop()
            v, c = render_node._value, render_node._children
            if isinstance(v, OpenRenderable):
                if revisited:
                    depth -= 1
                    text_content = v.render_end(context)
                    if not (
                        text_content_length_stk
                        and text_content_length_stk[-1]
                            == total_text_content_length
                    ):
                        if (
                            text_content
                            and total_text_content_length
                            and no_auto_newline_count == 0
                        ):
                            text_content = "\n" + text_content
                    if no_auto_indent_count == 0 and text_content:
                        text_content = ("\n"+"  "*depth).join(
                            text_content.split("\n")
                        )
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    text_content_length_stk.pop()
                    if not v.auto_newline:
                        no_auto_newline_count -= 1
                    if not v.auto_indent:
                        no_auto_indent_count -= 1
                else:
                    text_content = v.render_start(context)
                    if text_content and (
                        total_text_content_length
                        and no_auto_newline_count == 0
                    ):
                        text_content = "\n" + text_content
                    if no_auto_indent_count == 0 and text_content:
                        text_content = ("\n"+"  "*depth).join(
                            text_content.split("\n")
                        )
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    text_content_length_stk.append(total_text_content_length)
                    if not v.auto_newline:
                        no_auto_newline_count += 1
                    if not v.auto_indent:
                        no_auto_indent_count += 1
                    stk.append((render_node, True))
                    depth += 1
            elif isinstance(v, ClosedRenderable):
                if revisited:
                    depth -= 1
                else:
                    text_content = v.render(context)
                    if text_content and (
                        total_text_content_length
                        and no_auto_newline_count == 0
                    ):
                        text_content = "\n" + text_content
                    if no_auto_indent_count == 0 and text_content:
                        text_content = ("\n"+"  "*depth).join(
                            text_content.split("\n")
                        )
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    stk.append((render_node, True))
                    depth += 1
            if not revisited and c:
                for i in reversed(c):
                    stk.append((i, False))
        result.append("\n")
        return "".join(result)

