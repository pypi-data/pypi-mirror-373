import sys
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Mapping, Iterable
else:
    from collections.abc import Mapping, Iterable
import json
import os.path
import pathlib
import collections
import multiprocessing
from typing import Any, Union
from enum import Enum

from ophinode.exceptions.site import (
    RootPathUndefinedError,
    RootPathIsNotADirectoryError,
    NoCurrentPageError,
)
from ophinode.nodes.base import Page, Layout, Preparable, Expandable
from ophinode.nodes.html import TextNode, HTML5Layout
from ophinode.rendering.render_node import RenderNode

class _StackDelimiter:
    pass

class BuildPhase(Enum):
    INIT                        = 0
    PRE_PREPARE_SITE_BUILD      = 1
    PREPARE_SITE_BUILD          = 2
    POST_PREPARE_SITE_BUILD     = 3
    PRE_PREPARE_PAGE_BUILD      = 4
    PREPARE_PAGE_BUILD          = 5
    POST_PREPARE_PAGE_BUILD     = 6
    PRE_BUILD_PAGES             = 7
    BUILD_PAGES                 = 8
    POST_BUILD_PAGES            = 9
    PRE_PREPARE_PAGE_EXPANSION  = 10
    PREPARE_PAGE_EXPANSION      = 11
    POST_PREPARE_PAGE_EXPANSION = 12
    PRE_EXPAND_PAGES            = 13
    EXPAND_PAGES                = 14
    POST_EXPAND_PAGES           = 15
    PRE_RENDER_PAGES            = 16
    RENDER_PAGES                = 17
    POST_RENDER_PAGES           = 18
    PRE_EXPORT_PAGES            = 19
    EXPORT_PAGES                = 20
    POST_EXPORT_PAGES           = 21
    PRE_FINALIZE_PAGE_BUILD     = 22
    FINALIZE_PAGE_BUILD         = 23
    POST_FINALIZE_PAGE_BUILD    = 24
    PRE_FINALIZE_SITE_BUILD     = 25
    FINALIZE_SITE_BUILD         = 26
    POST_FINALIZE_SITE_BUILD    = 27

BUILD_CONTEXT_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "./ophinode_exported_files",
    "default_layout"                         : None,
    "page_default_file_name"                 : "index.html",
    "page_default_file_name_suffix"          : ".html",
    "auto_write_exported_page_build_files"   : False,
    "return_site_data_after_page_build"      : False,
    "return_page_data_after_page_build"      : False,
    "return_misc_data_after_page_build"      : True,
    "return_built_pages_after_page_build"    : False,
    "return_expanded_pages_after_page_build" : False,
    "return_rendered_pages_after_page_build" : False,
    "return_exported_files_after_page_build" : True,
}
BUILD_CONTEXT_CONFIG_KEYS = set(BUILD_CONTEXT_CONFIG_DEFAULT_VALUES)

