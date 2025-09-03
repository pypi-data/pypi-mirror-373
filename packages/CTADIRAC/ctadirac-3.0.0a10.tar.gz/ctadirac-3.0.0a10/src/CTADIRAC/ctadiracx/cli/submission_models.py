"""
CLI interface to run a CWL workflow from end to end (production/transformation/job).
"""

from typing import Any
from collections.abc import Mapping

from cwl_utils.parser import save
from cwl_utils.parser.cwl_v1_2 import (
    CommandLineTool,
    Workflow,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
    field_validator,
)

from CTADIRAC.ctadiracx.cli.metadata_models import IMetadataModel

# -----------------------------------------------------------------------------
# Job models
# -----------------------------------------------------------------------------


class JobDescriptionModel(BaseModel):
    """Description of a job."""

    platform: str | None = None
    priority: int = 10
    sites: list[str] | None = None


class JobParameterModel(BaseModel):
    """Parameter of a job."""

    # Allow arbitrary types to be passed to the model
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sandbox: list[str] | None
    cwl: dict[str, Any]

    @field_serializer("cwl")
    def serialize_cwl(self, value):
        return save(value)


class JobMetadataModel(BaseModel):
    """Job metadata."""

    type: str = "User"
    # Parameters used to build input/output queries
    # Generally correspond to the inputs of the previous transformations
    query_params: dict[str, Any] = {}

    # Validation to ensure type corresponds to a subclass of IMetadataModel
    @field_validator("type")
    def check_type(cls, value):
        # Collect all subclass names of IMetadataModel
        valid_types = {cls.__name__ for cls in IMetadataModel.__subclasses__()}

        # Check if the provided value matches any of the subclass names
        if value not in valid_types:
            raise ValueError(
                f"Invalid type '{value}'. Must be one of: {', '.join(valid_types)}."
            )

        return value

    def model_copy(
        self,
        *,
        update: Mapping[str, Any] | None = None,
        deep: bool = False,
    ) -> "JobMetadataModel":
        if update is None:
            update = {}
        else:
            update = dict(update)

        # Handle merging of query_params
        if "query_params" in update:
            new_query_params = self.query_params.copy()
            new_query_params.update(update.pop("query_params"))
            update["query_params"] = new_query_params

        return super().model_copy(update=update, deep=deep)


class JobSubmissionModel(BaseModel):
    """Job definition sent to the router."""

    # Allow arbitrary types to be passed to the model
    model_config = ConfigDict(arbitrary_types_allowed=True)

    task: CommandLineTool | Workflow
    parameters: list[JobParameterModel] | None = None
    description: JobDescriptionModel
    metadata: JobMetadataModel

    @field_serializer("task")
    def serialize_task(self, value):
        if isinstance(value, (CommandLineTool, Workflow)):
            return save(value)
        else:
            raise TypeError(f"Cannot serialize type {type(value)}")


# -----------------------------------------------------------------------------
# Transformation models
# -----------------------------------------------------------------------------


class TransformationMetadataModel(JobMetadataModel):
    """Transformation metadata."""

    # Number of data to group together in a transformation
    # Key: input name, Value: group size
    group_size: dict[str, int] | None = None


class TransformationSubmissionModel(BaseModel):
    """Transformation definition sent to the router."""

    # Allow arbitrary types to be passed to the model
    model_config = ConfigDict(arbitrary_types_allowed=True)

    task: CommandLineTool | Workflow
    metadata: TransformationMetadataModel
    description: JobDescriptionModel

    @field_serializer("task")
    def serialize_task(self, value):
        if isinstance(value, (CommandLineTool, Workflow)):
            return save(value)
        else:
            raise TypeError(f"Cannot serialize type {type(value)}")
