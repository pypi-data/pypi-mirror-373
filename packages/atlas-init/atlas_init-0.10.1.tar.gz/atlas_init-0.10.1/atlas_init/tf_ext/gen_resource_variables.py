import logging
from contextlib import contextmanager
from dataclasses import Field, fields, is_dataclass
from typing import Dict, List, Set, Union, get_args, get_origin, get_type_hints

from model_lib import Entity
from pydantic import Field as PydanticField

from atlas_init.tf_ext.gen_resource_main import format_tf_content
from atlas_init.tf_ext.models_module import ResourceAbs, ResourceGenConfig, ResourceTypePythonModule

logger = logging.getLogger(__name__)


class DefaultValueContext(Entity):
    default_lines: list[str] = PydanticField(default_factory=list)
    field_path: list[str] = PydanticField(default_factory=list)
    ignored_names: set[str] = PydanticField(default_factory=set)

    @property
    def final_str(self) -> str:
        if not self.default_lines:
            return "null"
        return "\n".join(self.default_lines)

    @property
    def current_field_path(self) -> str:
        return ".".join(self.field_path)

    def at_root(self, field_name: str) -> bool:
        return field_name == self.current_field_path

    @property
    def _prefix(self) -> str:
        return "  " * len(self.field_path)

    @contextmanager
    def add_nested_field(self, field_name: str):
        if not self.at_root(field_name):
            self.field_path.append(field_name)
        default_index_before = len(self.default_lines)
        try:
            yield
            default_index_after = len(self.default_lines)
            if (
                default_index_before == default_index_after
            ):  # no child had a default, so we don't need to add default lines
                return
            if self.at_root(field_name):
                self.default_lines.insert(default_index_before, "{")
            else:
                self.default_lines.insert(default_index_before, f"{self._prefix}{field_name} = {{")
            self.default_lines.append(f"{self._prefix}}}")
        finally:
            self.field_path.pop()

    def add_default(self, field_name: str, default_value: str) -> None:
        if self.at_root(field_name):  # root field default value, no field name needed
            self.default_lines.append(default_value)
        else:
            self.default_lines.append(f"{self._prefix}{field_name} = {default_value}")


def python_type_to_terraform_type(field: Field, py_type: type, context: DefaultValueContext) -> str:
    # Unwrap Optional/Union
    origin = get_origin(py_type)
    args = get_args(py_type)
    if origin is Union and type(None) in args:
        # Optional[X] or Union[X, None] -> X
        not_none = [a for a in args if a is not type(None)]
        return python_type_to_terraform_type(field, not_none[0], context) if not_none else "any"
    if origin is list or origin is List:
        elem_type = python_type_to_terraform_type(field, args[0], context)
        return f"list({elem_type})"
    elif origin is set or origin is Set:
        elem_type = python_type_to_terraform_type(field, args[0], context)
        return f"set({elem_type})"
    elif origin is dict or origin is Dict:
        elem_type = python_type_to_terraform_type(field, args[1], context)
        return f"map({elem_type})"
    elif is_dataclass(py_type):
        return dataclass_to_object_type(field.name, py_type, context)
    elif py_type is str:
        return "string"
    elif py_type is int or py_type is float:
        return "number"
    elif py_type is bool:
        return "bool"
    else:
        return "any"


def dataclass_to_object_type(name: str, cls: type, context: DefaultValueContext) -> str:
    lines = ["object({"]
    hints = get_type_hints(cls)
    with context.add_nested_field(name):
        for f in fields(cls):
            # Skip ClassVars and internal fields
            nested_field_name = f.name
            is_computed_only = ResourceAbs.is_computed_only(nested_field_name, cls)
            if is_computed_only or nested_field_name in context.ignored_names:
                continue
            tf_type = python_type_to_terraform_type(f, hints[nested_field_name], context)
            is_required = ResourceAbs.is_required(nested_field_name, cls)
            if default_value := ResourceAbs.default_hcl_string(nested_field_name, cls):
                context.add_default(nested_field_name, default_value)
                lines.append(f"  {nested_field_name} = optional({tf_type}, {default_value})")
            elif is_required:
                lines.append(f"  {nested_field_name} = {tf_type}")
            else:
                lines.append(f"  {nested_field_name} = optional({tf_type})")
        lines.append("})")
    return "\n".join(lines)


def generate_module_variables(
    python_module: ResourceTypePythonModule, resource_config: ResourceGenConfig
) -> tuple[str, str]:
    base_resource = python_module.resource
    assert base_resource is not None, f"{python_module} does not have a resource"
    skipped_names_in_resource_ext = set(python_module.base_field_names)
    return generate_resource_variables(base_resource, resource_config), generate_resource_variables(
        python_module.resource_ext, resource_config, skipped_names_in_resource_ext
    )


def generate_resource_variables(
    resource: type[ResourceAbs] | None, resource_config: ResourceGenConfig, extra_skipped: set[str] | None = None
) -> str:
    extra_skipped = extra_skipped or set()
    if resource is None:
        return ""
    required_variables = set(resource_config.required_variables)
    if not resource_config.use_opt_in_required_variables:
        required_variables |= getattr(resource, ResourceAbs.REQUIRED_ATTRIBUTES_NAME, set())
    out = []
    hints = get_type_hints(resource)
    ignored_names = (
        resource_config.skip_variables_extra
        | resource.COMPUTED_ONLY_ATTRIBUTES
        | getattr(resource, ResourceAbs.SKIP_VARIABLES_NAME, set())
        | extra_skipped
    )
    if resource_config.use_single_variable:
        context = DefaultValueContext(field_path=[], ignored_names=ignored_names)
        tf_type = dataclass_to_object_type(resource_config.name, resource, context)
        return format_tf_content(f'''variable "{resource_config.name}" {{
  type     = {tf_type}
}}\n''')
    fields_sorted = sorted(fields(resource), key=lambda f: (0 if f.name in required_variables else 1, f.name))
    for f in fields_sorted:  # type: ignore
        field_name = f.name
        if field_name.isupper() or field_name in ignored_names:
            continue
        context = DefaultValueContext(field_path=[field_name])
        tf_type = python_type_to_terraform_type(f, hints[field_name], context)
        default_line = f"\n  default  = {context.final_str}" if field_name not in required_variables else ""
        nullable_line = "\n  nullable = true" if field_name not in required_variables else ""
        out.append(f'''variable "{field_name}" {{
  type     = {tf_type}{nullable_line}{default_line}
}}\n''')
    return format_tf_content("\n".join(out))
