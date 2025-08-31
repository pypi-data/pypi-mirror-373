from typing import Any
from abc import ABC, abstractmethod

class ClosedRenderable(ABC):
    @abstractmethod
    def render(self, context: "ophinode.site.BuildContext"):
        pass

class OpenRenderable(ABC):
    @abstractmethod
    def render_start(self, context: "ophinode.site.BuildContext"):
        pass

    @abstractmethod
    def render_end(self, context: "ophinode.site.BuildContext"):
        pass

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

class Expandable(ABC):
    @abstractmethod
    def expand(self, context: "ophinode.site.BuildContext"):
        pass

class Preparable(ABC):
    @abstractmethod
    def prepare(self, context: "ophinode.site.BuildContext"):
        pass

class Page:
    @property
    def layout(self):
        return None

    @property
    def default_file_name(self):
        return None

    @property
    def default_file_name_suffix(self):
        return None

    def prepare_site(self, context: "ophinode.site.BuildContext"):
        pass

    def prepare_page(self, context: "ophinode.site.BuildContext"):
        pass

    def export_page(self, context: "ophinode.site.BuildContext"):
        export_path = context.current_page_path

        page_default_file_name = self.default_file_name
        if page_default_file_name is None:
            page_default_file_name = context.get_config_value(
                "page_default_file_name"
            )
        if export_path.endswith("/") and page_default_file_name is not None:
            export_path += page_default_file_name

        page_default_file_name_suffix = self.default_file_name_suffix
        if page_default_file_name_suffix is None:
            page_default_file_name_suffix = context.get_config_value(
                "page_default_file_name_suffix"
            )
        if (
            not export_path.endswith("/")
            and page_default_file_name_suffix is not None
            and not export_path.endswith(page_default_file_name_suffix)
        ):
            export_path += page_default_file_name_suffix

        render_result = context.get_rendered_page(context.current_page_path)
        context.export_file(export_path, render_result)

    def finalize_page(self, context: "ophinode.site.BuildContext"):
        pass

    def finalize_site(self, context: "ophinode.site.BuildContext"):
        pass

class Layout(ABC):
    @abstractmethod
    def build(self, page: Page, context: "ophinode.site.BuildContext"):
        pass

