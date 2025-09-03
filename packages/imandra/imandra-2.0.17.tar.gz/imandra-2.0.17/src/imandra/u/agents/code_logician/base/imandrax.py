from __future__ import annotations

import re
from enum import Enum
from typing import Literal, Self

from imandrax_api.lib import (
    Common_Fun_decomp_t_poly,
    Common_Region_t_poly,
    read_artifact_data,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)


class StorageEntry(BaseModel):
    model_config = ConfigDict(ser_json_bytes="base64", val_json_bytes="base64")

    key: str = Field(description="the CA store key")
    value: bytes = Field(description="the stored value")


class Art(BaseModel):
    model_config = ConfigDict(ser_json_bytes="base64", val_json_bytes="base64")

    kind: str = Field(description="The kind of artifact")
    data: bytes = Field(description="Serialized data, in twine")
    api_version: str = Field(
        description=(
            "Version of the API. This is mandatory and must match with the imandrax-api"
            " library version."
        )
    )
    storage: list[StorageEntry] = Field(
        default_factory=list, description="Additional definitions on the side"
    )


class ErrorKind(str, Enum):
    APPLIED_SYMBOL_TYPE_ERR = "AppliedSymbolTypeErr"
    CONFIG_ERROR = "ConfigError"
    CPTR_GET_OTHER_ERR = "CptrGetOtherErr"
    CPTR_NOT_FOUND_IN_STORAGE = "CptrNotFoundInStorage"
    GENERIC_USER_ERROR = "GenericUserError"
    INVALID_FUN_DEFINITION = "InvalidFunDefinition"
    INVALID_QIDENT = "InvalidQident"
    INVALID_TYPE_ALIAS = "InvalidTypeAlias"
    INVALID_TYPE_DEFINITION = "InvalidTypeDefinition"
    INVALID_CNAME = "InvalidCname"
    LEVAL_ERROR = "LevalError"
    LOWER_CIR_ERROR = "LowerCirError"
    LOWER_MIR_ERROR = "LowerMirError"
    LOWER_RIR_ERROR = "LowerRirError"
    PARSER_NOT_REGISTERED = "ParserNotRegistered"
    PATMATCH_ERROR = "PatmatchError"
    SYN_TERM_CREATE_ERROR = "SynTermCreateError"
    SYNTAX_ATTRIBUTE_ERR = "SyntaxAttributeErr"
    SYNTAX_ERR = "SyntaxErr"
    SYNTAX_UNSUGAR_ERR = "SyntaxUnsugarErr"
    TACTIC_EVAL_ERR = "TacticEvalErr"
    TERM_INVALID_SHAPE = "TermInvalidShape"
    TERM_MODEL_FIERR = "TermModelFIErr"
    THREAD_FUT_FAILURE = "ThreadFutFailure"
    THREAD_TIMER_FAILURE = "ThreadTimerFailure"
    TY_INFER_INTERNAL_ERROR = "TyInferInternalError"
    TYPE_ARITY_MISMATCH = "TypeArityMismatch"
    TYPE_CYCLE_DETECTED = "TypeCycleDetected"
    TYPE_ERR = "TypeErr"
    TYPE_VAR_ALREADY_BOUND = "TypeVarAlreadyBound"
    TYPED_SYMBOL_NON_GROUND = "TypedSymbolNonGround"
    UID_CONTENT_ADDRESSING_NAME_MISMATCH = "UidContentAddressingNameMismatch"
    UID_CONTENT_ADDRESSING_NOT_TEMPORARY = "UidContentAddressingNotTemporary"
    UID_NOT_CONTENT_ADDRESSED = "UidNotContentAddressed"
    UNKNOWN_BUILTIN_SYMBOL_FOR_UID = "UnknownBuiltinSymbolForUid"
    UNKNOWN_TYPE_DEFINITION = "UnknownTypeDefinition"
    INTERACTIVE_PROOF_ERR = "InteractiveProofErr"
    PROOF_DESER_ERROR = "ProofDeserError"
    PROOF_CHECK_ERROR = "ProofCheckError"
    INVALID_ANCHOR = "InvalidAnchor"
    INDUCT_SCHEMA_ERROR = "InductSchemaError"
    UNSUPPORTED = "Unsupported"
    LOWER_FOL_ERROR = "LowerFolError"
    VALIDATION_ERROR = "ValidationError"
    LSP_ERROR = "LspError"
    INTERRUPTED = "Interrupted"
    REDIS_ERROR = "RedisError"
    CIRDECL_NOT_FOUND_IN_STORAGE = "CIRDeclNotFoundInStorage"
    SERIALIZATION_ERROR = "SerializationError"
    DESERIALIZATION_ERROR = "DeserializationError"
    DEBUG_MODE = "DebugMode"
    IMPORT_ERROR = "ImportError"
    GENERIC_IOERROR = "GenericIOError"
    DUNE_ERROR = "DuneError"
    RPC_ERROR = "RpcError"
    RPC_DESER_ERROR = "RpcDeserError"
    RPC_NETWORK_ERROR = "RpcNetworkError"
    RPC_TIMEOUT = "RpcTimeout"
    AUTH_ERROR = "AuthError"
    FILE_EXISTS = "FileExists"
    DIRECTORY_CREATION_ERROR = "DirectoryCreationError"
    DECOMP_ERROR = "DecompError"
    VERSION_MISMATCH_ERROR = "VersionMismatchError"
    OH_NO_ERROR = "OhNoError"
    DEBOUNCED = "Debounced"

    @classmethod
    def from_proto_kind(cls, proto_kind: str) -> Self:
        kinds = re.findall(r'\{ Kind.name = "(.+)" \}', proto_kind)
        if len(kinds) != 1:
            raise ValueError("Unable to parse kind")
        return cls(kinds[0])


