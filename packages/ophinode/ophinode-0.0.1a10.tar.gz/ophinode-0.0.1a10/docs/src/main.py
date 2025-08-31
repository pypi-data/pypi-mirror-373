import sys
import os.path
import shutil

from ophinode import *
from misc import get_href

class DefaultLayout(Layout):
    def build(self, page, context):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    Meta(charset="utf-8"),
                    Meta(name="viewport", content="width=device-width, initial-scale=1"),
                    Title(page.title()),
                    Link(rel="stylesheet", href=get_href("/static/css/main.css")),
                    page.head(),
                ),
                Body(
                    page.body(),
                ),
            )
        ]

class MainContent(Expandable):
    def __init__(self, *args):
        self.children = args

    def expand(self, context):
        return Div(
            self.children,
            cls="main-container",
        )

class MainPage(Page):
    @property
    def layout(self):
        return DefaultLayout()

    def body(self):
        return MainContent(
            H1("ophinode"),
            P(
                Code("ophinode"),
                " is a static site generator written in Python that focuses "
                "on being a simple and flexible library for creating "
                "websites.",
            ),
            P(
                "You can generate a HTML document using predefined objects, "
                "like the following:",
            ),
            Pre(Code(
"""from ophinode import *

class MainPage(HTML5Page):
    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!"),
        )

    def head(self):
        return [
            Meta(charset="utf-8"),
            Title("Main Page"),
        ]

print(render_page(MainPage(), HTML5Layout()))""",
            )),
            P(
                "Or you can define a ", Code("Site"), " object which "
                "automatically writes build results to the file system:"
            ),
            Pre(Code(
"""from ophinode import *

class MainPage(HTML5Page):
    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!"),
        )

    def head(self):
        return [
            Meta(charset="utf-8"),
            Title("Main Page"),
        ]


if __name__ == "__main__":
    site = Site({
        "export_root_path"                       : "./out",
        "default_layout"                         : DefaultLayout(),
        "build_strategy"                         : "sync",
        "preserve_site_definition_across_builds" : False,
        "page_default_file_name"                 : "index.html",
        "page_default_file_name_suffix"          : ".html",
        "auto_write_exported_page_build_files"   : False,
        "auto_write_exported_site_build_files"   : True,
        "return_site_data_after_page_build"      : False,
        "return_page_data_after_page_build"      : False,
        "return_misc_data_after_page_build"      : True,
        "return_built_pages_after_page_build"    : False,
        "return_expanded_pages_after_page_build" : False,
        "return_rendered_pages_after_page_build" : False,
        "return_exported_files_after_page_build" : True,
        "gather_and_merge_page_build_results"    : True,
    }, [
        ("/", MainPage()),
    ])

    site.build_site()""",
            )),
        )

    def head(self):
        return []

    def title(self):
        return "ophinode"

if __name__ == "__main__":
    site = Site({
        "export_root_path"                       : "./docs",
        "default_layout"                         : DefaultLayout(),
        "build_strategy"                         : "sync",
        "preserve_site_definition_across_builds" : False,
        "page_default_file_name"                 : "index.html",
        "page_default_file_name_suffix"          : ".html",
        "auto_write_exported_page_build_files"   : False,
        "auto_write_exported_site_build_files"   : True,
        "return_site_data_after_page_build"      : False,
        "return_page_data_after_page_build"      : False,
        "return_misc_data_after_page_build"      : True,
        "return_built_pages_after_page_build"    : False,
        "return_expanded_pages_after_page_build" : False,
        "return_rendered_pages_after_page_build" : False,
        "return_exported_files_after_page_build" : True,
        "gather_and_merge_page_build_results"    : True,
    }, [
        ("/", MainPage()),
    ])

    site.build_site()

