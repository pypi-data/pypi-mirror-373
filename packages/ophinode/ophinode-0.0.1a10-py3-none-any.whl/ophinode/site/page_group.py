import sys
from typing import Any
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Callable, Mapping, Iterable
else:
    from collections.abc import Callable, Mapping, Iterable

from .build_contexts import BuildContext, BUILD_CONTEXT_CONFIG_KEYS

PAGE_GROUP_CONFIG_DEFAULT_VALUES = {
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
PAGE_GROUP_CONFIG_KEYS = set(PAGE_GROUP_CONFIG_DEFAULT_VALUES)

class PageGroup:
    def __init__(self, name):
        self._name = name
        self._config = {}
        self._pages_dict = {}
        self._pages = []
        self._dependency_group_of_pages = {}    # page path -> dependency group name
        self._dependencies = {}

        self._dependencies_in_page_build_preparation_stage = {}
        self._dependencies_in_page_build_stage = {}
        self._dependencies_in_page_expansion_preparation_stage = {}
        self._dependencies_in_page_expansion_stage = {}
        self._dependencies_in_page_rendering_stage = {}
        self._dependencies_in_page_exportation_stage = {}
        self._dependencies_in_page_build_finalization_stage = {}

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

    @property
    def name(self):
        return self._name

    def create_build_context(
        self,
        build_config,
        site_data,
        page_data,
    ):
        pages = self._pages.copy()
        dependencies = self._dependencies.copy()

        pre_page_build_preps = (
            self._preprocessors_before_page_build_preparation_stage
        ).copy()
        post_page_build_preps = (
            self._postprocessors_after_page_build_preparation_stage
        ).copy()
        pre_page_builds = (
            self._preprocessors_before_page_build_stage
        ).copy()
        post_page_builds = (
            self._postprocessors_after_page_build_stage
        ).copy()
        pre_page_expand_preps = (
            self._preprocessors_before_page_expansion_preparation_stage
        ).copy()
        post_page_expand_preps = (
            self._postprocessors_after_page_expansion_preparation_stage
        ).copy()
        pre_page_expands = (
            self._preprocessors_before_page_expansion_stage
        ).copy()
        post_page_expands = (
            self._postprocessors_after_page_expansion_stage
        ).copy()
        pre_page_renders = (
            self._preprocessors_before_page_rendering_stage
        ).copy()
        post_page_renders = (
            self._postprocessors_after_page_rendering_stage
        ).copy()
        pre_page_exports = (
            self._preprocessors_before_page_exportation_stage
        ).copy()
        post_page_exports = (
            self._postprocessors_after_page_exportation_stage
        ).copy()
        pre_page_build_finalizations = (
            self._preprocessors_before_page_build_finalization_stage
        ).copy()
        post_page_build_finalizations = (
            self._postprocessors_after_page_build_finalization_stage
        ).copy()

        cfg = {}
        for k in BUILD_CONTEXT_CONFIG_KEYS:
            if k in self._config:
                cfg[k] = self._config[k]
            elif k in build_config:
                cfg[k] = build_config[k]
            else:
                cfg[k] = self.get_config_value(k)

        return BuildContext(
            self._name,
            pages,
            dependencies,
            site_data,
            page_data,
            cfg,
            {
                "pre_prepare_page_build": pre_page_build_preps,
                "post_prepare_page_build": post_page_build_preps,
                "pre_build_pages": pre_page_builds,
                "post_build_pages": post_page_builds,
                "pre_prepare_page_expansion": pre_page_expand_preps,
                "post_prepare_page_expansion": post_page_expand_preps,
                "pre_expand_pages": pre_page_expands,
                "post_expand_pages": post_page_expands,
                "pre_render_pages": pre_page_renders,
                "post_render_pages": post_page_renders,
                "pre_export_pages": pre_page_exports,
                "post_export_pages": post_page_exports,
                "pre_finalize_page_build": pre_page_build_finalizations,
                "post_finalize_page_build": post_page_build_finalizations,
            },
        )

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError(
                "key must be a str, not {}".format(key.__class__.__name__)
            )
        if key not in PAGE_GROUP_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(key))
        if key in self._config:
            return self._config[key]
        return PAGE_GROUP_CONFIG_DEFAULT_VALUES[key]

    def set_config_value(self, key: str, value: Any):
        if not isinstance(key, str):
            raise TypeError(
                "key must be a str, not {}".format(key.__class__.__name__)
            )
        if key not in PAGE_GROUP_CONFIG_KEYS:
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
            if k not in PAGE_GROUP_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def add_page(self, page_definition):
        path = page_definition.path
        dependency_group = page_definition.dependency_group

        if dependency_group is None:
            dependency_group = path
        self._dependency_group_of_pages[path] = dependency_group

        self._pages_dict[page_definition.path] = page_definition
        self._pages.append(page_definition)

    def add_processor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None],
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")

        if stage == "pre_prepare_page_build":
            self._preprocessors_before_page_build_preparation_stage.append(processor)
        elif stage == "post_prepare_page_build":
            self._postprocessors_after_page_build_preparation_stage.append(processor)
        elif stage == "pre_build_pages":
            self._preprocessors_before_page_build_stage.append(processor)
        elif stage == "post_build_pages":
            self._postprocessors_after_page_build_stage.append(processor)
        elif stage == "pre_prepare_page_expansion":
            self._preprocessors_before_page_expansion_preparation_stage.append(processor)
        elif stage == "post_prepare_page_expansion":
            self._postprocessors_after_page_expansion_preparation_stage.append(processor)
        elif stage == "pre_expand_pages":
            self._preprocessors_before_page_expansion_stage.append(processor)
        elif stage == "post_expand_pages":
            self._postprocessors_after_page_expansion_stage.append(processor)
        elif stage == "pre_render_pages":
            self._preprocessors_before_page_rendering_stage.append(processor)
        elif stage == "post_render_pages":
            self._postprocessors_after_page_rendering_stage.append(processor)
        elif stage == "pre_export_pages":
            self._preprocessors_before_page_exportation_stage.append(processor)
        elif stage == "post_export_pages":
            self._postprocessors_after_page_exportation_stage.append(processor)
        elif stage == "pre_finalize_page_build":
            self._preprocessors_before_page_build_finalization_stage.append(processor)
        elif stage == "post_finalize_page_build":
            self._postprocessors_after_page_build_finalization_stage.append(processor)
        else:
            raise ValueError("invalid processor stage: '{}'".format(stage))
