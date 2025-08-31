import os
import sys
import copy
from typing import Any, Union
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Iterable, Tuple, Callable, Mapping, Sequence
else:
    from collections.abc import Iterable, Callable, Mapping, Sequence
    Tuple = tuple

from ophinode.nodes.base import Page, Layout
from ophinode.nodes.html.core import HTML5Doctype
from ophinode.nodes.html.elements.fullname import (
    HtmlElement,
    HeadElement,
    BodyElement,
)
from .page_group import PageGroup
from .page_definition import PageDefinition
from .build_contexts import (
    RootBuildContext,
    BuildContext,
    BuildPhase,
    ROOT_BUILD_CONTEXT_CONFIG_KEYS,
)

SITE_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "./ophinode_exported_files",
    "default_layout"                         : None,
    "build_strategy"                         : "sync",
    "parallel_build_workers"                 : os.cpu_count(),
    "parallel_build_chunksize"               : 1,
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
}
SITE_CONFIG_KEYS = set(SITE_CONFIG_DEFAULT_VALUES)

class Site:
    def __init__(
        self,
        config: Union[Mapping, None] = None,
        pages: Union[
            Iterable[Mapping],
            Iterable[Tuple[str, Page]],
            Iterable[Tuple[str, Page, str]],
            Iterable[Tuple[str, Page, str, str]],
            None
        ] = None,
        processors: Union[
            Iterable[Tuple[str, Callable[[BuildContext], None]]],
            Iterable[
                Tuple[str, Callable[[BuildContext], None], Union[str, None]]
            ],
            None
        ] = None,
    ):
        self._config = {}
        if config is not None:
            self.update_config(config)

        self._pages_dict = {}
        self._pages = []
        self._page_groups = {}
        if pages is not None:
            if not isinstance(pages, Iterable):
                raise TypeError("pages must be an iterable")
            for page_spec in pages:
                if isinstance(
                    page_spec, (str, bytes, bytearray, memoryview)
                ):
                    raise TypeError(
                        "object of type {} cannot be given as a page "
                        "specification".format(page_spec.__class__.__name__)
                    )
                elif isinstance(page_spec, Mapping):
                    if "path" not in page_spec:
                        raise ValueError(
                            "page specification does not contain 'path'"
                        )
                    if "page" not in page_spec:
                        raise ValueError(
                            "page specification does not contain 'page'"
                        )
                    path = page_spec["path"]
                    page = page_spec["page"]
                    page_group = None
                    dependency_group = None
                    if "page_group" in page_spec:
                        page_group = page_spec["page_group"]
                    if "dependency_group" in page_spec:
                        dependency_group = page_spec["dependency_group"]
                elif isinstance(page_spec, Sequence):
                    if len(page_spec) == 2:
                        path, page = page_spec
                        page_group, dependency_group = None, None
                    elif len(page_spec) == 3:
                        path, page, page_group = page_spec
                        dependency_group = None
                    elif len(page_spec) == 4:
                        path, page, page_group, dependency_group = (
                            page_spec
                        )
                    else:
                        raise ValueError(
                            "page specification contains wrong number of "
                            "arguments (expected 2~4, but {} given)".format(
                                len(page_spec)
                            )
                        )
                else:
                    raise TypeError(
                        "object of type {} cannot be given as a page "
                        "specification".format(page_spec.__class__.__name__)
                    )
                self.add_page(path, page, page_group, dependency_group)

        self._preprocessors_before_site_build_preparation_stage = []
        self._postprocessors_after_site_build_preparation_stage = []
        self._preprocessors_before_site_build_finalization_stage = []
        self._postprocessors_after_site_build_finalization_stage = []
        if processors is not None:
            if not isinstance(processors, Iterable):
                raise TypeError("processors must be an iterable")
            for processor_spec in processors:
                if isinstance(
                    processor_spec, (str, bytes, bytearray, memoryview)
                ):
                    raise TypeError(
                        "object of type {} cannot be given as a processor "
                        "specification".format(
                            processor_spec.__class__.__name__
                        )
                    )
                elif isinstance(processor_spec, Mapping):
                    if "stage" not in processor_spec:
                        raise ValueError(
                            "processor specification does not contain 'stage'"
                        )
                    if "processor" not in processor_spec:
                        raise ValueError(
                            "processor specification does not contain "
                            "'processor'"
                        )
                    stage = processor_spec["stage"]
                    processor = processor_spec["processor"]
                    page_group = None
                    if "page_group" in processor_spec:
                        page_group = processor_spec["page_group"]
                elif isinstance(processor_spec, Sequence):
                    if len(processor_spec) == 2:
                        stage, processor = processor_spec
                        page_group = None
                    elif len(processor_spec) == 3:
                        stage, processor, page_group = processor_spec
                    else:
                        raise ValueError(
                            "processor specification contains wrong number of"
                            " arguments (expected 2~4, but {} given)".format(
                                len(processor_spec)
                            )
                        )
                else:
                    raise TypeError(
                        "object of type {} cannot be given as a processor "
                        "specification".format(
                            processor_spec.__class__.__name__
                        )
                    )
                self.add_processor(stage, processor, page_group)

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError(
                "key must be a str, not {}".format(key.__class__.__name__)
            )
        if key not in SITE_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(key))
        if key in self._config:
            return self._config[key]
        return SITE_CONFIG_DEFAULT_VALUES[key]

    def set_config_value(self, key: str, value: Any):
        if not isinstance(key, str):
            raise TypeError(
                "key must be a str, not {}".format(key.__class__.__name__)
            )
        if key not in SITE_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(key))
        self._config[key] = value

    def update_config(
        self,
        config_values: Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(config_values, Mapping):
            raise TypeError("config_values must be a mapping")
        for k, v in config_values.items():
            if k not in SITE_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def get_page_group(self, page_group: str):
        if not isinstance(page_group, str):
            raise TypeError(
                "page_group must be a str, not {}".format(
                    page_group.__class__.__name__
                )
            )
        return self._page_groups[page_group]

    def add_page(
        self,
        path: str,
        page: Page,
        page_group: Union[str, None] = None,
        dependency_group: Union[str, None] = None,
    ):
        if not isinstance(path, str):
            raise TypeError(
                "path to a page must be a str, not {}".format(
                    path.__class__.__name__
                )
            )
        if not isinstance(page, Page):
            raise TypeError(
                "page must be an instance of Page, not {}".format(
                    page.__class__.__name__
                )
            )
        if path in self._pages_dict:
            raise ValueError("duplicate page path: " + path)

        if page_group is None:
            page_group = "default"
        if dependency_group is None:
            dependency_group = path

        if page_group not in self._page_groups:
            self._page_groups[page_group] = PageGroup(page_group)
        page_group_instance = self._page_groups[page_group]

        page_definition = PageDefinition(
            path, page, page_group, dependency_group
        )
        page_group_instance.add_page(page_definition)

        self._pages_dict[path] = page_definition
        self._pages.append(page_definition)

        return page_definition

    def get_page(self, path: str):
        if not isinstance(path, str):
            raise TypeError("path to a page must be a str")
        return self._pages_dict[path]

    def get_pages(self):
        return self._pages.copy()

    def get_page_paths(self):
        return [x.path for x in self._pages]

    def has_page(self, path: str):
        if not isinstance(path, str):
            raise TypeError("path to a page must be a str")
        return path in self._pages_dict

    def add_processor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None],
        page_group: Union[str, None] = None,
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")
        if page_group is not None and not isinstance(page_group, str):
            raise ValueError("page_group must be a str or None")

        if stage in (
            "pre_prepare_site_build",
            "post_prepare_site_build",
            "pre_finalize_site_build",
            "post_finalize_site_build",
        ):
            if page_group is not None:
                raise ValueError(
                    "preprocessors and postprocessors for site build can "
                    "only have 'page_group' set to None"
                )
            if stage == "pre_prepare_site_build":
                self._preprocessors_before_site_build_preparation_stage.append(processor)
            elif stage == "post_prepare_site_build":
                self._postprocessors_after_site_build_preparation_stage.append(processor)
            elif stage == "pre_finalize_site_build":
                self._preprocessors_before_site_build_finalization_stage.append(processor)
            elif stage == "post_finalize_site_build":
                self._postprocessors_after_site_build_finalization_stage.append(processor)
            else:
                raise ValueError("invalid processor stage: '{}'".format(stage))
        elif stage in (
            "pre_prepare_page_build",
            "post_prepare_page_build",
            "pre_build_pages",
            "post_build_pages",
            "pre_prepare_page_expansion",
            "post_prepare_page_expansion",
            "pre_expand_pages",
            "post_expand_pages",
            "pre_render_pages",
            "post_render_pages",
            "pre_export_pages",
            "post_export_pages",
            "pre_finalize_page_build",
            "post_finalize_page_build",
        ):
            if page_group is None:
                page_group = "default"
            if page_group not in self._page_groups:
                self._page_groups[page_group] = PageGroup(page_group)
            self._page_groups[page_group].add_processor(stage, processor)
        else:
            raise ValueError("invalid processor stage: '{}'".format(stage))

    def create_root_build_context(self) -> RootBuildContext:
        if self.get_config_value("preserve_site_definition_across_builds"):
            page_groups = copy.deepcopy(self._page_groups)
            pre_preparation = copy.deepcopy(
                self._preprocessors_before_site_build_preparation_stage
            )
            post_preparation = copy.deepcopy(
                self._postprocessors_after_site_build_preparation_stage
            )
            pre_finalization = copy.deepcopy(
                self._preprocessors_before_site_build_finalization_stage
            )
            post_finalization = copy.deepcopy(
                self._postprocessors_after_site_build_finalization_stage
            )
        else:
            page_groups = self._page_groups.copy()
            pre_preparation = (
                self._preprocessors_before_site_build_preparation_stage
            ).copy()
            post_preparation = (
                self._postprocessors_after_site_build_preparation_stage
            ).copy()
            pre_finalization = (
                self._preprocessors_before_site_build_finalization_stage
            ).copy()
            post_finalization = (
                self._postprocessors_after_site_build_finalization_stage
            ).copy()

        build_config = {}
        for k in ROOT_BUILD_CONTEXT_CONFIG_KEYS:
            if k in self._config:
                build_config[k] = self._config[k]

        return RootBuildContext(
            page_groups,
            build_config,
            {
                "pre_prepare_site_build": pre_preparation,
                "post_prepare_site_build": post_preparation,
                "pre_finalize_site_build": pre_finalization,
                "post_finalize_site_build": post_finalization,
            },
        )

    def build_site(self):
        context = self.create_root_build_context()
        return context.build_site()