class BuildContext:
    def __init__(
        self,
        name: str,
        pages: list,
        dependencies: dict,
        site_data: dict,
        page_data: dict,
        build_config: dict,
        processors: dict,
    ):
        self._build_phase = BuildPhase.INIT

        self._config = {}
        if build_config is not None:
            self.update_config(build_config)

        self._current_page_path = None
        self._current_page = None
        self._name = name
        self._pages_dict = {}
        self._pages = pages
        self._dependencies = dependencies

        for page_def in self._pages:
            self._pages_dict[page_def.path] = page_def

        self._site_data = site_data
        self._page_data = page_data
        self._misc_data = {}
        self._built_pages = {}
        self._expanded_pages = {}
        self._rendered_pages = {}
        self._exported_files = {}

        self._preprocessors_before_page_build_preparation_stage = []
        self._postprocessors_after_page_build_preparation_stage = []
        self._preprocessors_before_page_build_stage = []
        self._postprocessors_after_page_build_stage = []
        self._preprocessors_before_page_expansion_preparation_stage = []
        self._postprocessors_after_page_expansion_preparation_stage = []
        self._preprocessors_before_page_expansion_stage = []
        self._postprocessors_after_page_expansion_stage = []
        self._preprocessors_before_page_rendering_stage = []
        self._postprocessors_after_page_rendering_stage = []
        self._preprocessors_before_page_exportation_stage = []
        self._postprocessors_after_page_exportation_stage = []
        self._preprocessors_before_page_build_finalization_stage = []
        self._postprocessors_after_page_build_finalization_stage = []

        if "pre_prepare_page_build" in processors:
            l = self._preprocessors_before_page_build_preparation_stage
            for proc in processors["pre_prepare_page_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_prepare_page_build" in processors:
            l = self._postprocessors_after_page_build_preparation_stage
            for proc in processors["post_prepare_page_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_build_pages" in processors:
            l = self._preprocessors_before_page_build_stage
            for proc in processors["pre_build_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_build_pages" in processors:
            l = self._postprocessors_after_page_build_stage
            for proc in processors["post_build_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_prepare_page_expansion" in processors:
            l = self._preprocessors_before_page_expansion_preparation_stage
            for proc in processors["pre_prepare_page_expansion"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_prepare_page_expansion" in processors:
            l = self._postprocessors_after_page_expansion_preparation_stage
            for proc in processors["post_prepare_page_expansion"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_expand_pages" in processors:
            l = self._preprocessors_before_page_expansion_stage
            for proc in processors["pre_expand_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_expand_pages" in processors:
            l = self._postprocessors_after_page_expansion_stage
            for proc in processors["post_expand_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_render_pages" in processors:
            l = self._preprocessors_before_page_rendering_stage
            for proc in processors["pre_render_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_render_pages" in processors:
            l = self._postprocessors_after_page_rendering_stage
            for proc in processors["post_render_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_export_pages" in processors:
            l = self._preprocessors_before_page_exportation_stage
            for proc in processors["pre_export_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_export_pages" in processors:
            l = self._postprocessors_after_page_exportation_stage
            for proc in processors["post_export_pages"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_finalize_page_build" in processors:
            l = self._preprocessors_before_page_build_finalization_stage
            for proc in processors["pre_finalize_page_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_finalize_page_build" in processors:
            l = self._postprocessors_after_page_build_finalization_stage
            for proc in processors["post_finalize_page_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

    def _run_preprocessors_for_prepare_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_PREPARE_PAGE_BUILD)
        for processor in self._preprocessors_before_page_build_preparation_stage:
            processor(self)
        return self

    def _prepare_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PREPARE_PAGE_BUILD)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            self._set_current_page(path, page)
            page.prepare_page(self)
            self._unset_current_page()
        return self

    def _run_postprocessors_for_prepare_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_PREPARE_PAGE_BUILD)
        for processor in self._postprocessors_after_page_build_preparation_stage:
            processor(self)
        return self

    def _run_preprocessors_for_build_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_BUILD_PAGES)
        for processor in self._preprocessors_before_page_build_stage:
            processor(self)
        return self

    def _build_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.BUILD_PAGES)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            layout = self._resolve_layout(path, page)
            self._set_current_page(path, page)
            self._built_pages[path] = layout.build(page, self)
            self._unset_current_page()
        return self

    def _resolve_layout(self, path: str, page: Page) -> Layout:
        if not isinstance(page, Page):
            raise TypeError("page must be a Page, not {}".format(page.__class__.__name__))

        layout = page.layout
        l_src = "layout property of page"
        if not layout:
            layout = self.get_config_value("default_layout")
            l_src = "default_layout config of renderer"
        if not layout:
            layout = HTML5Layout()
            l_src = "fallback layout (HTML5Layout)"

        if not isinstance(layout, Layout) and callable(layout):
            layout = layout(self)

        if not isinstance(layout, Layout):
            raise ValueError(
                "resolved layout (from {}) is not a Layout instance".format(
                    l_src
                )
            )

        return layout

    def _run_postprocessors_for_build_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_BUILD_PAGES)
        for processor in self._postprocessors_after_page_build_stage:
            processor(self)
        return self

    def _run_preprocessors_for_prepare_page_expansion(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_PREPARE_PAGE_EXPANSION)
        for processor in self._preprocessors_before_page_expansion_preparation_stage:
            processor(self)
        return self

    def _prepare_page_expansion(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PREPARE_PAGE_EXPANSION)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            node = self.get_built_page(path)
            if not isinstance(node, Preparable):
                continue
            self._set_current_page(path, page)
            node.prepare(self)
            self._unset_current_page()
        return self

    def _run_postprocessors_for_prepare_page_expansion(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_PREPARE_PAGE_EXPANSION)
        for processor in self._postprocessors_after_page_expansion_preparation_stage:
            processor(self)
        return self

    def _run_preprocessors_for_expand_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_EXPAND_PAGES)
        for processor in self._preprocessors_before_page_expansion_stage:
            processor(self)
        return self

    def _expand_pages(self):
        self._set_build_phase(BuildPhase.EXPAND_PAGES)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            self._set_current_page(path, page)
            self._expanded_pages[path] = self._expand_page(
                self.get_built_page(path)
            )
            self._unset_current_page()

    def _expand_page(self, page_built: Iterable) -> RenderNode:
        root_node = RenderNode(None)
        curr = root_node

        stack = collections.deque()
        for node in reversed(page_built):
            stack.append(node)

        while stack:
            node = stack.pop()
            if isinstance(node, _StackDelimiter):
                curr = curr._parent
            elif isinstance(node, str):
                render_node = RenderNode(TextNode(node))
                render_node._parent = curr
                curr._children.append(render_node)
            elif callable(node):
                r = node(self)
                stack.append(r)
            elif isinstance(node, Iterable):
                for n in reversed(node):
                    stack.append(n)
            elif isinstance(node, Expandable):
                r = node.expand(self)
                stack.append(_StackDelimiter())
                next_render_node = RenderNode(node)
                next_render_node._parent = curr
                curr._children.append(next_render_node)
                curr = next_render_node
                stack.append(r)
            else:
                next_render_node = RenderNode(node)
                next_render_node._parent = curr
                curr._children.append(next_render_node)

        return root_node

    def _run_postprocessors_for_expand_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_EXPAND_PAGES)
        for processor in self._postprocessors_after_page_expansion_stage:
            processor(self)
        return self

    def _run_preprocessors_for_render_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_RENDER_PAGES)
        for processor in self._preprocessors_before_page_rendering_stage:
            processor(self)
        return self

    def _render_pages(self):
        self._set_build_phase(BuildPhase.RENDER_PAGES)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            self._set_current_page(path, page)
            self._rendered_pages[path] = self._render_page(path, page)
            self._unset_current_page()

    def _render_page(self, path: str, page: Any):
        root_node = self.get_expanded_page(path)
        render_result = root_node.render(self)
        return render_result

    def _run_postprocessors_for_render_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_RENDER_PAGES)
        for processor in self._postprocessors_after_page_rendering_stage:
            processor(self)
        return self

    def _run_preprocessors_for_export_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_EXPORT_PAGES)
        for processor in self._preprocessors_before_page_exportation_stage:
            processor(self)
        return self

    def _export_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.EXPORT_PAGES)
        for page_def in self._pages:
            path, page = page_def.path, page_def.page
            self._set_current_page(path, page)
            page.export_page(self)
            self._unset_current_page()
        return self

    def _run_postprocessors_for_export_pages(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_EXPORT_PAGES)
        for processor in self._postprocessors_after_page_exportation_stage:
            processor(self)
        return self

    def _run_preprocessors_for_finalize_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.PRE_FINALIZE_PAGE_BUILD)
        for processor in self._preprocessors_before_page_build_finalization_stage:
            processor(self)
        return self

    def _finalize_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.FINALIZE_PAGE_BUILD)
        if self.get_config_value("auto_write_exported_page_build_files"):
            self._write_exported_files()

    def _write_exported_files(self):
        export_root_path_value = self.get_config_value("export_root_path")
        if not export_root_path_value:
            raise RootPathUndefinedError(
                "failed to write exported files because export_root_path is "
                "empty"
            )

        export_root_path = pathlib.Path(export_root_path_value)
        export_root_path.mkdir(parents=True, exist_ok=True)

        for path, file_content in self._exported_files.items():
            target_path = export_root_path / path.lstrip('/')
            target_directory = target_path.parent
            target_directory.mkdir(parents=True, exist_ok=True)
            if isinstance(file_content, (bytes, bytearray)):
                with target_path.open(mode="wb") as f:
                    f.write(file_content)
            elif isinstance(file_content, str):
                with target_path.open(mode="w", encoding="utf-8") as f:
                    f.write(file_content)
            else:
                with target_path.open(mode="w", encoding="utf-8") as f:
                    json.dump(file_content, f)

    def _run_postprocessors_for_finalize_page_build(self) -> "BuildContext":
        self._set_build_phase(BuildPhase.POST_FINALIZE_PAGE_BUILD)
        for processor in self._postprocessors_after_page_build_finalization_stage:
            processor(self)
        return self

    def _set_build_phase(self, phase: BuildPhase):
        if not isinstance(phase, BuildPhase):
            raise TypeError("phase must be a BuildPhase, not {}".format(phase.__class__.__name__))
        self._build_phase = phase

    def _set_current_page(self, path, page):
        self._current_page_path = path
        self._current_page = page

    def _unset_current_page(self):
        self._current_page_path = None
        self._current_page = None

    @property
    def name(self):
        return self._name

    @property
    def site_data(self):
        return self._site_data

    @property
    def page_data(self):
        current_page_path = self._current_page_path
        if current_page_path is None:
            raise NoCurrentPageError("no page is currently being built in this context")
        return self._page_data[current_page_path]

    @property
    def misc_data(self):
        return self._misc_data

    @property
    def build_phase(self):
        return self._build_phase

    @property
    def current_page(self):
        return self._current_page

    @property
    def current_page_path(self):
        return self._current_page_path

    def build_page_group(self) -> dict:
        self._run_preprocessors_for_prepare_page_build()
        self._prepare_page_build()
        self._run_postprocessors_for_prepare_page_build()

        self._run_preprocessors_for_build_pages()
        self._build_pages()
        self._run_postprocessors_for_build_pages()

        self._run_preprocessors_for_prepare_page_expansion()
        self._prepare_page_expansion()
        self._run_postprocessors_for_prepare_page_expansion()

        self._run_preprocessors_for_expand_pages()
        self._expand_pages()
        self._run_postprocessors_for_expand_pages()

        self._run_preprocessors_for_render_pages()
        self._render_pages()
        self._run_postprocessors_for_render_pages()

        self._run_preprocessors_for_export_pages()
        self._export_pages()
        self._run_postprocessors_for_export_pages()

        self._run_preprocessors_for_finalize_page_build()
        self._finalize_page_build()
        self._run_postprocessors_for_finalize_page_build()

        result = {"name": self.name}
        if self.get_config_value("return_site_data_after_page_build"):
            result["site_data"] = self._site_data
        if self.get_config_value("return_page_data_after_page_build"):
            result["page_data"] = self._page_data
        if self.get_config_value("return_misc_data_after_page_build"):
            result["misc_data"] = self._misc_data
        if self.get_config_value("return_built_pages_after_page_build"):
            result["built_pages"] = self._built_pages
        if self.get_config_value("return_expanded_pages_after_page_build"):
            result["expanded_pages"] = self._expanded_pages
        if self.get_config_value("return_rendered_pages_after_page_build"):
            result["rendered_pages"] = self._rendered_pages
        if self.get_config_value("return_exported_files_after_page_build"):
            result["exported_files"] = self._exported_files

        return result

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError("key must be a str")
        if key not in BUILD_CONTEXT_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(k))
        if key in self._config:
            return self._config[key]
        return BUILD_CONTEXT_CONFIG_DEFAULT_VALUES[key]

    def update_config(
        self,
        config_values: Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(config_values, Mapping):
            raise TypeError("config_values must be a mapping")
        for k, v in config_values.items():
            if k not in BUILD_CONTEXT_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def get_page_data(self, page_path: Union[str, None] = None):
        if page_path is None:
            if self._current_page_path is None:
                raise NoCurrentPageError(
                    "no page is currently being built in this context"
                )
            return self._page_data[self._current_page_path]
        return self._page_data[page_path]

    def get_page(self, page_path: Union[str, None] = None):
        if page_path is None:
            if self._current_page is None:
                raise NoCurrentPageError(
                    "no page is currently being built in this context"
                )
            return self._current_page
        return self._pages_dict[page_path]

    def get_pages(self):
        return self._pages.copy()

    def get_page_paths(self):
        return [x.path for x in self._pages]

    def has_page(self, page_path: str):
        return page_path in self._pages_dict

    def get_built_page(self, page_path: str):
        return self._built_pages[page_path]

    def get_built_pages(self):
        return self._built_pages.copy()

    def get_built_page_paths(self):
        return list(self._built_pages.keys())

    def is_built_page_path(self, page_path: str):
        return page_path in self._built_pages

    def get_expanded_page(self, page_path: str):
        return self._expanded_pages[page_path]

    def get_expanded_pages(self):
        return self._expanded_pages.copy()

    def get_expanded_page_paths(self):
        return list(self._expanded_pages.keys())

    def is_expanded_page_path(self, page_path: str):
        return page_path in self._expanded_pages

    def get_rendered_page(self, page_path: str):
        return self._rendered_pages[page_path]

    def get_rendered_pages(self):
        return self._rendered_pages.copy()

    def get_rendered_page_paths(self):
        return list(self._rendered_pages.keys())

    def is_rendered_page_path(self, page_path: str):
        return page_path in self._rendered_pages

    def export_file(
        self,
        export_path: str,
        data: Union[str, bytes, bytearray, memoryview]
    ):
        normalized_export_path = os.path.normpath("/" + export_path)
        if normalized_export_path in self._exported_files:
            raise ExportPathCollisionError(
                "attempted to export a page to '{}', but another file is "
                "already exported to that path".format(normalized_export_path)
            )
        self._exported_files[normalized_export_path] = data

    def get_exported_file(self, export_path: str):
        return self._exported_files[export_path]

    def get_exported_files(self):
        return self._exported_files.copy()

    def get_exported_file_paths(self):
        return list(self._exported_files.keys())

    def is_exported_file_path(self, export_path: str):
        return export_path in self._exported_files

ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "./ophinode_exported_files",
    "default_layout"                         : None,
    "build_strategy"                         : "sync",
    "parallel_build_workers"                 : os.cpu_count(),
    "parallel_build_chunksize"               : 1,
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
}
ROOT_BUILD_CONTEXT_CONFIG_KEYS = set(ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES)

