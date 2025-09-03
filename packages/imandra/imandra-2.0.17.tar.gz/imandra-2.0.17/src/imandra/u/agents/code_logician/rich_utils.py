from typing import Any

from devtools import PrettyFormat
from pydantic import BaseModel
from rich.console import Console, RenderableType
from rich.text import Text


def extract_field_titles_and_values(model: BaseModel) -> dict[str, str]:
    """Extract the titles and values of the fields of a pydantic model"""
    model_type = model.__class__
    res = {}
    for field_name, field_info in model_type.model_fields.items():
        val = getattr(model, field_name)
        title = field_info.title
        res[title] = str(val)
    return res


def join_texts(texts: list[Text], sep: str = "\n") -> Text:
    """Join a list of texts with a separator"""
    t = Text()
    for text in texts:
        t.append(text)
        if text != texts[-1]:
            t.append(sep)
    return t


def left_pad(text: Text, width: int) -> Text:
    """Left pad a text with a given width"""
    lines = text.split()
    for line in lines:
        line.pad_left(width, " ")
    return join_texts(list(lines))


def devtools_pformat(obj: Any, indent: int = 2) -> Text:
    """Format an object with devtools.pformat"""
    return Text.from_ansi(PrettyFormat(indent_step=indent)(obj, highlight=True))


def get_str(*renderables: RenderableType | object, plain: bool = True) -> str:
    console = Console(
        record=True,
        width=80,
        color_system="standard",
        force_terminal=False,
        force_interactive=False,
        force_jupyter=False,
    )
    with console.capture() as capture:
        for renderable in renderables:
            console.print(renderable)
    exported_text = capture.get()
    if plain:
        return Text.from_ansi(exported_text).plain
    else:
        return exported_text
