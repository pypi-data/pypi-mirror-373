from __future__ import annotations

import textwrap
from datetime import UTC, datetime
from typing import Literal, Self

from pydantic import BaseModel, Field
from rich.align import Align
from rich.console import ConsoleRenderable, Group
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

from .base import FormalizationState
from .command import RootCommand
from .interrupt_message import InterruptMessage


class Formalization(BaseModel):
    """Represents a single step in the formalization process.

    Each step captures the action taken, the resulting state, and when it occurred.
    """

    action: str = Field(description="Name of the action")
    fstate: FormalizationState = Field(description="Formalization state")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 datetime string when recorded.",
    )

    @property
    def time_str(self) -> str:
        return datetime.fromisoformat(self.timestamp).strftime("%m-%d %H:%M:%S")

    @staticmethod
    def render_trajectory_summary(
        formalizations: list[Formalization],
    ) -> ConsoleRenderable:
        table = Table(title="Summary of Formalizations")
        table.add_column("#", width=2)
        table.add_column("Action", width=25)
        table.add_column("Status", width=15)
        table.add_column("Time", width=20)
        for i, f in enumerate(formalizations, 1):
            table.add_row(
                str(i),
                f.action,
                f.fstate.status.__rich__(),
                f.time_str,
            )
        return table

    @staticmethod
    def render_trajectory(formalizations: list[Formalization]) -> ConsoleRenderable:
        content_parts = []
        for i, f in enumerate(formalizations, 1):
            content_parts.extend(
                [
                    Text(f"Step {i}: ", "bold"),
                    f.__rich__(),
                    "\n",
                ]
            )
        return Panel(Group(*content_parts), title="Formalizations")

    def __rich__(self) -> Panel:
        content_parts = []

        action_str = Text.assemble(
            ("Action: ", "bold"),
            (self.action),
            ("\n"),
        )
        time_str = Text.assemble(
            ("Time: ", "bold"),
            (self.time_str),
            ("\n"),
        )
        content_parts.extend([action_str, time_str])

        fs_panel = self.fstate.__rich__()
        fs_renderables = [
            Text("Formalization State: ", "bold"),
            fs_panel,
        ]
        content_parts.extend(fs_renderables)
        return Panel(Group(*content_parts), title="Formalization")

    def __repr__(self) -> str:
        s = ""
        s += f"Action: {self.action}\n"
        s += f"Time: {self.time_str}\n"
        s += "F-state: \n"
        s += textwrap.indent(self.fstate.__repr__(), "  ")
        return s


class PrecheckFailure(BaseModel):
    """Represents a failure during pre-execution checks.

    Used to capture validation failures before executing a command.
    """

    field: str = Field(..., description="Field name")
    reason: str = Field(..., description="Reason for the error")
    message: str | None = Field(None, description="Message to the user")

    def __rich__(self) -> Pretty:
        return Pretty(self)


