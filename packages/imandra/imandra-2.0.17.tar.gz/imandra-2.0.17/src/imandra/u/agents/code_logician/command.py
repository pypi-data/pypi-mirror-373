import textwrap
from typing import Any, Literal

from pydantic import BaseModel, Field, RootModel
from rich.console import ConsoleRenderable, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class BaseCommand(BaseModel):
    """Base class for all individual commands with custom __repr__"""

    def __rich__(self) -> ConsoleRenderable:
        max_width = 40

        cmd_name = self.type
        args = self.model_dump(exclude={"type"})

        content_parts = []

        content_parts.append(Text(f"Command: {cmd_name}", style="bold"))

        if args:
            content_parts.append(Text("Parameters:", style="bold"))
            args_table = Table(show_header=False, box=None, padding=(0, 1))

            for key, value in args.items():
                if isinstance(value, str) and len(value) > max_width - 3:
                    display_value = (
                        value[: max_width - 3] + "..."
                        if len(value) > max_width - 3
                        else value
                    )
                elif isinstance(value, list | dict):
                    if isinstance(value, list):
                        display_value = f"[{len(value)} items]" if value else "[]"
                    else:
                        display_value = f"{{{len(value)} keys}}" if value else "{}"
                elif isinstance(value, bool):
                    display_value = (
                        f"[bright_green]{value}[/bright_green]"
                        if value
                        else f"[bright_red]{value}[/bright_red]"
                    )
                else:
                    display_value = str(value)

                args_table.add_row(f"[dim]{key}:[/dim]", display_value)
            content_parts.append(args_table)
        else:
            content_parts.append(Text("\nNo parameters", "dim"))

        content_group = Group(*content_parts)
        panel = Panel(
            content_group,
            title="Command",
        )
        return panel


class InitStateCommand(BaseCommand, extra="forbid"):
    """
    Initialize the formalization state. Formalization status will be initialized to
    `UNKNOWN`.

    Updates `src_code`, `src_lang` in the formalization state.
    """

    type: Literal["init_state"] = "init_state"
    src_code: str = Field(description="Source program to formalize")
    src_lang: str = Field(description="Source language")


class GetStateElementCommand(BaseCommand, extra="forbid"):
    """
    Get a state element from the formalization state.

    The following elements are supported:
    - `status`
    - `src_code`
    - `src_lang`
    - `refactored_code`
    - `conversion_source_info`
    - `conversion_failures_info`
    - `iml_code`
    - `iml_symbols`
    - `opaques`
    - `vgs`
    - `region_decomps`
    - `test_cases`
    Will not change the formalization state.
    """

    type: Literal["get_state_element"] = "get_state_element"
    element_names: list[str] = Field(
        description="Name(s) of the state element(s) to get"
    )


class EditStateElementCommand(BaseCommand, extra="forbid"):
    """
    Edit a state element in the formalization state.
    """

    type: Literal["edit_state_element"] = "edit_state_element"

    update: dict[str, Any] = Field(
        description=(
            "Updating dictionary to the formalization state, "
            "key-value pairs of field names and values"
        )
    )


class SearchFDBCommand(BaseCommand, extra="forbid"):
    """
    Search the FDB for a table and query.
    """

    type: Literal["search_fdb"] = "search_fdb"
    name: Literal[
        "missing_functions",
        "iml_code_by_iml_code",
        "formalization_examples_by_src_lang",
        "formalization_examples_by_src_code",
        "iml_api_reference_by_pattern",
        "iml_api_reference_by_src_code",
        "error_suggestion_by_error_msg",
    ] = Field(description="Name of the table to search")
    query: str | tuple[str, str] | None = Field(
        description=(
            textwrap.dedent(
                """
                Query to search the table.
                - Not required for `missing_functions`
                - For `formalization_examples_by_src_code`, the query is a tuple of
                (source language, source code)
                - For `iml_api_reference_by_src_code`, the query is a tuple of
                (source language, source code)
                - Otherwise, the query is a string
                """
            )
        )
    )
    top_k: int = Field(5, description="Number of results to return")


