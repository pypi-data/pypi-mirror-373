from abc import ABC
from collections import defaultdict
from contextlib import suppress
from dataclasses import Field, dataclass, fields
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar, Iterable, Self, TypeAlias

from model_lib import Entity, copy_and_validate, dump, parse_dict, parse_model
from pydantic import DirectoryPath, model_validator
from pydantic import Field as PydanticField
from zero_3rdparty.file_utils import ensure_parents_write_text
from zero_3rdparty.object_name import as_name

from atlas_init.tf_ext.plan_diffs import ExamplePlanCheck
from atlas_init.tf_ext.py_gen import (
    ContainerType,
    PrimitiveTypeError,
    import_from_path,
    make_post_init_line_from_field,
    module_dataclasses,
    unwrap_type,
)
from atlas_init.tf_ext.settings import RepoOut, TfExtSettings

ResourceTypeT: TypeAlias = str
TERRAFORM_DOCS_CONFIG_FILENAME: str = ".terraform-docs.yml"
README_FILENAME: str = "README.md"
EXAMPLES_DIRNAME: str = "examples"


@dataclass
class ResourceAbs(ABC):
    BLOCK_ATTRIBUTES_NAME: ClassVar[str] = "BLOCK_ATTRIBUTES"
    BLOCK_ATTRIBUTES: ClassVar[set[str]] = set()
    COMPUTED_ONLY_ATTRIBUTES_NAME: ClassVar[str] = "COMPUTED_ONLY_ATTRIBUTES"
    COMPUTED_ONLY_ATTRIBUTES: ClassVar[set[str]] = set()
    DEFAULTS_HCL_STRINGS_NAME: ClassVar[str] = "DEFAULTS_HCL_STRINGS"
    DEFAULTS_HCL_STRINGS: ClassVar[dict[str, str]] = {}
    NESTED_ATTRIBUTES_NAME: ClassVar[str] = "NESTED_ATTRIBUTES"
    NESTED_ATTRIBUTES: ClassVar[set[str]] = set()
    REQUIRED_ATTRIBUTES_NAME: ClassVar[str] = "REQUIRED_ATTRIBUTES"
    REQUIRED_ATTRIBUTES: ClassVar[set[str]] = set()
    SKIP_VARIABLES_NAME: ClassVar[str] = "SKIP_VARIABLES"
    SKIP_VARIABLES: ClassVar[set[str]] = set()

    @staticmethod
    def is_block(field_name: str, some_cls: type) -> bool:
        return field_name in getattr(some_cls, ResourceAbs.BLOCK_ATTRIBUTES_NAME, set())

    @staticmethod
    def is_required(field_name: str, some_cls: type) -> bool:
        return field_name in getattr(some_cls, ResourceAbs.REQUIRED_ATTRIBUTES_NAME, set())

    @staticmethod
    def is_computed_only(field_name: str, some_cls: type) -> bool:
        return field_name in getattr(some_cls, ResourceAbs.COMPUTED_ONLY_ATTRIBUTES_NAME, set())

    @staticmethod
    def is_nested(field_name: str, some_cls: type) -> bool:
        return field_name in getattr(some_cls, ResourceAbs.NESTED_ATTRIBUTES_NAME, set())

    @staticmethod
    def default_hcl_string(field_name: str, some_cls: type) -> str | None:
        return getattr(some_cls, ResourceAbs.DEFAULTS_HCL_STRINGS_NAME, {}).get(field_name)

    @staticmethod
    def skip_variable(field_name: str, some_cls: type) -> bool:
        return field_name in getattr(some_cls, ResourceAbs.SKIP_VARIABLES_NAME, set())


def as_import_line(name: str) -> str:
    from_part, name_part = name.rsplit(".", maxsplit=1)
    return f"from {from_part} import {name_part}"


class ResourceGenConfig(Entity):
    name: str
    use_single_variable: bool = False
    use_opt_in_required_variables: bool = False
    required_variables: set[str] = PydanticField(default_factory=set)
    skip_variables_extra: set[str] = PydanticField(default_factory=set)
    attribute_default_hcl_strings: dict[str, str] = PydanticField(default_factory=dict)
    include_id_field: bool = False

    @model_validator(mode="after")
    def add_id_as_skip_variable(self) -> Self:
        if not self.include_id_field:
            self.skip_variables_extra.add("id")  # SDKv2 Adds a computed+optional `id` field
        return self

    def single_variable_version(self) -> Self:
        assert not self.use_single_variable, "use_single_variable must be False to create a single variable version"
        return copy_and_validate(self, use_single_variable=True)


