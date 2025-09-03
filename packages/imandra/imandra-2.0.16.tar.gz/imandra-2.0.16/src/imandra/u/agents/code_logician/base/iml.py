from __future__ import annotations

from pydantic import BaseModel, Field
from rich.table import Table
from rich.text import Text

from .imandrax import InferredType

Loc = tuple[int, int]


class IMLCode(BaseModel):
    iml_code: str = Field(description="IML code", strict=True)


class IMLSymbol(InferredType):
    opaque: bool

    @staticmethod
    def render_list(
        iml_symbols: list[IMLSymbol], limit: int | None = None
    ) -> tuple[Text, Table]:
        header = Text(f"\nIML Symbols ({len(iml_symbols)}):", style="bold")
        table = Table(show_header=False, box=None, padding=(0, 1))
        for i, sym in enumerate(iml_symbols[:10], 1):
            opaque_marker = (
                "[bright_red]●[/bright_red]"
                if sym.opaque
                else "[bright_green]●[/bright_green]"
            )
            table.add_row(f"{i}.", f"{opaque_marker} {sym.name}")
        if len(iml_symbols) > 10:
            table.add_row("...", f"[dim]({len(iml_symbols) - 10} more)[/dim]")
        return header, table


class Opaqueness(BaseModel):
    """Existence of opaque function and its possible solutions"""

    opaque_func: str = Field(description="The opaque function")
    assumptions: list[str] = Field(
        [],
        description=(
            "Assumptions about the opaque function. Each assumption is an axiom. "
            "For example, `axiom boo x = f x > 0`"
        ),
    )
    approximation: str | None = Field(
        None, description="An approximation of the opaque function"
    )
    assumption_candidates: list[str] = Field([], description="Assumption candidates")
    approximation_candidates: list[str] = Field(
        [], description="Approximation candidates"
    )

    @staticmethod
    def render_list(
        opaques: list[Opaqueness], limit: int | None = None
    ) -> tuple[Text, Table]:
        header = Text(f"Opaque Functions ({len(opaques)}):", style="bold")
        table = Table(show_header=False, box=None, padding=(0, 1))
        for i, opa in enumerate(opaques[:limit], 1):
            num_assumptions = len(opa.assumptions)
            has_approx = opa.approximation is not None
            status_icon = (
                "[bright_green]✓[/bright_green]"
                if has_approx
                else "[bright_yellow]○[/bright_yellow]"
            )
            table.add_row(
                f"{i}.",
                f"{status_icon} {opa.opaque_func}",
                f"({num_assumptions} assumptions)",
            )
        if limit is not None and len(opaques) > limit:
            table.add_row("...", f"[dim]({len(opaques) - limit} more)[/dim]", "")

        return header, table
