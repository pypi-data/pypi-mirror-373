from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Self

import structlog
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.remote import RemoteGraph
from langgraph.types import Command as LGCommand
from pydantic import BaseModel, Field, field_validator
from rich.console import ConsoleRenderable

from ..base import (
    FormalizationState,
)
from ..command import (
    Command,
    InitStateCommand,
    RootCommand,
)
from ..task import Interaction

logger = structlog.get_logger(__name__)


class GraphState(BaseModel):
    """
    Graph state of Code Logician
    """

    steps: list[Interaction] = Field([], description="Commands and their trajectories")
    step_i: int | None = Field(None, description="Index of the current step")
    info: dict = Field({}, description="Internal information shared between nodes")

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state"""
        last_fstate = None
        for step in self.steps:
            if step.last_fstate is not None:
                last_fstate = step.last_fstate
        return last_fstate

    @field_validator("steps", mode="after")
    @classmethod
    def last_fstate_cannot_be_later_than_the_first_pending_step(
        cls, steps: list[Interaction]
    ) -> list[Interaction]:
        step_i = next(
            (
                i
                for i, step in enumerate(steps)
                if step.task is not None and step.task.status == "pending"
            ),
            None,
        )
        if step_i is None:
            return steps

        for step in steps[step_i + 1 :]:
            if step.last_fstate is not None:
                raise ValueError(
                    "Last fstate cannot be later than the first pending step"
                )
        return steps

    def add_commands(
        self,
        commands: Command | list[Command],
    ) -> Self:
        """Return a new GraphState with the added commands"""
        match commands:
            case command if isinstance(command, Command):
                new_steps = [
                    *self.steps,
                    Interaction(command=command),
                ]
                update = {"steps": new_steps}
            case list() as commands:
                new_steps = [
                    *self.steps,
                    *[Interaction(command=command) for command in commands],
                ]
                update = {"steps": new_steps}
            case _:
                raise ValueError(f"Invalid command: {commands}")

        gs = GraphState.model_validate(self.model_dump() | update)
        return GraphState.model_validate_json(gs.model_dump_json())

    def init_with_file(self, file_path: str, src_lang: str) -> GraphState:
        content = Path(file_path).read_text()
        steps = [
            Interaction(
                command=RootCommand(
                    root=InitStateCommand(
                        src_code=content,
                        src_lang=src_lang,
                    )
                )
            )
        ]
        return GraphState(steps=steps)

    async def run(
        self,
        graph: CompiledStateGraph | RemoteGraph,
        config: dict | RunnableConfig | None = None,
        resume: LGCommand | None = None,
    ) -> tuple[Self, dict | None]:
        config = RunnableConfig(**(config or {}))
        inputs = resume or self
        async for chunk in graph.astream(
            inputs, config, stream_mode=["values", "updates"]
        ):
            chunk_type, chunk_value = chunk
            if chunk_type == "values":
                values = chunk_value
            elif chunk_type == "updates":
                updates = chunk_value
        gs = GraphState.model_validate(values)
        if "__interrupt__" in updates:
            return (gs, updates)
        else:
            return (gs, None)

    def __rich__(self) -> ConsoleRenderable:
        return Interaction.render_interactions_summary(self.steps)

    def __repr__(self):
        s = ""
        s += "Graph State:\n\n"
        s += f"{len(self.steps)} Steps\n\n"
        for i, step in enumerate(self.steps, 1):
            s += f"Step {i}:\n\n"
            s += textwrap.indent(step.__repr__(), "  ")
            s += "\n\n"
            s += "=" * 40 + "\n\n"

        return s