def as_provider_name(provider_path: str) -> str:
    return provider_path.rsplit("/", maxsplit=1)[-1]


class ProviderGenConfig(Entity):
    provider_path: str
    resources: list[ResourceGenConfig] = PydanticField(default_factory=list)
    settings: TfExtSettings = PydanticField(default_factory=TfExtSettings.from_env)
    last_gen_sha: str = ""

    def config_dump(self) -> dict[str, Any]:
        return {
            "provider_path": self.provider_path,
            "resources": [r.model_dump(exclude_defaults=True, exclude_unset=True) for r in self.resources],
            "last_gen_sha": self.last_gen_sha,
        }

    @property
    def provider_name(self) -> str:
        return self.provider_path.rsplit("/", maxsplit=1)[-1]

    def resource_types(self) -> list[str]:
        return [r.name for r in self.resources]

    def resource_config_or_none(self, resource_type: str) -> ResourceGenConfig | None:
        return next((r for r in self.resources if r.name == resource_type), None)


class ModuleGenConfig(Entity):
    CONFIG_FILENAME: ClassVar[str] = "config.yaml"
    FILENAME_EXAMPLE_CHECKS: ClassVar[str] = "example_plan_checks.yaml"
    FILENAME_EXAMPLES_TEST: ClassVar[str] = "examples_test.py"

    @classmethod
    def skip_copy(cls, src_file: Path) -> bool:
        return (
            src_file.stem.endswith("_test")
            or src_file.name == "__init__.py"
            or src_file.name in {cls.CONFIG_FILENAME, cls.FILENAME_EXAMPLE_CHECKS, cls.FILENAME_EXAMPLES_TEST}
        )

    name: str = ""
    resources: list[ResourceGenConfig] = PydanticField(default_factory=list)
    settings: TfExtSettings = PydanticField(default_factory=TfExtSettings.from_env)
    in_dir: Path | None = None
    out_dir: Path | None = None
    dataclass_out_dir: Path | None = None
    skip_python: bool = False
    debug_json_logs: bool = False
    example_plan_checks: list[ExamplePlanCheck] = PydanticField(default_factory=list)
    use_descriptions: bool = False
    inputs_json_hcl_extras: list[str] = PydanticField(default_factory=list)

    @model_validator(mode="after")
    def set_defaults(self) -> Self:
        if not self.name:
            assert self.resource_types, "must set either name or resource_types"
            self.name = self.resource_types[0]
        return self

    @property
    def resource_types(self) -> list[str]:
        return [r.name for r in self.resources]

    def resource_config(self, resource_type: str) -> ResourceGenConfig:
        config = next((r for r in self.resources if r.name == resource_type), None)
        if config is None:
            raise ValueError(f"module config {self.name} doesn't have: {resource_type}")
        return config

    @classmethod
    def from_repo_out(cls, resource_type: str, provider_config: ProviderGenConfig, repo_out: RepoOut) -> Self:
        resource_config = provider_config.resource_config_or_none(resource_type) or ResourceGenConfig(
            name=resource_type
        )
        return cls(
            name=resource_type,
            resources=[resource_config],
            settings=provider_config.settings,
            in_dir=None,
            out_dir=repo_out.resource_module_path(provider_config.provider_name, resource_type),
            dataclass_out_dir=repo_out.py_provider_module(provider_config.provider_name),
        )

    @classmethod
    def from_paths(cls, name: str, in_dir: DirectoryPath, out_dir: DirectoryPath, settings: TfExtSettings) -> Self:
        config_path = in_dir / name / f"{cls.CONFIG_FILENAME}"
        assert config_path.exists(), f"{config_path} does not exist"
        out_dir = out_dir or settings.modules_out_path
        assert out_dir.exists(), f"{out_dir} does not exist"
        config = parse_model(config_path, t=cls)
        config.out_dir = out_dir / name
        config.in_dir = in_dir / name
        config.settings = settings
        return config

    def skip_variables_extra(self, resource_type: str) -> set[str]:
        return next((r.skip_variables_extra for r in self.resources if r.name == resource_type), set())

    def required_variables(self, resource_type: str) -> set[str]:
        return next((r.required_variables for r in self.resources if r.name == resource_type), set())

    def attribute_default_hcl_strings(self, resource_type: str) -> dict[str, str]:
        return next((r.attribute_default_hcl_strings for r in self.resources if r.name == resource_type), {})

    @property
    def module_out_path(self) -> Path:
        if out_dir := self.out_dir:
            return out_dir
        parent_path = self.settings.modules_out_path
        return parent_path / self.name

    @property
    def example_plan_checks_path(self) -> Path:
        assert self.in_dir, "in_dir is required to find example checks"
        return self.in_dir / ModuleGenConfig.FILENAME_EXAMPLE_CHECKS

    @property
    def examples_test_path(self) -> Path:
        assert self.in_dir, "in_dir is required to find examples test"
        return self.in_dir / ModuleGenConfig.FILENAME_EXAMPLES_TEST

    def dataclass_path(self, resource_type: str) -> Path:
        # Must align with RepoOut.dataclass_path
        if dataclass_out_dir := self.dataclass_out_dir:
            return dataclass_out_dir / f"{resource_type}.py"
        return self.module_out_path / f"{resource_type}.py"

    def main_tf_path(self, resource_type: str) -> Path:
        if len(self.resource_types) > 1:
            return self.module_out_path / f"{resource_type}.tf"
        return self.module_out_path / "main.tf"

    def variables_path(self, resource_type: str) -> Path:
        if len(self.resource_types) > 1:
            return self.module_out_path / f"{resource_type}_variables.tf"
        return self.module_out_path / "variables.tf"

    def variablesx_path(self, resource_type: str) -> Path:
        if len(self.resource_types) > 1:
            return self.module_out_path / f"{resource_type}_variablesx.tf"
        return self.module_out_path / "variablesx.tf"

    def output_path(self, resource_type: str) -> Path:
        if len(self.resource_types) > 1:
            return self.module_out_path / f"{resource_type}_output.tf"
        return self.module_out_path / "output.tf"

    def output_name(self, resource_type: str, *attr_name: str) -> str:
        attr_single = "_".join(attr_name)
        if len(self.resource_types) > 1:
            return f"{resource_type}_{attr_single}"
        return attr_single

    def resolve_resource_type(self, path: Path) -> ResourceTypeT:
        if len(self.resource_types) == 1:
            return self.resource_types[0]
        for resource_type in self.resource_types:
            if path.name.startswith(resource_type):
                return resource_type
        raise ValueError(f"Could not resolve resource type for path {path}")

    @property
    def readme_path(self) -> Path:
        return self.module_out_path / README_FILENAME

    @property
    def examples_path(self) -> Path:
        return self.module_out_path / EXAMPLES_DIRNAME

    def example_name(self, name: str, example_nr: int) -> str:
        return f"{example_nr:02d}_{name}"

    def example_path(self, name: str) -> Path:
        return self.examples_path / name

    def terraform_docs_config_path(self) -> Path:
        return self.module_out_path / TERRAFORM_DOCS_CONFIG_FILENAME


