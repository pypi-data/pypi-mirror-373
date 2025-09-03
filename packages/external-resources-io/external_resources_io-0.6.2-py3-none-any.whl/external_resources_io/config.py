from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Action(StrEnum):
    APPLY = "apply"
    DESTROY = "destroy"


class EnvVar:
    ACTION = "ACTION"
    DRY_RUN = "DRY_RUN"
    LOG_LEVEL = "LOG_LEVEL"
    INPUT_FILE = "INPUT_FILE"
    BACKEND_TF_FILE = "BACKEND_TF_FILE"
    OUTPUTS_FILE = "OUTPUTS_FILE"
    PLAN_FILE_JSON = "PLAN_FILE_JSON"
    TERRAFORM_CMD = "TERRAFORM_CMD"
    TF_VARS_FILE = "TF_VARS_FILE"
    VARIABLES_TF_FILE = "VARIABLES_TF_FILE"


class Config(BaseSettings):
    """Environment Variables."""

    # general settings
    action: Action = Field(Action.APPLY, alias=EnvVar.ACTION)
    dry_run: bool = Field(default=True, alias=EnvVar.DRY_RUN)
    log_level: str = Field("INFO", alias=EnvVar.LOG_LEVEL)

    # app-interface input related
    input_file: str = Field("/inputs/input.json", alias=EnvVar.INPUT_FILE)

    backend_tf_file: str = Field("module/backend.tf", alias=EnvVar.BACKEND_TF_FILE)
    outputs_file: str = Field("tmp/outputs.json", alias=EnvVar.OUTPUTS_FILE)
    plan_file_json: str = Field("tmp/plan.json", alias=EnvVar.PLAN_FILE_JSON)
    terraform_cmd: str = Field("terraform", alias=EnvVar.TERRAFORM_CMD)
    tf_vars_file: str = Field("module/terraform.tfvars.json", alias=EnvVar.TF_VARS_FILE)
    variables_tf_file: str = Field(
        "module/variables.tf", alias=EnvVar.VARIABLES_TF_FILE
    )

    @field_validator("action", mode="before")
    @classmethod
    def action_lower(cls, v: str) -> str:
        """Always lower action string to match with Action enum."""
        return v.lower()