def render_page(
    page: Page,
    default_layout: Union[Layout, None] = None,
    processors: Union[
        Iterable[Tuple[str, Callable[[BuildContext], None]]],
        Iterable[
            Tuple[str, Callable[[BuildContext], None], Union[str, None]]
        ],
        None
    ] = None,
):
    config = {
        "export_root_path": "/",
        "build_strategy": "sync",
        "auto_write_exported_page_build_files": False,
        "auto_write_exported_site_build_files": False,
        "return_rendered_pages_after_page_build" : True,
    }
    if default_layout is not None:
        config["default_layout"] = default_layout
    site = Site(config, [("/", page)], processors)
    context = site.build_site()
    result = context.get_page_build_result("default")
    return result["rendered_pages"]["/"]

def render_nodes(
    *nodes,
    processors: Union[
        Iterable[Tuple[str, Callable[[BuildContext], None]]],
        Iterable[
            Tuple[str, Callable[[BuildContext], None], Union[str, None]]
        ],
        None
    ] = None,
):
    config = {
        "export_root_path": "/",
        "build_strategy": "sync",
        "auto_write_exported_page_build_files": False,
        "auto_write_exported_site_build_files": False,
        "return_rendered_pages_after_page_build" : True,
    }
    class TempPage(Page):
        def __init__(self, nodes):
            self.nodes = nodes
    class TempLayout(Layout):
        def build(self, page: TempPage, context: BuildContext):
            return page.nodes
    config["default_layout"] = TempLayout()
    site = Site(config, [("/", TempPage(list(nodes)))], processors)
    context = site.build_site()
    result = context.get_page_build_result("default")
    return result["rendered_pages"]["/"]

def render_html(
    *nodes,
    root_attributes: Union[Mapping, None] = None,
    processors: Union[
        Iterable[Tuple[str, Callable[[BuildContext], None]]],
        Iterable[
            Tuple[str, Callable[[BuildContext], None], Union[str, None]]
        ],
        None
    ] = None,
):
    root = HtmlElement(list(nodes), attributes=root_attributes)
    return render_nodes([HTML5Doctype(), root], processors=processors)