# This wrapper is used to support multiple invocations of
# BuildContext.build_page_group() when utilizing multiprocessing.Pool
def build_page_group(subcontext: BuildContext):
    return subcontext.build_page_group()

class RootBuildContext:
    def __init__(
        self,
        page_groups: dict,
        build_config: dict,
        processors: dict,
    ):
        self._build_phase = BuildPhase.INIT

        self._config = {}
        if build_config is not None:
            self.update_config(build_config)

        self._page_groups = page_groups
        self._subcontexts = []
        self._page_build_results = {}
        self._site_data = {}
        self._page_data = {}
        self._misc_data = {}
        self._built_pages = {}
        self._expanded_pages = {}
        self._rendered_pages = {}
        self._exported_files = {}

        self._preprocessors_before_site_build_preparation_stage = []
        self._postprocessors_after_site_build_preparation_stage = []
        self._preprocessors_before_site_build_finalization_stage = []
        self._postprocessors_after_site_build_finalization_stage = []

        if "pre_prepare_site_build" in processors:
            l = self._preprocessors_before_site_build_preparation_stage
            for proc in processors["pre_prepare_site_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_prepare_site_build" in processors:
            l = self._postprocessors_after_site_build_preparation_stage
            for proc in processors["post_prepare_site_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "pre_finalize_site_build" in processors:
            l = self._preprocessors_before_site_build_finalization_stage
            for proc in processors["pre_finalize_site_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

        if "post_finalize_site_build" in processors:
            l = self._postprocessors_after_site_build_finalization_stage
            for proc in processors["post_finalize_site_build"]:
                if not callable(proc):
                    raise ValueError(
                        "pre- and post-processors must be callable"
                    )
                l.append(proc)

    def _run_preprocessors_for_prepare_site_build(self) -> "RootBuildContext":
        self._set_build_phase(BuildPhase.PRE_PREPARE_SITE_BUILD)
        for processor in self._preprocessors_before_site_build_preparation_stage:
            processor(self)
        return self

    def _prepare_site_build(self) -> "RootBuildContext":
        self._set_build_phase(BuildPhase.PREPARE_SITE_BUILD)
        for page_group in self._page_groups.values():
            self.create_subcontext(page_group)
        return self

    def _run_postprocessors_for_prepare_site_build(self) -> "RootBuildContext":
        self._set_build_phase(BuildPhase.POST_PREPARE_SITE_BUILD)
        for processor in self._postprocessors_after_site_build_preparation_stage:
            processor(self)
        return self

    def _run_preprocessors_for_finalize_site_build(self) -> "RootBuildContext":
        self._set_build_phase(BuildPhase.PRE_FINALIZE_SITE_BUILD)
        for processor in self._preprocessors_before_site_build_finalization_stage:
            processor(self)
        return self

    def _finalize_site_build(self):
        self._set_build_phase(BuildPhase.FINALIZE_SITE_BUILD)
        if self.get_config_value("auto_write_exported_site_build_files"):
            self._write_exported_files()

    def _write_exported_files(self):
        export_root_path_value = self.get_config_value("export_root_path")
        if not export_root_path_value:
            raise RootPathUndefinedError(
                "failed to write exported files because export_root_path is "
                "empty"
            )

        export_root_path = pathlib.Path(export_root_path_value)
        export_root_path.mkdir(parents=True, exist_ok=True)

        for path, file_content in self._exported_files.items():
            target_path = export_root_path / path.lstrip('/')
            target_directory = target_path.parent
            target_directory.mkdir(parents=True, exist_ok=True)
            if isinstance(file_content, (bytes, bytearray)):
                with target_path.open(mode="wb") as f:
                    f.write(file_content)
            elif isinstance(file_content, str):
                with target_path.open(mode="w", encoding="utf-8") as f:
                    f.write(file_content)
            else:
                with target_path.open(mode="w", encoding="utf-8") as f:
                    json.dump(file_content, f)

    def _run_postprocessors_for_finalize_site_build(self) -> "RootBuildContext":
        self._set_build_phase(BuildPhase.POST_FINALIZE_SITE_BUILD)
        for processor in self._postprocessors_after_site_build_finalization_stage:
            processor(self)
        return self

    def _merge_data_from_build_results(self, build_result: dict):
        if "site_data" in build_result:
            self._site_data.update(build_result["site_data"])
        if "page_data" in build_result:
            self._page_data.update(build_result["page_data"])
        if "misc_data" in build_result:
            self._misc_data.update(build_result["misc_data"])
        if "built_pages" in build_result:
            self._built_pages.update(build_result["built_pages"])
        if "expanded_pages" in build_result:
            self._expanded_pages.update(build_result["expanded_pages"])
        if "rendered_pages" in build_result:
            self._rendered_pages.update(build_result["rendered_pages"])
        if "exported_files" in build_result:
            self._exported_files.update(build_result["exported_files"])

    def build_site(self) -> "RootBuildContext":
        self._run_preprocessors_for_prepare_site_build()
        self._prepare_site_build()
        self._run_postprocessors_for_prepare_site_build()

        build_strategy = self.get_config_value("build_strategy")
        if build_strategy == "sync":
            for subcontext in self._subcontexts:
                result = build_page_group(subcontext)
                self._page_build_results[result["name"]] = result
                if self.get_config_value(
                    "gather_and_merge_page_build_results"
                ):
                    self._merge_data_from_build_results(result)
        elif build_strategy == "parallel":
            pool = multiprocessing.Pool(
                processes=self.get_config_value("parallel_build_workers")
            )
            for result in pool.imap_unordered(
                build_page_group,
                self._subcontexts,
                self.get_config_value("parallel_build_chunksize")
            ):
                self._page_build_results[result["name"]] = result
                if self.get_config_value(
                    "gather_and_merge_page_build_results"
                ):
                    self._merge_data_from_build_results(result)
            pool.close()
            pool.join()
        else:
            raise ValueError("unknown build strategy: {}".format(build_strategy))

        self._run_preprocessors_for_finalize_site_build()
        self._finalize_site_build()
        self._run_postprocessors_for_finalize_site_build()

        return self

    def create_subcontext(self, page_group: "PageGroup"):
        build_config = {}
        for k in BUILD_CONTEXT_CONFIG_KEYS:
            if k in self._config:
                build_config[k] = self._config[k]

        subcontext = page_group.create_build_context(
            build_config,
            self._site_data,
            self._page_data,
        )
        self._subcontexts.append(subcontext)

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError("key must be a str")
        if key not in ROOT_BUILD_CONTEXT_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(k))
        if key in self._config:
            return self._config[key]
        return ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES[key]

    def update_config(
        self,
        config_values: Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(config_values, Mapping):
            raise TypeError("config_values must be a mapping")
        for k, v in config_values.items():
            if k not in ROOT_BUILD_CONTEXT_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def get_site(self):
        return self._site

    def get_build_phase(self) -> BuildPhase:
        return self._build_phase

    def _set_build_phase(self, phase: BuildPhase):
        if not isinstance(phase, BuildPhase):
            raise TypeError("phase must be a BuildPhase, not {}".format(phase.__class__.__name__))
        self._build_phase = phase

    def get_page_data(self, key: str, page_path: Union[str, None] = None):
        """Get a local data whose name is 'key' from Page 'page_path'.
        """
        page_data = self._page_data[page_path]
        data = page_data[key]
        return data

    def get_page(self, page_path: str):
        return self._site.get_page(page_path)

    def get_pages(self):
        return self._site.get_pages()

    def get_page_paths(self):
        return self._site.get_page_paths()

    def has_page(self, page_path: str):
        return self._site.has_page(page_path)

    def set_built_page(self, page_path: str, built_page: Any):
        self._built_pages[page_path] = built_page

    def get_built_page(self, page_path: str):
        return self._built_pages[page_path]

    def get_built_pages(self):
        return self._built_pages.copy()

    def get_built_page_paths(self):
        return list(self._built_pages.keys())

    def is_built_page_path(self, page_path: str):
        return page_path in self._built_pages

    def set_expanded_page(self, page_path: str, expanded_page: RenderNode):
        self._expanded_pages[page_path] = expanded_page

    def get_expanded_page(self, page_path: str):
        return self._expanded_pages[page_path]

    def get_expanded_pages(self):
        return self._expanded_pages.copy()

    def get_expanded_page_paths(self):
        return list(self._expanded_pages.keys())

    def is_expanded_page_path(self, page_path: str):
        return page_path in self._expanded_pages

    def set_rendered_page(self, page_path: str, rendered_page: str):
        self._rendered_pages[page_path] = rendered_page

    def get_rendered_page(self, page_path: str):
        return self._rendered_pages[page_path]

    def get_rendered_pages(self):
        return self._rendered_pages.copy()

    def get_rendered_page_paths(self):
        return list(self._rendered_pages.keys())

    def is_rendered_page_path(self, page_path: str):
        return page_path in self._rendered_pages

    def export_file(
        self,
        export_path: str,
        data: Union[str, bytes, bytearray, memoryview]
    ):
        normalized_export_path = os.path.normpath("/" + export_path)
        if normalized_export_path in self._exported_files:
            raise ExportPathCollisionError(
                "attempted to export a page to '{}', but another file is "
                "already exported to that path".format(normalized_export_path)
            )
        self._exported_files[normalized_export_path] = data

    def get_exported_file(self, export_path: str):
        return self._exported_files[export_path]

    def get_exported_files(self):
        return self._exported_files.copy()

    def get_exported_file_paths(self):
        return list(self._exported_files.keys())

    def is_exported_file_path(self, export_path: str):
        return export_path in self._exported_files

    def get_page_build_result(self, page_group_name: str):
        return self._page_build_results[page_group_name]