class ErrorMessage(BaseModel):
    """An error message"""

    msg: str
    locs: list[Location] = Field(
        default_factory=list, description="Locations for this message"
    )
    backtrace: str | None = Field(default=None, description="Captured backtrace")


class Error(BaseModel):
    msg: ErrorMessage | None = Field(
        default=None, description="The toplevel error message"
    )
    kind: str = Field(description="A string description of the kind of error")
    stack: list[ErrorMessage] = Field(
        default_factory=list, description="Context for the error"
    )
    process: str | None = Field(default=None)


class Position(BaseModel):
    line: int
    col: int


class Location(BaseModel):
    file: str | None = Field(default=None)
    start: Position | None = Field(default=None)
    stop: Position | None = Field(default=None)


class Session(BaseModel):
    """A session identifier"""

    id: str = Field(description="The session's unique ID (e.g a uuid)")


class SessionCreate(BaseModel):
    """Create a new session"""

    po_check: bool = Field(default=True, description="Do we check Proof Obligations?")
    api_version: str = Field(description="the API types version (mandatory)")


class SessionOpen(BaseModel):
    """Reconnect to the given session"""

    id: Session | None = Field(
        default=None, description="The session's unique ID (e.g a uuid)"
    )
    api_version: str = Field(description="the API types version (mandatory)")


class TaskKind(Enum):
    TASK_UNSPECIFIED = "TASK_UNSPECIFIED"
    TASK_EVAL = "TASK_EVAL"
    TASK_CHECK_PO = "TASK_CHECK_PO"
    TASK_PROOF_CHECK = "TASK_PROOF_CHECK"
    TASK_DECOMP = "TASK_DECOMP"


class TaskID(BaseModel):
    id: str = Field(description="The task identifier")


class Task(BaseModel):
    id: TaskID | None = Field(default=None)
    kind: TaskKind


class Origin(BaseModel):
    from_sym: str = Field(description="Symbol from which the task originated")
    count: int = Field(description="A counter for tasks for this symbol")