@dataclass
class ResourceTypePythonModule:
    resource_type: str
    resource: type[ResourceAbs] | None = None
    resource_ext: type[ResourceAbs] | None = None
    module: ModuleType | None = None

    @property
    def dataclasses(self) -> dict[str, type]:
        if not self.module:
            return {}
        return module_dataclasses(self.module)

    @property
    def resource_ext_cls_used(self) -> bool:
        return self.resource_ext is not None

    @property
    def errors_func_used(self) -> bool:
        return self.module is not None and getattr(self.module, "errors", None) is not None

    @property
    def modify_out_func_used(self) -> bool:
        return self.module is not None and hasattr(self.module, "modify_out")

    @property
    def extra_post_init_lines(self) -> list[str]:
        if self.resource_ext is None:
            return []
        return [make_post_init_line_from_field(extra_field) for extra_field in self.extra_fields]

    @property
    def base_fields(self) -> list[Field]:
        if self.resource is None:
            return []
        return list(fields(self.resource))

    @property
    def base_field_names(self) -> list[str]:
        return sorted(f.name for f in self.base_fields)

    @property
    def all_fields(self) -> list[Field]:
        return self.base_fields + self.extra_fields

    @property
    def all_field_names(self) -> list[str]:
        return sorted(f.name for f in self.all_fields)

    @property
    def base_field_names_computed(self) -> list[str]:
        if self.resource is None:
            return []
        computed = getattr(self.resource, ResourceAbs.COMPUTED_ONLY_ATTRIBUTES_NAME, set())
        return sorted(name for name in self.base_field_names if name in computed)

    @property
    def base_field_names_not_computed(self) -> list[str]:
        computed = getattr(self.resource, ResourceAbs.COMPUTED_ONLY_ATTRIBUTES_NAME, set())
        return sorted(name for name in self.base_field_names if name not in computed)

    @property
    def extra_fields(self) -> list[Field]:
        if self.resource is None or self.resource_ext is None:
            return []
        base_fields = {f.name for f in self.base_fields}
        return sorted(
            (
                f
                for f in fields(self.resource_ext)
                if f.name not in base_fields and not ResourceAbs.skip_variable(f.name, self.resource_ext)
            ),
            key=lambda f: f.name,
        )

    @property
    def extra_fields_names(self) -> list[str]:
        return [f.name for f in self.extra_fields]

    @property
    def extra_import_lines(self) -> list[str]:
        module = self.module
        if not module:
            return []
        return [
            as_import_line(as_name(value))
            for key, value in vars(module).items()
            if not key.startswith("_") and not as_name(value).startswith(("__", self.resource_type))
        ]

    @property
    def all_skip_variables(self) -> set[str]:
        skip_vars = set()
        if self.resource:
            skip_vars.update(getattr(self.resource, ResourceAbs.SKIP_VARIABLES_NAME, set()))
        if self.resource_ext:
            skip_vars.update(getattr(self.resource_ext, ResourceAbs.SKIP_VARIABLES_NAME, set()))
        return skip_vars

    @property
    def nested_field_types(self) -> Iterable[tuple[str, ContainerType[ResourceAbs]]]:
        cls = self.resource_ext or self.resource
        if not cls:
            return []
        yield from self.container_types(cls)

    @staticmethod
    def container_types(data_class: type[ResourceAbs]) -> Iterable[tuple[str, ContainerType[ResourceAbs]]]:
        for field in fields(data_class):
            if ResourceAbs.is_nested(field.name, data_class):
                with suppress(PrimitiveTypeError):
                    container_type = unwrap_type(field)
                    yield field.name, container_type