class FormalizationTask(BaseModel):
    formalizations: list[Formalization] = Field(
        description="Trajectory of formalization steps"
    )
    status: Literal[
        "precheck_failed",
        "pending",
        "done",
        "error",
        "hitl_waiting",
        "hitl_done",
    ] = Field(description="Status of the task")
    precheck_failures: list[PrecheckFailure] = Field(
        [],
        description="Precheck failures",
    )
    hitl_qas: list[list[InterruptMessage]] = Field(
        [],
        description="Interrupt messages used for `interrupt`",
    )
    metadata: dict = Field(
        {},
        description="Metadata about the task",
    )

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state, or None if there is no trajectory"""
        match self.formalizations:
            case []:
                return None
            case [*_, last_f]:
                return last_f.fstate
            case _:
                raise ValueError(
                    f"Invalid formalization trajectory: {self.formalizations}"
                )

    def extend_traj(self, action: str, fstate: FormalizationState) -> Self:
        """Extend the trajectory with a new formalization step"""
        return self.model_copy(
            update={
                "fstep_trajectory": [
                    *self.formalizations,
                    Formalization(action=action, fstate=fstate),
                ],
            }
        )

    def render_status(self) -> Text:
        status_colors = {
            "precheck_failed": "bright_red",
            "pending": "bright_yellow",
            "done": "bright_green",
            "error": "bright_red",
            "hil_waiting": "bright_cyan",
            "hil_done": "bright_blue",
        }
        status_color = status_colors.get(self.status, "white")
        return Text(self.status.upper(), status_color)

    def __rich__(self) -> ConsoleRenderable:
        summary_parts = []

        status_str = Text("Status: ", "bold") + self.render_status()
        summary_parts.append(status_str)

        if self.precheck_failures:
            precheck_parts = []
            precheck_parts.append(
                Text(
                    f"\nPrecheck Failures ({len(self.precheck_failures)}):",
                    style="bold bright_red",
                )
            )
            for failure in self.precheck_failures:
                precheck_parts.append(failure.__rich__())
            summary_parts.extend(precheck_parts)

        traj_summary = Formalization.render_trajectory_summary(self.formalizations)
        summary_parts.append(traj_summary)

        if self.hitl_qas:
            hitl_parts = []
            hitl_parts.append(
                Text.assemble(
                    ("Human-in-the-Loop Interactions: ", "bold"),
                    (str(len(self.hitl_qas)), "bright_cyan"),
                )
            )
            summary_parts.extend(hitl_parts)

        if self.metadata:
            summary_parts.extend(
                [
                    Text("Metadata: ", "bold"),
                    Pretty(self.metadata),
                ]
            )

        panel = Panel(
            Group(*summary_parts),
            title="Formalization Task",
        )

        return panel


class Interaction(BaseModel):
    """Represents a complete user-initiated step in the formalization process.

    Contains the command to execute, the trajectory of formalization states,
    and metadata about the step's execution.
    """

    command: RootCommand = Field(description="User command")
    message: dict | None = Field(
        None, description="Non-formalization state information"
    )
    task: FormalizationTask | None = Field(None, description="Formalization task")

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state, or None if there is no trajectory"""
        ftask = self.task
        match ftask:
            case None:
                return None
            case FormalizationTask(formalizations=[]):
                return None
            case FormalizationTask(formalizations=formalizations):
                return formalizations[-1].fstate
            case _:
                raise ValueError(f"Invalid task: {ftask}")

    @property
    def response_type(self) -> str:
        if self.task is None and self.message is None:
            return "Pending"
        elif self.task is not None:
            return "Task"
        else:
            return "Message"

    @staticmethod
    def render_interactions_summary(
        interactions: list[Interaction],
    ) -> ConsoleRenderable:
        table = Table(title="Summary of Interactions")
        table.add_column("#", width=2)
        table.add_column("Command")
        table.add_column("Response")
        for i, interaction in enumerate(interactions, 1):
            response_type = interaction.response_type
            response_str = Text.assemble(
                (f"{response_type}", "bold"),
            )
            if response_type == "Task":
                response_str += Text.assemble(
                    (" ("),
                    (interaction.task.render_status()),
                    (")"),
                )

            table.add_row(
                str(i),
                interaction.command.__rich__(),
                Align.center(response_str, vertical="middle"),
            )
        return table

    def __rich__(self) -> ConsoleRenderable:
        parts = []
        parts.append(self.command.__rich__())

        response_type = self.response_type
        parts.append(Text(f"Response: {response_type}", style="bold"))
        if response_type == "Task":
            response_content = Panel(
                Group(
                    self.task.__rich__(),
                ),
            )
            parts.append(response_content)
        elif response_type == "Message":
            response_content = Panel(
                Group(
                    Pretty(self.message),
                ),
            )
            parts.append(response_content)

        panel = Panel(
            Group(*parts),
            title="Interaction",
        )

        return panel
