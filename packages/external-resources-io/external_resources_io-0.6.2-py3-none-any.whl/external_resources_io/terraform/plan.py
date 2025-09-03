from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

# Ref: https://github.com/hashicorp/terraform-json/blob/main/plan.go


class Action(Enum):
    # ActionNoop denotes a no-op operation.
    ActionNoop = "no-op"
    # ActionCreate denotes a create operation.
    ActionCreate = "create"
    # ActionRead denotes a read operation.
    ActionRead = "read"
    # ActionUpdate denotes an update operation.
    ActionUpdate = "update"
    # ActionDelete denotes a delete operation.
    ActionDelete = "delete"
    # ActionForget denotes a forget operation.
    ActionForget = "forget"


class Change(BaseModel):
    # This class only has the required attributes to
    # do the validation
    # The action to be carried out by this change.
    actions: list[Action] = []
    # Before and After are representations of the object value both
    # before and after the action. For create and delete actions,
    # either Before or After is unset (respectively). For no-op
    # actions, both values will be identical. After will be incomplete
    # if there are values within it that won't be known until after
    # apply.
    before: Any | None = None
    after: Any | None = None
    # A deep object of booleans that denotes any values that are
    # unknown in a resource. These values were previously referred to
    # as "computed" values.
    # If the value cannot be found in this map, then its value should
    # be available within After, so long as the operation supports it.
    after_unknown: Any
    # BeforeSensitive and AfterSensitive are object values with similar
    # structure to Before and After, but with all sensitive leaf values
    # replaced with true, and all non-sensitive leaf values omitted. These
    # objects should be combined with Before and After to prevent accidental
    # display of sensitive values in user interfaces.
    before_sensitive: Any | None = None
    after_sensitive: Any | None = None


class ResourceChange(BaseModel):
    # The absolute resource address.
    address: str | None = None
    # The absolute address that this resource instance had
    # at the conclusion of a previous plan.
    previous_address: str | None = None
    # The module portion of the above address. Omitted if the instance
    # is in the root module.
    module_address: str | None = None
    # The resource mode
    resource_mode: str | None = None
    # The resource type, example: "aws_instance" for aws_instance.foo.
    type: str = ""
    # The resource name, example: "foo" for aws_instance.foo.
    name: str = ""
    # The instance key for any resources that have been created using
    # "count" or "for_each". If neither of these apply the key will be
    # empty.
    index: str | int | None = None
    # The name of the provider this resource belongs to. This allows
    # the provider to be interpreted unambiguously in the unusual
    # situation where a provider offers a resource type whose name
    # does not start with its own name, such as the "googlebeta"
    # provider offering "google_compute_instance".
    provider_name: str | None = None
    # The data describing the change that will be made to this object.
    change: Change | None = None


class DeferredResourceChange(BaseModel):
    # Reason is the reason why this resource change was deferred.
    reason: str | None = None
    resource_change: ResourceChange | None = None


class ResourceAttribute(BaseModel):
    resource: str
    attribute: list[str]


class Plan(BaseModel):
    # The version of the plan format. This should always match the
    # PlanFormatVersion constant in this package, or else an unmarshal
    # will be unstable.
    format_version: str | None = None

    # The version of Terraform used to make the plan.
    terraform_version: str | None = None

    # The variables set in the root module when creating the plan.
    # Variables map[string]*PlanVariable `json:"variables,omitempty"`

    # The common state representation of resources within this plan.
    # This is a product of the existing state merged with the diff for
    # this plan.
    # PlannedValues *StateValues `json:"planned_values,omitempty"`
    planned_values: dict[str, Any] = {}

    # The change operations for resources and data sources within this plan
    # resulting from resource drift.
    resource_drift: list[ResourceChange] = []

    # The change operations for resources and data sources within this
    # plan.
    resource_changes: list[ResourceChange] = []

    # DeferredChanges contains the change operations for resources that are deferred
    # for this plan.
    deferred_changes: list[DeferredResourceChange] = []

    # Complete indicates that all resources have successfully planned changes.
    # This will be false if there are DeferredChanges or if the -target flag is used.

    # Complete was introduced in Terraform 1.8 and will be nil for all previous
    # Terraform versions.
    complete: bool | None = None

    # The change operations for outputs within this plan.
    output_changes: dict[str, Change] = {}

    # The Terraform state prior to the plan operation. This is the
    # same format as PlannedValues, without the current diff merged.
    # PriorState *State `json:"prior_state,omitempty"`
    prior_state: dict[str, Any] = {}

    # The Terraform configuration used to make the plan.
    # Config *Config `json:"configuration,omitempty"`
    configuration: dict[str, Any] = {}

    # RelevantAttributes represents any resource instances and their
    # attributes which may have contributed to the planned changes
    # RelevantAttributes []ResourceAttribute `json:"relevant_attributes,omitempty"`
    relevant_attributes: list[ResourceAttribute] = []

    # Checks contains the results of any conditional checks executed, or
    # planned to be executed, during this plan.
    # Checks []CheckResultStatic `json:"checks,omitempty"`
    checks: dict[str, Any] = {}

    # Timestamp contains the static timestamp that Terraform considers to be
    # the time this plan executed, in UTC.
    timestamp: str | None = None

    errored: bool | None = None


class TerraformJsonPlanParser:
    def __init__(self, plan_path: str) -> None:
        self.plan = Plan.model_validate_json(
            Path(plan_path).read_text(encoding="utf-8")
        )
