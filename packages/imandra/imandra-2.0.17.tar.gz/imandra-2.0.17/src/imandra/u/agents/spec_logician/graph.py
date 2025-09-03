from typing import Literal

from pydantic import BaseModel, Field


class InitStateCommand(BaseModel):
    type: Literal["init_state"] = "init_state"
    src_spec: str


class GenerateFormalSpecCommand(BaseModel):
    type: Literal["generate_formal_spec"] = "generate_formal_spec"


class ValidateFormalSpec(BaseModel):
    type: Literal["validate_formal_spec"] = "validate_formal_spec"


class SetSourceSpecCommand(BaseModel, extra="forbid"):
    type: Literal["set_source_spec"] = "set_source_spec"
    src_spec: str


class SetFormalSpecCommand(BaseModel, extra="forbid"):
    type: Literal["set_formal_spec"] = "set_formal_spec"
    formal_spec: str


class AutomaticWorkflowCommand(BaseModel, extra="forbid"):
    type: Literal["automatic_workflow"] = "automatic_workflow"


class SyncSourceCommand(BaseModel, extra="forbid"):
    type: Literal["sync_source"] = "sync_source"


class SyncFormalCommand(BaseModel, extra="forbid"):
    type: Literal["sync_formal"] = "sync_formal"


class SubmitFnImplementation(BaseModel, extra="forbid"):
    type: Literal["submit_fn_implementation"] = "submit_fn_implementation"
    name: str
    statements: list[str]


class SetUserInstructions(BaseModel, extra="forbid"):
    type: Literal["add_user_instructions"] = "add_user_instructions"
    instructions: list[str]


class GetNLSpec(BaseModel, extra="forbid"):
    type: Literal["get_nl_spec"] = "get_nl_spec"


class GetPprintedFormalSpec(BaseModel, extra="forbid"):
    type: Literal["get_pprinted_formal_spec"] = "get_pprinted_formal_spec"


class GetIplSpec(BaseModel, extra="forbid"):
    type: Literal["get_ipl_spec"] = "get_ipl_spec"


class GetValidationResult(BaseModel, extra="forbid"):
    type: Literal["get_validation_result"] = "get_validation_result"


class GetOpaqueFunctions(BaseModel, extra="forbid"):
    type: Literal["get_opaque_functions"] = "get_opaque_functions"


class GetUserInstructions(BaseModel, extra="forbid"):
    type: Literal["get_user_instructions"] = "get_user_instructions"


UserCommand = (
    InitStateCommand
    | GenerateFormalSpecCommand
    | ValidateFormalSpec
    | SetSourceSpecCommand
    | SetFormalSpecCommand
    | AutomaticWorkflowCommand
    | SyncSourceCommand
    | SyncFormalCommand
    | SubmitFnImplementation
    | SetUserInstructions
    | GetNLSpec
    | GetPprintedFormalSpec
    | GetIplSpec
    | GetValidationResult
    | GetOpaqueFunctions
    | GetUserInstructions
)


class EndResult(BaseModel):
    """
    Fulfilled right before `__end__` node.
    """

    result: Literal["success", "failure", "abort"] = Field(
        description="Final result of agent calling"
    )
    info: str | None = Field(
        None, description="Additional information about the result"
    )


class GraphState(BaseModel):
    command: UserCommand | None = Field(None, description="User command to run")
    end_result: EndResult = Field(
        description="End result of the whole task.",
        default=EndResult(result="success", info=""),
    )
