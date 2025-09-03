# ruff: noqa: ANN401
import json
from collections.abc import Sequence
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from external_resources_io.config import Config
from external_resources_io.input import AppInterfaceProvision
from external_resources_io.terraform.run import terraform_fmt


class SetEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def create_tf_vars_json(
    input_data: BaseModel,
    output_file: Path | str | None = None,
    *,
    exclude_none: bool = True,
) -> Path:
    """Helper method to create teraform vars files. Used in terraform based ERv2 modules."""
    output = Path(output_file or Config().tf_vars_file)
    output.write_text(
        input_data.model_dump_json(exclude_none=exclude_none),
        encoding="utf-8",
    )
    return output


def create_backend_tf_file(
    provision_data: AppInterfaceProvision, output_file: Path | str | None = None
) -> Path:
    """Helper method to create teraform backend configuration. Used in terraform based ERv2 modules."""
    output = Path(output_file or Config().backend_tf_file)
    output.write_text(
        terraform_fmt(f"""\
            terraform {{
              backend "s3" {{
                bucket = "{provision_data.module_provision_data.tf_state_bucket}"
                key    = "{provision_data.module_provision_data.tf_state_key}"
                region = "{provision_data.module_provision_data.tf_state_region}"
                dynamodb_table = "{provision_data.module_provision_data.tf_state_dynamodb_table}"
                profile = "external-resources-state"
              }}
            }}"""),
        encoding="utf-8",
    )
    return output


def create_variables_tf_file(
    model: type[BaseModel], variables_file: Path | str | None = None
) -> Path:
    """Generates Terraform variables.tf file."""
    output = Path(variables_file or Config().variables_tf_file)
    output.write_text(
        terraform_fmt(
            _convert_json_to_hcl(_generate_terraform_variables_from_model(model))
        ),
        encoding="utf-8",
    )
    return output


def _generate_fields(model: type[BaseModel]) -> dict[str, dict]:
    return {
        field_name: _generate_terraform_variable(
            python_type=field_info.annotation,
            default=field_info.default,
            description=field_info.description,
        )
        for field_name, field_info in model.model_fields.items()
    }


def _generate_terraform_variables_from_model(model: type[BaseModel]) -> dict:
    """Generates Terraform variables json."""
    return {"variable": _generate_fields(model)}


def _generate_terraform_variable(
    python_type: Any, default: Any = None, description: str | None = None
) -> dict:
    """Generates a Terraform variable block."""
    variable_block: dict[str, str | None] = {"type": _get_terraform_type(python_type)}

    if default is not PydanticUndefined:
        variable_block["default"] = (
            default.model_dump()
            if default and isinstance(default, BaseModel)
            else default
        )
    if description:
        variable_block["description"] = description
    return variable_block


def _convert_generic_types(origin: Any, args: Any) -> str:  # noqa: PLR0911
    """Convert generic types to Terraform types."""
    match origin:
        case t if t in {list, Sequence}:
            return f"list({_get_terraform_type(args[0])})" if args else "list(any)"

        case t if t is set:
            return f"set({_get_terraform_type(args[0])})" if args else "set(any)"

        case t if t is dict:
            return f"map({_get_terraform_type(args[1])})" if args else "map(any)"

        case t if t is Literal:
            return "string"

        case t if t in {UnionType, Union}:
            if type(None) in args:
                return _get_terraform_type(args[0])
            return "any"

        case _:
            return "any"


def _convert_basic_types(python_type: Any) -> str:  # noqa: PLR0911
    """Convert basic python types to Terraform types."""
    match python_type:
        case t if t is str:
            return "string"
        case t if t is int:
            return "number"
        case t if t is bool:
            return "bool"
        case t if t is list:
            return "list(any)"
        case t if t is set:
            return "set(any)"
        case t if t is dict:
            return "map(any)"
        case t if issubclass(t, BaseModel):
            # nested model
            fields_types = ",".join(
                f"{k} = {v['type']}" for k, v in _generate_fields(t).items()
            )
            return f"object({{{fields_types}}})"
        case _:
            return "any"


def _get_terraform_type(python_type: Any) -> str:
    """Maps Python types to Terraform types."""
    origin = get_origin(python_type)
    args = get_args(python_type)

    return (
        _convert_generic_types(origin, args)
        if origin is not None
        else _convert_basic_types(python_type)
    )


def _convert_json_value_to_hcl(value: Any) -> str:  # noqa: PLR0911
    """Converts a JSON value to HCL."""
    match value:
        case t if isinstance(t, str):
            return f'"{value}"'
        case t if isinstance(t, bool):
            return str(value).lower()
        case t if isinstance(t, int | float):
            return str(value)
        case t if isinstance(t, list | set):
            if not value:
                return "[]"
            return "[" + ",".join(_convert_json_value_to_hcl(e) for e in value) + "]"
        case t if isinstance(t, dict):
            if not value:
                return "{}"
            pairs = []
            for k, v in value.items():
                converted_v = _convert_json_value_to_hcl(v)
                pairs.append(f"{k} = {converted_v}")
            return "{\n" + "\n".join(pairs) + "\n}"
        case None:
            return "null"
        case _:
            return str(value)


def _convert_json_to_hcl(data: dict) -> str:
    variables = data.get("variable", {})
    hcl_blocks = []

    for var_name, var_config in sorted(variables.items()):
        block_lines = [f'variable "{var_name}" {{']
        for key, value in var_config.items():
            hcl_value = value if key == "type" else _convert_json_value_to_hcl(value)
            block_lines.append(f"{key} = {hcl_value}")
        block_lines.append("}\n")
        hcl_blocks.append("\n".join(block_lines))

    return "\n".join(hcl_blocks)
