import math
from typing import List, Set, cast

from lark import Lark, Transformer, Tree, Token

from blitzbuffers.shared import (
    DefMapping,
    Definition,
    DefinitionContext,
    DefKind,
    PRIMITIVE_BYTE_SIZES,
    OFFSET_BYTE_SIZE,
    StructDefinition,
    is_enum,
    is_struct,
    is_tagged_union,
)

json_parser = Lark(
    r"""

    schema : namespace_def? defs

    namespace_lang : "<" CNAME ">"
    namespace_def : "namespace" namespace_lang? namespace_name ("." namespace_name)* ";"? -> namespace
    ?namespace_name : CNAME -> name

    defs : def*
    ?def : struct
         | enum

    ?def_name : PASCAL_NAME -> name

    struct : "struct" def_name struct_def
    ?struct_def : "{" struct_fields "}"

    struct_fields : (struct_field [";" | ","])* -> fields
    struct_field : struct_field_name ":" struct_field_type -> field
    ?struct_field_name : CNAME -> name

    ?struct_field_type: type -> type

    ?tuple : "(" type ("," type)* ")" -> tuple

    ?type: PASCAL_NAME -> def
        | struct_def -> anon_struct
        | type "[" "]" -> vector
        | "string" -> string
        | "bool" -> bool

        | "u8"    -> u8
        | "u16"   -> u16
        | "u32"   -> u32
        | "u64"   -> u64
        | "u128"  -> u128

        | "i8"    -> i8
        | "i16"   -> i16
        | "i32"   -> i32
        | "i64"   -> i64
        | "i128"  -> i128

        | "f32" -> f32
        | "f64" -> f64

    enum : "enum" def_name "{" enum_values "}"
    enum_values : (enum_value [";" | ","])* -> values
    ?enum_value : PASCAL_NAME -> simple_enum
        | PASCAL_NAME tuple -> tagged_union_tuple
        | PASCAL_NAME struct_def -> tagged_union_struct

    PASCAL_NAME: (UCASE_LETTER [LCASE_LETTER | DIGIT]*)+

    COMMENT: "#" /[^\n]*/ _NEWLINE
    COMMENT_SLASH: "//" /[^\n]*/ _NEWLINE
    _NEWLINE: "\n"

    %import common.WS
    %import common.UCASE_LETTER
    %import common.LCASE_LETTER
    %import common.LETTER
    %import common.CNAME
    %import common.WORD
    %import common.DIGIT
    %ignore WS
    %ignore COMMENT
    %ignore COMMENT_SLASH

    """,
    start="schema",
)


class BlitzBuffersTransformer(Transformer):
    __anon_struct_count = 0

    def name(self, name: Tree):
        (name,) = name
        return name

    def type(self, type: Tree):
        type = type[0]
        if len(type.children) == 0:
            return type.data

        if type.data == "def":
            return type.children[0]
        elif type.data == "vector":
            return {"container": "vector", "inner": self.type(type.children)}
        elif type.data == "anon_struct":
            self.__anon_struct_count = self.__anon_struct_count + 1
            return {
                "kind": DefKind.STRUCT,
                "name": f"_AnonStruct_{self.__anon_struct_count}",
                "fields": type.children[0],
            }
        else:
            raise Exception(f"Unknown type: {type}")

    def CNAME(self, cname: Token):
        return cname.value

    def PASCAL_NAME(self, pascal_name: Token):
        return pascal_name.value

    def field(self, field: List):
        return {
            "name": field[0],
            "type": field[1],
        }

    fields = list
    values = list

    def tuple(self, fields):
        return [{"name": f"{idx}", "type": self.type((entry,))} for idx, entry in enumerate(fields)]

    def defs(self, defs):
        return defs

    def schema(self, schema):
        return schema

    def namespace(self, namespace):
        return namespace

    def struct(self, struct):
        return {
            "kind": DefKind.STRUCT,
            "name": struct[0],
            "fields": struct[1],
        }

    def enum(self, enum):
        variants_info = []

        is_tagged_union = False
        for variant in enum[1]:
            variant_name = variant.children[0]
            type = None

            if variant.data == "tagged_union_struct":
                is_tagged_union = True
                type = {
                    "kind": DefKind.STRUCT,
                    "name": variant_name,
                    "fields": variant.children[1],
                }
            elif variant.data == "tagged_union_tuple":
                is_tagged_union = True
                type = {
                    "kind": DefKind.STRUCT,
                    "name": variant_name,
                    "fields": variant.children[1],
                }
            else:
                type = {
                    "kind": DefKind.STRUCT,
                    "name": variant_name,
                    "fields": [],
                }

            variants_info.append({"name": variant_name, "type": type})

        if is_tagged_union:
            return {
                "kind": DefKind.TAGGED_UNION,
                "name": enum[0],
                "variants": variants_info,
            }
        else:
            # It"s just a simple enum
            return {
                "kind": DefKind.ENUM,
                "name": enum[0],
                "variants": [v["name"] for v in variants_info],
            }


