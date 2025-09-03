import copy
from typing import Any

from pydantic import BaseModel, Field
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .. import rich_utils
from .imandrax import DecomposeRes


class RawDecomposeReq(BaseModel):
    """
    A function to decompose in source code and its corresponding function in IML.
    """

    description: str = Field(
        description="Human-readable description of the function to decompose"
    )
    src_func_name: str = Field(
        description="name of function to decompose in source code"
    )
    iml_func_name: str = Field(description="name of function to decompose in IML")


class DecomposeReqData(BaseModel):
    name: str
    assuming: list[str] | None = Field(None)
    basis: list[str] | None = Field(None)
    rule_specs: list[str] | None = Field(None)
    prune: bool | None = Field(True)
    ctx_simp: bool | None = Field(True)
    lift_bool: Any | None = Field(None)
    timeout: float | None = Field(None)
    str_: bool | None = Field(True)

    def render_content(self) -> Text:
        data = self.model_dump()
        data = {k: v for k, v in data.items() if v is not None}
        skip_keys = ["str_", "name"]
        data = {k: v for k, v in data.items() if k not in skip_keys}

        content_t = rich_utils.devtools_pformat(data, indent=0)
        content_ts = content_t.split("\n")[1:-1]

        t = rich_utils.join_texts(content_ts)
        return t

    def __rich__(self) -> Text:
        t = Text()
        t.append(Text("DecomposeReqData:", style="bold"))
        t.append("\n")
        t.append(rich_utils.left_pad(self.render_content(), 2))
        return t


class RegionDecomp(BaseModel):
    """
    A region decomposition
    """

    raw: RawDecomposeReq
    data: DecomposeReqData | None = Field(None)
    res: DecomposeRes | None = Field(None)

    test_cases: dict[str, list[dict]] | None = Field(
        None,
        examples=[
            {
                "iml": [
                    {"args": {"x": "1"}, "expected_output": "(-2)"},
                    {"args": {"x": "2"}, "expected_output": "4"},
                ],
                "src": [
                    {
                        "args": {"x": "1"},
                        "expected_output": "-2",
                        "docstr": (
                            "Constraints:\n    - `x <= 1`\nInvariant:\n    - `x - 3`\n"
                        ),
                    },
                    {
                        "args": {"x": "2"},
                        "expected_output": "4",
                        "docstr": (
                            "Constraints:\n    - `x >= 2`\nInvariant:\n    - `x + 2`\n"
                        ),
                    },
                ],
            }
        ],
    )

    @staticmethod
    @staticmethod
    def render_test_cases(test_cases: dict[str, list[dict]]) -> Table:
        test_cases = copy.deepcopy(test_cases)
        if "src" in test_cases:
            data = test_cases["src"]
        else:
            data = test_cases["iml"]

        if "docstr" in data[0]:
            for item in data:
                item.pop("docstr")

        def format_args(args_dict: dict) -> str:
            """Format args dictionary nicely: {'x': '1', 'y': '2'} -> 'x: 1, y: 2'"""
            if not args_dict:
                return ""

            formatted_pairs = []
            for key, value in args_dict.items():
                formatted_pairs.append(f"{key}: {value}")

            return ", ".join(formatted_pairs)

        table = Table(title="Test Cases")
        col_names = list(data[0].keys())

        def title_case(s: str) -> str:
            s = s.replace("_", " ")
            return s.title()

        col_names = [title_case(name) for name in col_names]
        col_names = ["", *col_names]
        for col_name in col_names:
            table.add_column(col_name)

        for i, item in enumerate(data, 1):
            row_values = []
            for key, value in item.items():
                if key == "args":
                    row_values.append(format_args(value))
                else:
                    row_values.append(str(value))
            table.add_row(str(i), *row_values)

        return table

    def render_content(self) -> list[Text]:
        ts = []
        ts.append(Text("RawDecomposeReq:", style="bold"))
        ts.append(Text(f"  Src func name: {self.raw.src_func_name}"))
        ts.append(Text(f"  IML func name: {self.raw.iml_func_name}"))
        ts.append(Text(f"  Description: {self.raw.description}"))

        # data
        if self.data is not None:
            ts.append(self.data.__rich__())

        # res
        ts.append(Text("DecomposeRes:", style="bold"))
        ts.append(
            Text(
                f"  {str(len(self.res.__repr__())) + ' bytes' if self.res else 'None'}"
            )
        )

        ts.append(Text("Test cases:", style="bold"))
        ts.append(
            Text(f"  {len(self.test_cases['iml']) if self.test_cases else 'None'}")
        )
        return ts

    def __rich__(self) -> Panel:
        """Rich display for the entire RegionDecomp."""
        content_parts = []

        # Add raw request info
        raw_req_group = Group(
            Text(f"Src func name: {self.raw.src_func_name}"),
            Text(f"IML func name: {self.raw.iml_func_name}"),
            Text(f"Description: {self.raw.description}"),
        )
        content_parts.append(Panel(raw_req_group, title="Raw Request"))

        if self.data:
            content_parts.append(Panel(self.data.__rich__(), title="Request Data"))

        if self.res and self.res.regions_str and len(self.res.regions_str) > 0:
            # data = [region.model_dump() for region in self.res.regions_str]
            data = self.res.regions_str

            if "docstr" in data[0]:
                for item in data:
                    item.pop("docstr")

            table = Table(title="Regions")

            col_names = ["#", "Constraints", "Invariant"]
            for col_name in col_names:
                table.add_column(col_name)

            for i, item in enumerate(data, 1):
                table.add_row(
                    str(i),
                    str(
                        "\n".join(
                            item.constraints_str
                            if isinstance(item.constraints_str, list)
                            else [item.constraints_str]
                        )
                    ),
                    str(
                        "\n".join(
                            item.invariant_str
                            if isinstance(item.invariant_str, list)
                            else [item.invariant_str]
                        )
                    ),
                )

            content_parts.append(table)

        if self.test_cases:
            content_parts.append(self.render_test_cases(self.test_cases))

        return Panel(Group(*content_parts), title="Region Decomposition")

    def __repr__(self):
        title_t = Text("RegionDecomp", style="bold")

        content_ts = self.render_content()
        content_t = rich_utils.join_texts(content_ts)

        t = Text()
        t.append(title_t)
        t.append("\n")
        t.append(rich_utils.left_pad(content_t, 2))
        return t.plain
