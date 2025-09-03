from typing import Annotated, Self, Union

from pydantic import Field
from pydantic.dataclasses import dataclass

from linq.schema import workflow_api
from linq.sdk_entity import SDKEntity


@dataclass(kw_only=True, slots=True)
class BooleanParameterDefinition(
    SDKEntity[workflow_api.BooleanParameterDefinitionInput, workflow_api.BooleanParameterDefinition]
):
    id: str = Field(
        ...,
        description="Unique identifier for the parameter. This is used to reference the parameter in the workflow definition.",
        title="Id",
    )
    name: str = Field(..., description="Human-readable name for the parameter.", title="Name")
    always_required: bool = Field(
        default=False,
        description="If true, the parameter is always required. If false, parameter is only required when publishing or validating for execution.",
    )
    default: bool | None = Field(..., description="Default value for the parameter.", title="Default")

    def to_api_input(self) -> workflow_api.BooleanParameterDefinitionInput:
        return workflow_api.BooleanParameterDefinitionInput(
            id=self.id,
            name=self.name,
            always_required=self.always_required,
            default=self.default,
        )


@dataclass(kw_only=True, slots=True)
class FloatParameterDefinition(
    SDKEntity[workflow_api.FloatParameterDefinitionInput, workflow_api.FloatParameterDefinition]
):
    id: str = Field(
        ...,
        description="Unique identifier for the parameter. This is used to reference the parameter in the workflow definition.",
        title="Id",
    )
    name: str = Field(..., description="Human-readable name for the parameter.", title="Name")
    always_required: bool = Field(
        default=False,
        description="If true, the parameter is always required. If false, parameter is only required when publishing or validating for execution.",
    )
    default: float | None = Field(
        default=None,
        description="Default value for the parameter.",
        title="Default",
    )
    minimum: float | None = Field(
        default=None,
        description="Minimum value for the parameter, greater than or equal to. If not provided, no minimum is enforced.",
        title="Minimum",
    )
    maximum: float | None = Field(
        default=None,
        description="Maximum value for the parameter, less than or equal to. If not provided, no maximum is enforced.",
        title="Maximum",
    )

    def to_api_input(self) -> workflow_api.FloatParameterDefinitionInput:
        return workflow_api.FloatParameterDefinitionInput(
            id=self.id,
            name=self.name,
            always_required=self.always_required,
            default=self.default,
            minimum=self.minimum,
            maximum=self.maximum,
        )


@dataclass(kw_only=True, slots=True)
class IntegerParameterDefinition(
    SDKEntity[workflow_api.IntegerParameterDefinitionInput, workflow_api.IntegerParameterDefinition]
):
    id: str = Field(
        ...,
        description="Unique identifier for the parameter. This is used to reference the parameter in the workflow definition.",
        title="Id",
    )
    name: str = Field(..., description="Human-readable name for the parameter.", title="Name")
    always_required: bool = Field(
        default=False,
        description="If true, the parameter is always required. If false, parameter is only required when publishing or validating for execution.",
    )
    default: int | None = Field(
        default=None,
        description="Default value for the parameter.",
        title="Default",
    )
    minimum: int | None = Field(
        default=None,
        description="Minimum value for the parameter, greater than or equal to. If not provided, no minimum is enforced.",
        title="Minimum",
    )
    maximum: int | None = Field(
        default=None,
        description="Maximum value for the parameter, less than or equal to. If not provided, no maximum is enforced.",
        title="Maximum",
    )
    multiple_of: int | None = Field(
        default=None,
        description="Value must be a multiple of this number. If not provided, no restriction is enforced.",
        title="Multiple Of",
    )

    def to_api_input(self) -> workflow_api.IntegerParameterDefinitionInput:
        return workflow_api.IntegerParameterDefinitionInput(
            id=self.id,
            name=self.name,
            always_required=self.always_required,
            default=self.default,
            minimum=self.minimum,
            maximum=self.maximum,
        )


@dataclass(kw_only=True, slots=True)
class StringParameterDefinition(
    SDKEntity[workflow_api.StringParameterDefinitionInput, workflow_api.StringParameterDefinition]
):
    id: str = Field(
        ...,
        description="Unique identifier for the parameter. This is used to reference the parameter in the workflow definition.",
        title="Id",
    )
    name: str = Field(..., description="Human-readable name for the parameter.", title="Name")
    always_required: bool = Field(
        default=False,
        description="If true, the parameter is always required. If false, parameter is only required when publishing or validating for execution.",
    )
    default: str | None = Field(
        default=None,
        description="Default value for the parameter.",
        title="Default",
    )
    is_file_path: bool | None = Field(
        default=False,
        description="If true, the parameter is expected to be a file path. This allows for additional validation.",
        title="Is File Path",
    )
    is_directory_path: bool = Field(
        default=False,
        description="If true, the parameter is expected to be a directory path. This allows for additional validation.",
        title="Is Directory Path",
    )

    def to_api_input(self) -> workflow_api.StringParameterDefinitionInput:
        return workflow_api.StringParameterDefinitionInput(
            id=self.id,
            name=self.name,
            always_required=self.always_required,
            default=self.default,
            is_file_path=self.is_file_path,
            is_directory_path=self.is_directory_path,
        )


@dataclass(kw_only=True, slots=True)
class ParameterReference(SDKEntity[workflow_api.ParameterReferenceInput, workflow_api.ParameterReference]):
    parameter_id: str

    def to_api_input(self) -> workflow_api.ParameterReferenceInput:
        return workflow_api.ParameterReferenceInput(parameter_id=self.parameter_id)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.ParameterReference) -> Self:
        return cls(parameter_id=api_output.parameter_id)


ParameterDefinition = Annotated[
    Union[
        BooleanParameterDefinition,
        IntegerParameterDefinition,
        FloatParameterDefinition,
        StringParameterDefinition,
    ],
    Field(discriminator="type"),
]

ParameterValue = Annotated[
    Union[
        workflow_api.BooleanParameterValueInput,
        workflow_api.IntegerParameterValueInput,
        workflow_api.FloatParameterValueInput,
        workflow_api.StringParameterValueInput,
    ],
    Field(discriminator="type"),
]