class CheckFormalizationCommand(BaseCommand, extra="forbid"):
    """
    Check if the source code contains any functions that are hard to formalize in IML.
    If so, relevant context will be retrieved from the FDB to help the later
    formalization.

    Updates `conversion_source_info.missing_funcs` in the formalization state.
    """

    type: Literal["check_formalization"] = "check_formalization"


class GenProgramRefactorCommand(BaseCommand, extra="forbid"):
    """
    Refactor the source code to make it easier to formalize in IML.

    Updates `refactored_code` in the formalization state.
    """

    type: Literal["gen_program_refactor"] = "gen_program_refactor"


class GenFormalizationDataCommand(BaseCommand, extra="forbid"):
    """
    Based on the source code, retrieve relevant information from the FDB as context
    for formalization. Must be called before `gen_model`.

    Updates `conversion_source_info` in the formalization state.
    """

    type: Literal["gen_formalization_data"] = "gen_formalization_data"


class InjectFormalizationContextCommand(BaseCommand, extra="forbid"):
    """
    Inject additional context that is relevant to the formalization.

    Updates `conversion_source_info.user_inject` in the formalization state.
    """

    type: Literal["inject_formalization_context"] = "inject_formalization_context"
    context: str = Field(description="Additional context for formalization")


class InjectCustomExamplesCommand(BaseCommand, extra="forbid"):
    """
    Inject custom examples for formalization.
    """

    type: Literal["inject_custom_examples"] = "inject_custom_examples"
    examples: list[tuple[str, str]] = Field(
        description=(
            "Examples of source code and corresponding IML code in the form of tuples"
        )
    )


class GenFormalizationFailureDataCommand(BaseCommand, extra="forbid"):
    """
    Based on the formalization failure, retrieve relevant information from the FDB as
    context for re-try formalization.

    Retrieved information will be appended to `conversion_failures_info` in the
    formalization state.
    """

    type: Literal["gen_formalization_failure_data"] = "gen_formalization_failure_data"


class AdmitModelCommand(BaseCommand, extra="forbid"):
    """
    Admit the current IML model and see if there's any error.

    Updates `eval_res` in the formalization state.
    """

    type: Literal["admit_model"] = "admit_model"


class GenModelCommand(BaseCommand, extra="forbid"):
    """
    Generate IML code based on source program and retrieved context.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    type: Literal["gen_model"] = "gen_model"


class SetModelCommand(BaseCommand, extra="forbid"):
    """
    Set the IML model and admit it to see if there's any error.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    type: Literal["set_model"] = "set_model"
    model: str = Field(description="new IML model to use")


class GenVgsCommand(BaseCommand, extra="forbid"):
    """
    Generate verification goals on the source code and its corresponding IML model. Then
    use ImandraX to verify the VGs.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `vgs` in the formalization state.
    """

    type: Literal["gen_vgs"] = "gen_vgs"
    description: str | None = Field(
        None,
        description=(
            "Description of the VGs to generate. If not provided, CodeLogician will "
            "seek verification goal requests from the comments in the source code."
        ),
    )


class GenRegionDecompsCommand(BaseCommand, extra="forbid"):
    """
    Generate region decompositions.

    If `function_name` is provided, the region decompositions will be generated for the
    specific function. Otherwise, CodeLogician will seek region decomposition requests
    from the comments in the source code.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `region_decomps` in the formalization state.

    After successful execution, you can either:
    - See the region decomposition results using `get_state_element` with
        `region_decomps`
    - Generate test cases for this specific region decomposition using `gen_test_cases`
    """

    type: Literal["gen_region_decomps"] = "gen_region_decomps"
    function_name: str | None = Field(
        None,
        description="Name of the function to decompose",
    )


class GenTestCasesCommand(BaseCommand, extra="forbid"):
    """
    Use a specific region decomposition to generate test cases for a specific function
    in the source code.

    Updates `region_decomps[decomp_idx].test_cases` in the formalization state.

    After successful execution, you can:
    - See the test cases using `get_state_element` with `["test_cases"]`
    """

    type: Literal["gen_test_cases"] = "gen_test_cases"
    decomp_idx: int = Field(
        description="Index of the region decomposition to generate test cases for"
    )