class Empty(BaseModel):
    """Void type, used for messages without arguments or return value."""

    pass


class StringMsg(BaseModel):
    msg: str


class SessionCreateReq(BaseModel):
    api_version: str = Field(description="the API types version (mandatory)")


class LiftBool(Enum):
    Default = 0
    NestedEqualities = 1
    Equalities = 2
    All = 3


class DecomposeReq(BaseModel):
    session: Session | None = Field(default=None)
    name: str = Field(description="name of function to decompose")
    assuming: str | None = Field(
        default=None, description="name of side condition function"
    )
    basis: list[str]
    rule_specs: list[str]
    prune: bool
    ctx_simp: bool | None = Field(default=None)
    lift_bool: LiftBool | None = Field(default=None)
    str_: bool = Field(default=True, alias="str")
    timeout: int | None = Field(default=None)


class DecomposeResProto(BaseModel):
    artifact: Art | None = Field(default=None)
    err: Empty | None = Field(default=None)
    errors: list[Error] = Field(default_factory=list)
    task: Task | None = Field(default=None)

    @model_validator(mode="after")
    def one_of_res(self) -> Self:
        if (self.artifact is None) == (self.err is None):
            raise ValueError("One of artifact or err must be set")
        return self


class string_kv(BaseModel):
    k: str
    v: str


class RegionStr(BaseModel):
    model_eval_str: str
    constraints_str: list[str] | None = Field(default=None)
    invariant_str: str
    model_str: dict[str, str]


def sanitise_table_cell(cell: str) -> str:
    return cell.replace("\n", "\\\n").replace("|", "\\|")


class DecomposeRes(DecomposeResProto):
    """Result of a decomposition"""

    regions_str: list[RegionStr] | None = Field(
        default=None, description="None if there's decomposition error"
    )

    @model_validator(mode="after")
    def unwrap_region_str(self) -> Self:
        # Unwrap the regionsStr from the artifact to the old format
        if self.regions_str is not None:  # noqa: SIM114
            return self
        elif self.errors:
            return self
        else:
            art = read_artifact_data(data=self.artifact.data, kind=self.artifact.kind)
            match art:
                case Common_Fun_decomp_t_poly(_f_id, _f_args, regions):
                    pass
                case _:
                    raise ValueError(f"Unknown decomp artifact type: {type(art)}")

            regions_str: list[RegionStr] = []
            for region in regions:
                match region:
                    case Common_Region_t_poly(
                        constraints=_constraints,
                        invariant=_invariant,
                        meta=meta,
                        status=_status,
                    ):
                        meta_d = dict(meta)

                        # string
                        meta_str_d = dict(meta_d.get("str").arg)
                        constraints = [c.arg for c in meta_str_d.get("constraints").arg]
                        invariant = meta_str_d.get("invariant").arg
                        model = {k: v.arg for (k, v) in meta_str_d.get("model").arg}
                        model_eval = meta_str_d.get("model_eval").arg
                        region_str = RegionStr(
                            model_eval_str=model_eval,
                            invariant_str=invariant,
                            constraints_str=constraints,
                            model_str=model,
                        )
                        regions_str.append(region_str)
                    case _:
                        raise ValueError(f"Unknown region type: {type(region)}")
            return self.model_copy(update={"regions_str": regions_str})

    @property
    def model(self) -> list[dict[str, str]]:
        """[{"x": "1", "y": "2"}, {"x": "3", "y": "4"}]"""
        if not self.regions_str:
            return []
        return [r.model_str for r in self.regions_str]

    @property
    def model_eval(self) -> list[str]:
        if not self.regions_str:
            return []
        return [r.model_eval_str for r in self.regions_str]

    @property
    def iml_test_cases(self) -> list[dict[str, str]]:
        """
        [
            {"args": {"x": "1", "y": "2"}, "expected_output": "3"},
            {"args": {"x": "3", "y": "4"}, "expected_output": "7"},
        ]
        """
        if not self.regions_str:
            return []
        return list(
            map(
                lambda x: {"args": x[0], "expected_output": x[1]},
                zip(self.model, self.model_eval, strict=False),
            )
        )

    @property
    def test_docstrs(self) -> list[str]:
        docstrs = []
        for region_str in self.regions_str:
            s = ""
            if region_str.constraints_str:
                s += "Constraints:\n"
                for c in region_str.constraints_str:
                    s += f"    - `{c}`\n"
            if region_str.invariant_str:
                s += "Invariant:\n"
                s += f"    - `{region_str.invariant_str}`\n"
            docstrs.append(s)
        return docstrs


