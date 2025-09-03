from enum import Enum
from typing import List, Literal, Mapping, Optional, TypeGuard, TypedDict, Union

OFFSET_BYTE_SIZE = 4

PRIMITIVE_BYTE_SIZES = {
    "bool": 1,
    "u8": 1,
    "u16": 2,
    "u32": 4,
    "u64": 8,
    "u128": 16,
    "i8": 1,
    "i16": 2,
    "i32": 4,
    "i64": 8,
    "i128": 16,
    "f32": 4,
    "f64": 8,
}


class DefKind(Enum):
    STRUCT = 0
    ENUM = 1
    TAGGED_UNION = 2


FieldTy = Union[Literal["vector", "string"], str]


class StructField(TypedDict):
    kind: Literal["vector", "string", "embed", "primitive"]
    name: str
    type: Union[FieldTy, List[FieldTy]]


class BaseDefinition(TypedDict):
    name: str
    size: int
    id: str
    path: str


class StructDefinition(BaseDefinition):
    kind: DefKind.STRUCT
    fields: List[StructField]


class EnumDefinition(BaseDefinition):
    kind: DefKind.ENUM
    variants: List[str]


class TaggedUnionVariant(TypedDict):
    name: str
    type: Optional[StructDefinition]


class TaggedUnionDefinition(BaseDefinition):
    kind: DefKind.TAGGED_UNION
    size: int
    variants: List[TaggedUnionVariant]


Definition = Union[StructDefinition, EnumDefinition, TaggedUnionDefinition]

DefMapping = Mapping[str, Definition]


def is_struct(definition: Definition) -> TypeGuard[StructDefinition]:
    return definition["kind"] == DefKind.STRUCT


def is_enum(definition: Definition) -> TypeGuard[EnumDefinition]:
    return definition["kind"] == DefKind.ENUM


def is_tagged_union(definition: Definition) -> TypeGuard[TaggedUnionDefinition]:
    return definition["kind"] == DefKind.TAGGED_UNION


class DefinitionContext(TypedDict):
    def_mapping: DefMapping
    def_names: List[str]
    namespace: List[str]
