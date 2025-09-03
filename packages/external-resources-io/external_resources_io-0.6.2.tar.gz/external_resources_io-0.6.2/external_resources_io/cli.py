import importlib
from pathlib import Path
from typing import Annotated, Protocol, cast

from pydantic import BaseModel

from external_resources_io.config import Config, EnvVar
from external_resources_io.input import (
    AppInterfaceProvision,
    parse_model,
    read_input_from_file,
)
from external_resources_io.terraform.generators import (
    create_backend_tf_file,
    create_tf_vars_json,
    create_variables_tf_file,
)

try:
    import typer
except ImportError:
    raise ImportError(
        "Please install external-resources-io with `pip install external-resources-io[cli]`"
    ) from None


app = typer.Typer()
tf_app = typer.Typer()
app.add_typer(tf_app, name="tf")
config = Config()


class AppInterfaceInputInterface(Protocol):
    data: BaseModel
    provision: AppInterfaceProvision


def _get_app_interface_class(app_interface_input_class: str) -> type[BaseModel]:
    ai_module_name, ai_class_name = app_interface_input_class.rsplit(".", maxsplit=1)
    ai_class = getattr(importlib.import_module(ai_module_name), ai_class_name)
    if not issubclass(ai_class, BaseModel):
        raise TypeError(
            f"{app_interface_input_class} must be a subclass of pydantic.BaseModel"
        )
    return ai_class


def _get_app_interface_data_class(app_interface_input_class: str) -> type[BaseModel]:
    data_class = (
        _get_app_interface_class(app_interface_input_class)
        .model_fields["data"]
        .annotation
    )
    if not data_class or not issubclass(data_class, BaseModel):
        raise TypeError(f"{data_class} must be a subclass of pydantic.BaseModel")
    return data_class


def _get_ai_input(
    app_interface_input_class: str, input_file: Path | None
) -> AppInterfaceInputInterface:
    """Get the AppInterfaceInput from the input file."""
    return cast(
        "AppInterfaceInputInterface",
        parse_model(
            _get_app_interface_class(app_interface_input_class),
            read_input_from_file(input_file),
        ),
    )


@tf_app.command()
def generate_variables_tf(
    app_interface_input_class: Annotated[
        str,
        typer.Argument(
            help="App interface input class. E.g. your_module_name.input.AppInterfaceInput",
            show_default=False,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            help="Output file",
            dir_okay=False,
            writable=True,
            envvar=EnvVar.OUTPUTS_FILE,
        ),
    ] = Path(config.variables_tf_file),
) -> None:
    """Generates Terraform variables.tf file."""
    create_variables_tf_file(
        _get_app_interface_data_class(app_interface_input_class), output
    )


@tf_app.command()
def generate_backend_tf(
    app_interface_input_class: Annotated[
        str,
        typer.Argument(
            help="App interface input class. E.g. your_module_name.input.AppInterfaceInput",
            show_default=False,
        ),
    ],
    input_file: Annotated[
        Path,
        typer.Argument(
            help="The App interface input json file",
            show_default=False,
            readable=True,
            file_okay=True,
            envvar=EnvVar.INPUT_FILE,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            help="Output file",
            dir_okay=False,
            writable=True,
            envvar=EnvVar.OUTPUTS_FILE,
        ),
    ] = Path(config.backend_tf_file),
) -> None:
    """Generates Terraform backends.tf file."""
    ai_input = _get_ai_input(app_interface_input_class, input_file)
    create_backend_tf_file(ai_input.provision, output)


@tf_app.command()
def generate_tf_vars_json(
    app_interface_input_class: Annotated[
        str,
        typer.Argument(
            help="App interface input class. E.g. your_module_name.input.AppInterfaceInput",
            show_default=False,
        ),
    ],
    input_file: Annotated[
        Path,
        typer.Argument(
            help="The App interface input json file",
            show_default=False,
            readable=True,
            file_okay=True,
            envvar=EnvVar.INPUT_FILE,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            help="Output file",
            dir_okay=False,
            writable=True,
            envvar=EnvVar.OUTPUTS_FILE,
        ),
    ] = Path(config.tf_vars_file),
) -> None:
    """Generates Terraform tfvars.json file."""
    ai_input = _get_ai_input(app_interface_input_class, input_file)
    create_tf_vars_json(ai_input.data, output)


if __name__ == "__main__":
    app()