class EvalSrcReq(BaseModel):
    session: Session | None = Field(default=None)
    src: str = Field(description="source code to evaluate")
    async_only: bool | None = Field(
        default=None,
        description="if true, do not wait for tasks results, only return the task list "
        "and not the task results. Use `get_artifact` to get the results.",
    )


class EvalOutput(BaseModel):
    """Output of an `eval` statement"""

    success: bool
    value_as_ocaml: str | None = Field(
        default=None, description="result as a OCaml value, if any"
    )
    errors: list[Error] = Field(default_factory=list)


class EvalRes(BaseModel):
    success: bool = Field()
    messages: list[str] = Field(default_factory=list, description='"normal" messages')
    errors: list[Error] = Field(default_factory=list, description="akin to stderr")

    # All tasks started during eval
    tasks: list[Task] = Field(
        default_factory=list, description="all tasks started during eval"
    )
    po_results: list[PO_Res] = Field(default_factory=list)
    eval_results: list[EvalOutput] = Field(default_factory=list)
    decomp_results: list[DecomposeRes] = Field(default_factory=list)


class VerifySrcReq(BaseModel):
    session: Session | None = Field(default=None)
    src: str = Field(description="source code")
    hints: str | None = Field(default=None)


class VerifyNameReq(BaseModel):
    session: Session | None = Field(default=None)
    name: str = Field(description="name of the predicate to verify")
    hints: str | None = Field(default=None)


class InstanceSrcReq(BaseModel):
    session: Session | None = Field(default=None)
    src: str = Field(description="source code")
    hints: str | None = Field(default=None)


class InstanceNameReq(BaseModel):
    session: Session | None = Field(default=None)
    name: str = Field(description="name of the predicate to verify")
    hints: str | None = Field(default=None)


class Proved(BaseModel):
    proof_pp: str | None = Field(default=None)


class Verified_upto(BaseModel):
    msg: str | None = Field(default=None)


class Unsat(BaseModel):
    proof_pp: str | None = Field(default=None)


class ModelType(Enum):
    Counter_example = "Counter_example"
    Instance = "Instance"


class Model(BaseModel):
    m_type: ModelType  # NOTE: proto file has this but it's not returned?
    src: str = Field(description="iml source code for the model")
    artifact: Art | None = Field(default=None, description="the model as an artifact")


class Refuted(BaseModel):
    model: Model | None = Field(default=None)


class Sat(BaseModel):
    model: Model | None = Field(default=None)


class CounterSat(BaseModel):
    model: Model | None = Field(default=None)


class PO_Res(BaseModel):
    unknown: StringMsg | None = Field(default=None)
    err: Empty | None = Field(default=None)
    proof: Proved | None = Field(default=None)
    instance: CounterSat | None = Field(default=None)
    verified_upto: Verified_upto | None = Field(default=None)

    errors: list[Error] = Field(default_factory=list)
    task: Task | None = Field(default=None, description="the ID of the task")
    origin: Origin | None = Field(
        default=None, description="where did the task originate?"
    )

    @model_validator(mode="after")
    def one_of_res(self) -> Self:
        sum_of_res = sum(
            1
            for r in [
                self.unknown,
                self.err,
                self.proof,
                self.instance,
                self.verified_upto,
            ]
            if r is not None
        )
        if sum_of_res != 1:
            raise ValueError(
                "Exactly one of unknown, err, proof, instance, verified_upto must be "
                "set"
            )
        return self