class MissingDescriptionError(Exception):
    def __init__(self, attribute_name: str, resource_type: ResourceTypeT):
        super().__init__(f"Missing description for attribute {attribute_name} in resource type {resource_type}")
        self.attribute_name = attribute_name
        self.resource_type = resource_type


class AttributeDescriptions(Entity):
    manual_nested: dict[ResourceTypeT, dict[str, str]] = PydanticField(default_factory=lambda: defaultdict(dict))
    generated_nested: dict[ResourceTypeT, dict[str, str]] = PydanticField(default_factory=lambda: defaultdict(dict))
    manual_flat: dict[str, str] = PydanticField(default_factory=dict)
    generated_flat: dict[str, str] = PydanticField(default_factory=dict)

    def resolve_description(self, attribute_name: str, resource_type: ResourceTypeT) -> str:
        lookup_order = [
            self.manual_nested.get(resource_type, {}),
            self.generated_nested.get(resource_type, {}),
            self.manual_flat,
            self.generated_flat,
        ]
        try:
            return next(desc for desc_dict in lookup_order if (desc := desc_dict.get(attribute_name)))
        except StopIteration as e:
            raise MissingDescriptionError(attribute_name, resource_type) from e


def parse_attribute_descriptions(settings: TfExtSettings) -> AttributeDescriptions:
    return AttributeDescriptions(
        manual_nested=parse_dict(settings.attribute_resource_descriptions_manual_file_path)
        if settings.attribute_resource_descriptions_manual_file_path.exists()
        else {},
        generated_nested=parse_dict(settings.attribute_resource_descriptions_file_path)
        if settings.attribute_resource_descriptions_file_path.exists()
        else {},
        manual_flat=parse_dict(settings.attribute_description_manual_file_path)
        if settings.attribute_description_manual_file_path.exists()
        else {},
        generated_flat=parse_dict(settings.attribute_description_file_path)
        if settings.attribute_description_file_path.exists()
        else {},
    )


def store_updated_attribute_description(
    existing: AttributeDescriptions,
    settings: TfExtSettings,
    attribute_name: str,
    description: str,
    resource_type: ResourceTypeT = "",
):
    if resource_type:
        out_path = settings.attribute_resource_descriptions_manual_file_path
        existing.manual_nested.setdefault(resource_type, {})[attribute_name] = description
        out_yaml = dump(existing.manual_nested, "yaml")
    else:
        out_path = settings.attribute_description_manual_file_path
        existing.manual_flat[attribute_name] = description
        out_yaml = dump(existing.manual_flat, "yaml")
    ensure_parents_write_text(out_path, out_yaml)


def import_resource_type_python_module(resource_type: str, generated_dataclass_path: Path) -> ResourceTypePythonModule:
    module = import_from_path(resource_type, generated_dataclass_path)
    assert module
    resource = getattr(module, "Resource")
    assert resource
    resource_ext = getattr(module, "ResourceExt", None)
    return ResourceTypePythonModule(resource_type, resource, resource_ext, module)