class SyncSourceCommand(BaseCommand, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the source code.

    Updates `src_code` in the formalization state.
    """

    type: Literal["sync_source"] = "sync_source"


class SyncModelCommand(BaseCommand, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the IML code.

    Updates `iml_code` in the formalization state.
    """

    type: Literal["sync_model"] = "sync_model"


class AgentFormalizerCommand(BaseCommand, extra="forbid"):
    """
    Use the agentic workflow to formalize the source code. This is roughly equivalent to
    the following steps:
    1. check if the source code is within the scope of Imandra's capability
    (CheckFormalizationCommand)
    2. refactor the source code to make it easier to formalize in IML
    (GenProgramRefactorCommand)
    3. retrieve relevant information from the FDB based on the source code
    (GenFormalizationDataCommand)
    4. generate IML code based on the source code and retrieved context
    (GenModelCommand)
    5. admit the IML code and see if there's any error (AdmitModelCommand)
    6. If the IML code is not admissible, retrieve relevant information from the FDB
    based on the error message (GenFormalizationFailureDataCommand)
    7. repeat 4-6 until the IML code is admissible or the number of tries is exhausted

    Some steps can be skipped by setting the corresponding flags.

    Relevant fields in the formalization state:
    - `refactored_code`, `conversion_source_info`, `conversion_failures_info`?,
    `iml_code`, `eval_res`, `iml_symbols`, `opaques`, `status`
    """

    type: Literal["agent_formalizer"] = "agent_formalizer"
    no_check_formalization_hitl: bool = Field(
        False,
        description="Whether to skip HITL in check_formalization",
    )
    no_refactor: bool = Field(
        False,
        description="Whether to skip refactoring",
    )
    no_gen_model_hitl: bool = Field(
        False,
        description="Whether to skip HITL in gen_model",
    )
    max_tries_wo_hitl: int = Field(
        2,
        description=(
            "Maximum number of tries for the formalizer agent without human-in-the-loop"
        ),
    )
    max_tries: int = Field(
        3,
        description="Maximum number of tries for the formalizer agent",
    )


class SuggestFormalizationActionCommand(BaseCommand, extra="forbid"):
    """
    Upon a formalization failure, provide information by populating the `human_hint`
    field of the latest `conversion_failures_info` in the formalization state, which
    will be taken into account by the next formalization attempt (either GenModelCommand
    or AgentFormalizerCommand).
    """

    type: Literal["suggest_formalization_action"] = "suggest_formalization_action"
    feedback: str = Field(
        description="Feedback on the formalization failure",
    )


class SuggestAssumptionsCommand(BaseCommand, extra="forbid"):
    """
    Suggest assumptions for a specific opaque function.

    Updates `opaques[i].assumptions` in the formalization state.
    """

    type: Literal["suggest_assumptions"] = "suggest_assumptions"
    feedback: str = Field()


class SuggestApproximationCommand(BaseCommand, extra="forbid"):
    """
    Suggest an approximation for a specific opaque function.

    Updates `opaques[i].approximation` in the formalization state.
    """

    type: Literal["suggest_approximation"] = "suggest_approximation"
    feedback: str = Field()


IndividualCommand = (
    InitStateCommand
    | GetStateElementCommand
    | EditStateElementCommand
    | SearchFDBCommand
    | CheckFormalizationCommand
    | GenProgramRefactorCommand
    | GenFormalizationDataCommand
    | InjectFormalizationContextCommand
    | InjectCustomExamplesCommand
    | GenFormalizationFailureDataCommand
    | AdmitModelCommand
    | GenModelCommand
    | SetModelCommand
    | GenVgsCommand
    | GenRegionDecompsCommand
    | GenTestCasesCommand
    | SyncSourceCommand
    | SyncModelCommand
    | AgentFormalizerCommand
    | SuggestFormalizationActionCommand
    | SuggestAssumptionsCommand
    | SuggestApproximationCommand
)


class RootCommand(RootModel):
    root: IndividualCommand = Field(discriminator="type")

    def __rich__(self) -> ConsoleRenderable:
        return self.root.__rich__()


Command = IndividualCommand | RootCommand