class VerifyRes(BaseModel):
    unknown: StringMsg | None = Field(default=None)
    err: Empty | None = Field(default=None)
    proved: Proved | None = Field(default=None)
    refuted: Refuted | None = Field(default=None)
    verified_upto: Verified_upto | None = Field(default=None)

    errors: list[Error] = Field(default_factory=list)
    task: Task | None = Field(default=None, description="the ID of the task")

    @property
    def res_type(
        self,
    ) -> Literal["unknown", "err", "proved", "refuted", "verified_upto"]:
        if self.unknown is not None:
            return "unknown"
        elif self.err is not None:
            return "err"
        elif self.proved is not None:
            return "proved"
        elif self.refuted is not None:
            return "refuted"
        elif self.verified_upto is not None:
            return "verified_upto"
        else:
            raise AssertionError("Never")

    @property
    def res(self) -> StringMsg | Empty | Proved | Refuted | Verified_upto:
        if self.unknown is not None:
            return self.unknown
        elif self.err is not None:
            return self.err
        elif self.proved is not None:
            return self.proved
        elif self.refuted is not None:
            return self.refuted
        elif self.verified_upto is not None:
            return self.verified_upto
        else:
            raise AssertionError("Never")

    @model_validator(mode="after")
    def one_of_res(self) -> Self:
        sum_of_res = sum(
            1
            for r in [
                self.unknown,
                self.err,
                self.proved,
                self.refuted,
                self.verified_upto,
            ]
            if r is not None
        )
        if sum_of_res != 1:
            raise ValueError(
                "Exactly one of unknown, err, proved, refuted, verified_upto must be "
                "set"
            )
        return self


class InstanceRes(BaseModel):
    unknown: StringMsg | None = Field(default=None)
    err: Empty | None = Field(default=None)
    unsat: Unsat | None = Field(default=None)
    sat: Sat | None = Field(default=None)

    errors: list[Error] = Field(default_factory=list)
    task: Task | None = Field(default=None, description="the ID of the task")

    @model_validator(mode="after")
    def one_of_res(self) -> Self:
        sum_of_res = sum(
            1 for r in [self.unknown, self.err, self.unsat, self.sat] if r is not None
        )
        if sum_of_res != 1:
            raise ValueError("Exactly one of unknown, err, unsat, sat must be set")
        return self


class TypecheckReq(BaseModel):
    session: Session | None = Field(default=None)
    src: str = Field(description="source code to evaluate")


class TypecheckResProto(BaseModel):
    success: bool
    types: str = Field(description="JSON string of inferred types")
    errors: list[Error] = Field(default_factory=list)


class InferredType(BaseModel):
    name: str
    ty: str = Field(description="inferred type")
    line: int = Field(description="line number")
    column: int = Field(description="column number")


InferredTypes = TypeAdapter(list[InferredType])


class TypecheckRes(TypecheckResProto):
    types: list[InferredType] = Field(description="Parsed inferred types")

    @field_validator("types", mode="before")
    @classmethod
    def validate_types(cls, v: str | list[InferredType]) -> list[InferredType]:
        if isinstance(v, str):
            # Parse JSON string into list of dicts and validate with pydantic
            types_list = InferredTypes.validate_json(v)
            return types_list
        return v


class OneshotReq(BaseModel):
    input: str = Field(description="some iml code")
    timeout: float | None = Field(default=None)


class OneshotRes(BaseModel):
    class Stats(BaseModel):
        time: float

    results: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    stats: Stats | None = Field(default=None)
    detailed_results: list[str] = Field(default_factory=list)
