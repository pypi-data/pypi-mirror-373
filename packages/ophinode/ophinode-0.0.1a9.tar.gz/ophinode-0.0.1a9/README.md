# ophinode
`ophinode` is a static site generator written in Python that focuses on being
a simple and flexible library for creating websites.

This project is currently in the initial development stage, and the APIs may
change at any time.

## Example programs

You can also get these example programs by running
`python -m ophinode examples`.

```python
# Example program: render a page without defining a site.
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

```

```python
# Example program: create a page in a directory.
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

```

```python
# Example program: parallel build.
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

```
