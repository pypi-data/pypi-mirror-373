import json

from langchain_core.runnables.config import RunnableConfig

from imandra.u.agents import get_remote_graph

from .graph import (
    AutomaticWorkflowCommand,
    EndResult,
    GenerateFormalSpecCommand,
    GetIplSpec,
    GetNLSpec,
    GetOpaqueFunctions,
    GetPprintedFormalSpec,
    GetUserInstructions,
    GetValidationResult,
    GraphState,
    InitStateCommand,
    SetFormalSpecCommand,
    SetSourceSpecCommand,
    SetUserInstructions,
    SubmitFnImplementation,
    SyncFormalCommand,
    SyncSourceCommand,
    UserCommand,
    ValidateFormalSpec,
)


class Client:
    def __init__(self, api_key, host=None):
        graph = get_remote_graph(
            "spec_logician",
            api_key=api_key,
            host=host,
        )

        if graph.sync_client is not None:
            thread = graph.sync_client.threads.create()
        else:
            raise ValueError("Failed to create new remote graph thread")

        self.graph = graph
        self.thread = thread

    async def get_graph_state(self) -> GraphState:
        if self.graph.client is not None:
            thread_state = await self.graph.client.threads.get_state(
                self.thread["thread_id"]
            )
            gs = GraphState.model_validate(thread_state["values"])
            return gs
        else:
            raise ValueError("Failed to retrieve thread state: graph client is not set")

    async def call_command(self, cmd: UserCommand) -> EndResult:
        config = {"configurable": {"thread_id": self.thread["thread_id"]}}
        state = await self.get_graph_state()
        gs_with_cmd = state.model_copy(update={"command": cmd})
        gs_raw = await self.graph.ainvoke(gs_with_cmd, config=RunnableConfig(**config))
        gs = GraphState.model_validate(gs_raw)
        return gs.end_result

    async def init_state(self, src_spec: str):
        """
        Initialize the formalization state with a natural language spec.
        """
        cmd = InitStateCommand(src_spec=src_spec)
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def set_source_spec(self, src_spec: str):
        """
        Manually update the natural language spec in the formalization state.
        """
        cmd = SetSourceSpecCommand(src_spec=src_spec)
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def set_formal_spec(self, formal_spec: str):
        """
        Manually update the FormalSpec source in the formalization state.
        The formal spec argument passed to this function must be a valid
        FormalSpec document in its pretty-printed form.
        """
        cmd = SetFormalSpecCommand(formal_spec=formal_spec)
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def generate_formal_spec(self):
        """
        Translate the current natural language spec into a formal specification,
        using the FormalSpec DSL.

        This function takes into account previous formalization attempts and
        validation results, using them as references to guide new formalizations.

        """
        cmd = GenerateFormalSpecCommand()
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def validate_formal_spec(self):
        """
        Validate the current FormalSpec source.

        This function destructively updates the formalization state with the
        validation results. The results can be fetched via the
        `get_validation_result` tool.
        """
        cmd = ValidateFormalSpec()
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def automatic_workflow(self):
        """
        Run a fully automatic agentic workflow that translates the current natural
        language spec into a formal specification, using the FormalSpec DSL.

        This function takes into account previous formalization attempts and
        validation results, using them as references to guide new formalizations.

        Generated FormalSpec sources are automatically validated, and in case of
        errors, formalization is retried (up to 3 total attempts) using the
        validation results as feedback to refine the process.

        The automatic workflow comprises the following two individual tool calls:

        - `generate_formal_spec`
        - `validate_formal_spec`

        These two steps are executed in a loop until:
        - a valid formal spec is found, or
        - no valid formalization is found after 3 loop repetitions, at which point
          the tool returns with an error message, updating the formalization state
          with the last formalization attempt and its validation results.

        """
        cmd = AutomaticWorkflowCommand()
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def sync_nl_spec(self):
        """
        Use the most recent FormalSpec, and the latest known FormalSpec directly
        generated from the natural language spec, to update the natural language
        spec in a way that reflects the edits to the formal spec.

        This function is useful in the case where the natural language spec is
        formalized into a FormalSpec document, but the user subsequently modifies
        the FormalSpec directly, thus leaving the two out of sync.
        """
        cmd = SyncSourceCommand()
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def sync_formal(self):
        """
        Use the most recent natural language spec, and the latest known natural
        language spec used to generate the current formal spec, to update the
        formal spec in a way that reflects the edits to the natural language spec.

        This function is useful in the case where the natural language spec is
        formalized into a FormalSpec document, but the user subsequently modifies
        the natural language spec directly, thus leaving the two out of sync.

        This function behaves like `generate_formal_spec`, except that it is a
        no-op if there is no difference between the most recent natural language
        spec and the latest known natural language spec used to generate the
        current formal spec.
        """
        cmd = SyncFormalCommand()
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def get_nl_spec(self) -> str:
        """
        Get the current version of the natural language spec.
        """
        cmd = GetNLSpec()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return result.info

    async def get_pprinted_formal_spec(self) -> str:
        """
        Get the current, most recent version of the formal spec, in its
        human-readable, pretty-printed form.
        """
        cmd = GetPprintedFormalSpec()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return result.info

    async def get_ipl_spec(self) -> str:
        """
        Take the current version of the formal spec, and compile it to a formal
        state-machine representation, expressed in Imandra Protocol Language.
        """
        cmd = GetIplSpec()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return result.info

    async def get_validation_result(self) -> list[str]:
        """
        Get the results of validating the current, most recent version of the
        formal spec. The function fails if `validate_formal_spec` hasn't been run
        yet for the current formal spec.
        """
        cmd = GetValidationResult()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return json.loads(result.info)

    async def get_opaque_functions(self) -> list[str]:
        """
        Get a list of all opaque functions in the current formal spec.
        Opaque functions are given by their signature, which includes their name,
        list of parameters, and return type.
        """
        cmd = GetOpaqueFunctions()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return json.loads(result.info)

    async def submit_fn_implementation(self, fn_name: str, fn_statements: list[str]):
        """
        Manually set the implementation of a custom function definition in the
        current formal spec. The function's implementation must be given as a list
        of IPL statements.
        """
        cmd = SubmitFnImplementation(name=fn_name, statements=fn_statements)
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)

    async def get_user_instructions(self) -> list[str]:
        """
        Get the list of user-provided instructions in the formalization state.
        """
        cmd = GetUserInstructions()
        result = await self.call_command(cmd)
        if result.result != "success" or result.info is None:
            raise ValueError(result.info)
        return json.loads(result.info)

    async def set_user_instructions(self, instructions: list[str]):
        """
        Set the list of user-provided instructions in the formalization state.
        The instructions list currently present in the state is overwritten by the
        list provided as argument.
        """
        cmd = SetUserInstructions(instructions=instructions)
        result = await self.call_command(cmd)
        if result.result != "success":
            raise ValueError(result.info)