def validate_type(type, context: DefinitionContext, current_def_path=[]) -> None:
    # Check for primitive types or references to other user-defined types
    if isinstance(type, str):
        if type == "string":
            return
        elif type[0].islower():
            # Lower-case types are native, and needs to exist with a specific byte size
            if type not in PRIMITIVE_BYTE_SIZES:
                raise Exception(f"Unknown primitive type: '{type}'")
            return

        else:
            if type not in context["def_mapping"]:
                raise Exception(f"Unknown struct or enum: '{type}'")
            return

    # Remaining types are dictionaries
    if not isinstance(type, dict):
        raise Exception(f"Unexpected type: '{type}'")

    # Check for vector types
    if isinstance(type, dict):
        if "inner" in type:
            validate_type(type["inner"], context, current_def_path)
            return

    def_name = type["name"]

    type["path"] = current_def_path[:]
    current_def_path.append(def_name)

    if is_struct(type):
        # Validate fields
        seen_field_names = set()
        err = None

        for field in type["fields"]:
            field_name = field["name"]

            if field_name.startswith("_"):
                err = f"Fields are not allowed to start with an underscore: '{field_name}'"
            elif field_name in seen_field_names:
                err = f"Duplicate field name: '{field_name}'"
            else:
                field_type = field["type"]
                validate_type(field_type, context, current_def_path)

            if err != None:
                raise Exception(f"Invalid struct '{def_name}': {err}")

            seen_field_names.add(field_name)

    elif is_enum(type):
        seen_variant_names = set()
        err = None

        for variant_name in type["variants"]:
            if variant_name in seen_variant_names:
                err = f"Duplicate variant name '{variant_name}'"

            if err != None:
                raise Exception(f"Invalid enum '{def_name}': {err}")

            seen_variant_names.add(variant_name)

    elif is_tagged_union(type):
        seen_variant_names = set()
        err = None

        for variant in type["variants"]:
            variant_name = variant["name"]

            if variant_name.startswith("_"):
                err = f"Variants are not allowed to start with an underscore: '{variant_name}'"
            elif variant_name in seen_variant_names:
                err = f"Duplicate variant name: '{variant_name}'"

            validate_type(variant["type"], context, current_def_path)

            if err != None:
                raise Exception(f"Invalid enum '{def_name}': {err}")

            seen_variant_names.add(variant_name)
    else:
        raise Exception(f"Missing implementation for definition kind: {type['kind']}")

    current_def_path.pop()


def get_type_info(type, def_mappings, current_path):
    if isinstance(type, str) and type in PRIMITIVE_BYTE_SIZES:
        return PRIMITIVE_BYTE_SIZES[type], "primitive"

    elif isinstance(type, str) and type == "string":
        return OFFSET_BYTE_SIZE, "string"

    elif isinstance(type, dict):
        if "container" in type:
            if type["container"] == "vector":
                return OFFSET_BYTE_SIZE, "vector"

        size = prepare_and_calculate_size(type, def_mappings, current_path)
        if is_enum(type):
            return size, "primitive"
        else:
            return size, "embed"

    elif isinstance(type, str) and type in def_mappings:
        size = prepare_and_calculate_size(def_mappings[type], def_mappings, current_path)
        if is_enum(def_mappings[type]):
            return size, "primitive"
        else:
            return size, "embed"

    else:
        raise Exception(f"Unknown type size for: '{type}'")


def setup_id_and_path(definition: Definition, current_path: List[str]):
    if not isinstance(definition, dict) or not "name" in definition:
        return

    definition["path"] = current_path[:]
    current_path.append(definition["name"])
    definition["id"] = "::".join(current_path)

    if is_struct(definition):
        for field in definition["fields"]:
            setup_id_and_path(field["type"], current_path)

    elif is_enum(definition):
        pass

    elif is_tagged_union(definition):
        for variant in definition["variants"]:
            setup_id_and_path(variant["type"], current_path)

    else:
        raise Exception(f"Unhandled definition kind: {definition['kind']}")

    current_path.pop()


