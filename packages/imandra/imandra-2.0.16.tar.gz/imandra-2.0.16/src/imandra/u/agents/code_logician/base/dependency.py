from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class ModuleInfo(BaseModel):
    """
    A data class that contains the information of a module that will be used as
    dependency information context in the formalization.
    """

    name: str
    relative_path: Path
    content: str
    src_lang: str


class FormalizationDependency(BaseModel):
    """
    A data class that couples a source module and its corresponding IML module.
    """

    src_module: ModuleInfo
    iml_module: ModuleInfo
