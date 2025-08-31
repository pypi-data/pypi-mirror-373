from ..base import Page, Layout
from .core import HTML5Doctype
from .elements import Html, Head, Body

class HTML5Page(Page):
    @property
    def layout(self):
        return HTML5Layout()

    def html_attributes(self) -> dict:
        return {}

    def head(self):
        return []

    def body(self):
        return []

class HTML5Layout(Layout):
    def build(self, page: HTML5Page, context: "ophinode.site.BuildContext"):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    page.head()
                ),
                Body(
                    page.body()
                ),
                **page.html_attributes()
            )
        ]

