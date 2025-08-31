import argparse

EXAMPLE1 = """# Example program: render a page without defining a site.
#
# Running this program prints a HTML document to standard output.
#
from ophinode import *

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

print(render_page(MainPage(), HTML5Layout()))
"""

EXAMPLE2 = """# Example program: create a page in a directory.
#
# Running this program creates "index.html" in "./out" directory.
#
from ophinode import *

class DefaultLayout(Layout):
    def build(self, page, context):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    Meta(charset="utf-8"),
                    Title(page.title()),
                    page.head(),
                ),
                Body(
                    page.body(),
                ),
            )
        ]

class MainPage(Page):
    @property
    def layout(self):
        return DefaultLayout()

    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!"),
        )

    def head(self):
        return []

    def title(self):
        return "Main Page"

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

    site.build_site()
"""

EXAMPLE3 = """# Example program: parallel build.
#
# Running this program creates "page1.html" to "page1000.html"
# in "./out" directory.
#
import os
from ophinode import *

class DefaultLayout(Layout):
    def build(self, page, context):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    Meta(charset="utf-8"),
                    Title(page.title()),
                    page.head(),
                ),
                Body(
                    page.body(),
                ),
            )
        ]

class MainPage(Page):
    def __init__(self, idx):
        self.idx = idx

    @property
    def layout(self):
        return DefaultLayout()

    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!"),
            P(f"This is page{self.idx}.html."),
        )

    def head(self):
        return []

    def title(self):
        return "Main Page"

if __name__ == "__main__":
    cpu_count = os.cpu_count()
    site = Site({
        "export_root_path"                       : "./out",
        "default_layout"                         : DefaultLayout(),
        "build_strategy"                         : "parallel",
        "parallel_build_workers"                 : cpu_count,
        "parallel_build_chunksize"               : 1,
        "preserve_site_definition_across_builds" : False,
        "page_default_file_name"                 : "index.html",
        "page_default_file_name_suffix"          : ".html",
        "auto_write_exported_page_build_files"   : True,
        "auto_write_exported_site_build_files"   : False,
        "return_site_data_after_page_build"      : False,
        "return_page_data_after_page_build"      : False,
        "return_misc_data_after_page_build"      : True,
        "return_built_pages_after_page_build"    : False,
        "return_expanded_pages_after_page_build" : False,
        "return_rendered_pages_after_page_build" : False,
        "return_exported_files_after_page_build" : False,
        "gather_and_merge_page_build_results"    : False,
    }, [
    ])

    for i in range(1, 1001):
        page_group = i % cpu_count
        site.add_page(
            f"/page{i}.html",
            MainPage(i),
            page_group=f"{page_group}"
        )

    site.build_site()
"""

def main():
    parser = argparse.ArgumentParser(prog="ophinode")
    parser.add_argument("subcommand", choices=["examples"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.subcommand == "examples":
        if not args.arguments:
            print(
                "available examples: render_page, basic_site, parallel_build"
            )
        elif args.arguments[0] == "render_page":
            print(EXAMPLE1)
        elif args.arguments[0] == "basic_site":
            print(EXAMPLE2)
        elif args.arguments[0] == "parallel_build":
            print(EXAMPLE3)
        else:
            print(
                "available examples: render_page, basic_site, parallel_build"
            )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