def prepare_and_calculate_size(definition: Definition, def_mappings: DefMapping, rec_stack: Set[str]) -> int:
    if "size" in definition:
        return definition["size"]

    def_name = definition["name"]
    if definition["id"] in rec_stack:
        raise Exception(f"Recursive definition found. Loop contains: {rec_stack}")

    rec_stack.add(definition["id"])

    # Minimize size needed for a pure enum, or an enum tag in a tagged union
    if is_enum(definition) or is_tagged_union(definition):
        variant_count = len(definition["variants"])

        bits_needed = variant_count and math.log2(variant_count) or 1

        enum_size = 0
        if bits_needed <= 8:
            enum_size = 1
        elif bits_needed <= 16:
            enum_size = 2
        elif bits_needed <= 32:
            enum_size = 4
        else:
            raise Exception(f"Too many variants for '{def_name}': {variant_count}")

        definition["enum_size"] = enum_size

    current_size = 0
    if is_struct(definition):
        for field in definition["fields"]:
            field["offset"] = current_size
            field["size"], field["kind"] = get_type_info(field["type"], def_mappings, rec_stack)
            current_size = current_size + field["size"]

    elif is_enum(definition):
        current_size = definition["enum_size"]

    elif is_tagged_union(definition):
        current_size = definition["enum_size"]

        max_variant_size = 0
        for idx, variant in enumerate(definition["variants"]):
            variant["tag"] = idx + 1

            variant_size = prepare_and_calculate_size(variant["type"], def_mappings, rec_stack)
            variant["size"] = variant_size
            if variant_size > max_variant_size:
                max_variant_size = variant_size

        current_size = current_size + max_variant_size

    else:
        raise Exception(f"Unhandled definition kind: {definition['kind']}")

    rec_stack.remove(definition["id"])

    definition["size"] = current_size
    return current_size


def topological_sort_struct(d: StructDefinition, ctx: DefinitionContext, visited: Set[str], stack: List[str]):
    for field in d["fields"]:
        if field["kind"] == "embed":
            if isinstance(field["type"], str) and field["type"][0].isupper():
                topological_sort_base_def(ctx["def_mapping"][field["type"]], ctx, visited, stack)
            else:
                topological_sort_struct(field["type"], ctx, visited, stack)


def topological_sort_base_def(d: Definition, ctx: DefinitionContext, visited: Set[str], stack: List[str]):
    if d["id"] in visited:
        return

    visited.add(d["id"])

    if is_struct(d):
        topological_sort_struct(d, ctx, visited, stack)

    elif is_tagged_union(d):
        for variant in d["variants"]:
            topological_sort_struct(variant["type"], ctx, visited, stack)

    stack.append(d["id"])


def topological_sort(ctx: DefinitionContext):
    stack = []
    visited = set()

    for d in ctx["def_mapping"].values():
        if d["id"] in visited:
            continue
        topological_sort_base_def(d, ctx, visited, stack)

    return stack


def parse_blitzbuffers(input: str) -> DefinitionContext:
    parsed_blitzbuffers = cast(List[Definition], BlitzBuffersTransformer().transform(json_parser.parse(input)))

    namespace = []
    defs = None
    # Check for namespace, and add to definitions if present
    if isinstance(parsed_blitzbuffers[0], list) and isinstance(parsed_blitzbuffers[0][0], str):
        defs = parsed_blitzbuffers[1]
        namespace = parsed_blitzbuffers[0]
    else:
        defs = parsed_blitzbuffers[0]

    context: DefinitionContext = {
        "def_names": [],
        "def_mapping": {},
        "namespace": namespace,
    }
    def_mapping = context["def_mapping"]

    # Setup initial definition name mapping
    for definition in defs:
        def_name = definition["name"]
        def_mapping[def_name] = definition

    for definition in defs:
        # Check validity of types and their relations
        validate_type(definition, context)

        # Sets up the path to each subdefinition within each definition
        setup_id_and_path(definition, [])

    for definition in defs:
        # Calculate sizes, offsets, and references to other defs
        prepare_and_calculate_size(definition, def_mapping, set())

    sorted_ids = topological_sort(context)
    context["def_names"] = sorted_ids

    return context
