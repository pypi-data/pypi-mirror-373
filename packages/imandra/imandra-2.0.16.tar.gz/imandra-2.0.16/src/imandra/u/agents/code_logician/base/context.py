from typing import Any

from pydantic import BaseModel, Field

from .imandrax import EvalRes


class ConversionSourceInfo(BaseModel):
    """
    Context retrieved based on the source code.

    For languages other than Python, only `iml_api_refs` are populated
    """

    meta_eg: list[Any] = Field([], description="Language-specific meta examples")
    relevant_eg: list[Any] = Field([], description="Relevant examples")
    iml_api_refs: list[Any] = Field(
        [], description="IML API references relevant to the source code"
    )
    missing_func: list[Any] | None = Field(
        None, description="Missing functions in the source code"
    )
    user_inject: str | None = Field(None, description="User-injected context")


class ConversionFailureInfo(BaseModel):
    """Context based on conversion failure. Used for re-try conversion.

    Note that `iml_api_refs` and `missing_func` are re-retrived based on the error,
    different from the ones in `SourceCodeInfo`.
    """

    iml_code: str = Field(description="IML code")
    eval_res: EvalRes

    sim_errs: list[Any] = Field([], description="Similar errors")
    human_hint: str | None = Field(None, description="Human hint")
    iml_api_refs: list[Any] = Field([], description="Relevant IML API references")
    missing_func: list[Any] = Field([], description="Missing functions in the code")
