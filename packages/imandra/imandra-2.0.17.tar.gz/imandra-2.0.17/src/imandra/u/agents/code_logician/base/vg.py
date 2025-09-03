from typing import Literal, Self

from pydantic import BaseModel, Field
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .. import rich_utils
from .imandrax import Error, ErrorKind, ErrorMessage, VerifyRes


class RawVerifyReq(BaseModel):
    """
    A formal specification of a property / logical statement, clause, predicate,
    or condition to verify about functions in the source code.

    Each verification pairs a natural language description with a corresponding logical
    statement that will be later used in tasks related to property-based testing and
    formal verification.
    The description is human-readable, while the logical statement is more precise,
    mathematically formal.
    """

    src_func_names: list[str] = Field(
        title="Src func names",
        description="names of the functions (including class methods) involved "
        "in the verification",
    )
    iml_func_names: list[str] = Field(
        title="IML func names",
        description="names of the corresponding functions in IML",
    )
    description: str = Field(
        title="Description",
        description="Human-readable description of the property to verify. Should "
        "clearly explain what aspect of the function's behavior is being checked. "
        "Example: 'The function always returns a value greater than or equal to 10' or "
        "'The output array is always sorted in ascending order'",
    )
    logical_statement: str = Field(
        title="Logical statement",
        description="Logical statement expressing the property in a precise way. "
        "Can use plain English with logical terms like 'for all', 'there exists', "
        "'and', 'or', etc. Example: 'for all inputs x, f(x) is greater than or equal "
        "to 10' or 'for all indices i from 0 to n-2, array[i] is less than or equal "
        "to array[i+1]'",
    )

    def render_content(self) -> list[Text]:
        return [
            Text(f"Src func names: {', '.join(self.src_func_names)}"),
            Text(f"IML func names: {', '.join(self.iml_func_names)}"),
            Text(f"Description: {self.description}"),
            Text(f"Logical statement: {self.logical_statement}"),
        ]

    def __rich__(self) -> Text:
        title_t = Text("RawVerifyReq", style="bold")
        t = Text()
        t.append(title_t)
        t.append("\n")

        for item in self.render_content():
            t.append(rich_utils.left_pad(item, 2))
            t.append("\n")
        return t

    def __repr__(self):
        return self.__rich__().plain


class VerifyReqData(BaseModel):
    """Verify"""

    predicate: str = Field(
        title="Predicate",
        description="IML code representing some logical statement using lambda"
        "functions. Eg. `fun x -> x >= 10`, `fun x -> f x <> 98`. Backticks should"
        "be omitted.",
    )
    kind: Literal["verify", "instance"] = Field(
        title="Kind",
        description="""Kind of reasoning request.
        - `verify` checks that the given predicate is always true (universal)
        - `instance` finds an example where the predicate is true (existential)
        """,
    )

    def to_iml(self) -> str:
        return f"${self.kind} ({self.predicate})"

    def to_negation(self) -> Self:
        """Negate the predicate"""

        predicate = self.predicate
        arrow_idx = predicate.index("->")
        dom = predicate[:arrow_idx]
        cod = predicate[arrow_idx + 2 :]
        neg_cod = f"not ({cod.strip()})"
        neg_predicate = f"{dom}-> {neg_cod}"
        if self.kind == "verify":
            kind = "instance"
        else:
            kind = "verify"
        return self.__class__(predicate=neg_predicate, kind=kind)

    def render_content(self) -> list[Text]:
        return [
            Text(f"Predicate: {self.predicate}"),
            Text(f"Kind: {self.kind}"),
            Text(f"IML: {self.to_iml()}", style="dim"),
        ]

    def __rich__(self) -> Text:
        t = Text()
        t.append(Text("VerifyReqData", style="bold"))
        for item in self.render_content():
            t.append(rich_utils.left_pad(item, 2))
            t.append("\n")
        return t

    def __repr__(self):
        return self.__rich__().plain


def render_error_table(errors: list[Error], title: str | None = None) -> Table:
    error_table = Table(title=title or "Errors")
    error_table.add_column("#")
    error_table.add_column("Kind")
    error_table.add_column("Message")
    error_table.add_column("Process")

    for i, error in enumerate(errors, 1):
        match error.msg:
            case ErrorMessage(msg=msg):
                if len(msg) > 200:
                    msg = msg[:197] + "..."
                msg = msg.replace("\n", "  ")
            case None:
                msg = "None"

        kind = ErrorKind.from_proto_kind(error.kind)

        error_table.add_row(
            str(i),
            kind.value,
            msg,
            error.process or "None",
        )

    return error_table


def render_verify_res_content(res: VerifyRes) -> list[Text]:
    res_parts = []

    # VerifyRes.res
    res_type = res.res_type
    if res_type == "proved":
        res_parts.append(Text("✓ PROVED", style="green"))
    else:
        res_parts.append(Text(f"✗ {res_type.upper()}", style="red"))
    res_res = res.res
    if res_res is not None:
        res_res = next(iter(res_res.model_dump().values()))
    else:
        res_res = "None"
    res_res_details = Text(res_res)
    res_res_details = rich_utils.left_pad(res_res_details, 2)
    res_parts.append(res_res_details)

    # VerifyRes.errors
    if len(res.errors) > 0:
        res_parts.append(Text("\nErrors:", style="red"))
        error_table = render_error_table(res.errors, title="Verification Errors")
        res_parts.append(error_table)

    # VerifyRes.task
    # if res.task:
    #     res_parts.append(Text(f"\nTask ID: {res.task.id.id}", style="dim"))
    #     res_parts.append(Text(f"Task Kind: {res.task.kind.value}", style="dim"))
    return res_parts


class VG(BaseModel):
    """
    A verification goal
    """

    raw: RawVerifyReq
    data: VerifyReqData | None = Field(None)
    res: VerifyRes | None = Field(None)

    def __rich__(self) -> Panel:
        """Rich display for the entire VG."""
        content_parts = []

        # Add raw request info
        raw_req_parts = self.raw.render_content()
        content_parts.append(Panel(Group(*raw_req_parts), title="Raw Request"))

        if self.data:
            data_group = self.data.render_content()
            content_parts.append(Panel(Group(*data_group), title="Request Data"))

        if self.res:
            res_parts = render_verify_res_content(self.res)
            content_parts.append(Panel(Group(*res_parts), title="Verification Result"))

        return Panel(Group(*content_parts), title="Verification Goal")

    def __repr__(self):
        return rich_utils.get_str(self.__rich__())
