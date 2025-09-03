from io import TextIOWrapper
from typing import Callable, Dict

from ..output_builder import OutputBuilder
from ..shared import DefKind, DefinitionContext
from . import struct, enum, tagged_union
from .prepare import prepare_context


def write_to_file_cpp(file: TextIOWrapper, context: DefinitionContext):
    builder = OutputBuilder()
    prepare_context(context)
    add_file_contents(builder, context)
    file.write(builder.make())


def add_file_contents(b: OutputBuilder, context: DefinitionContext):
    add_header(b, context)
    add_forward_declarations(b, context)
    add_declarations(b, context)
    add_definitions(b, context)


def add_header(b: OutputBuilder, context: DefinitionContext):
    b.add_text(
        f"""
/**
 * This file has been auto-generated via blitzbuffers. Do not edit it directly.
 */
"""
    )

    b.add_file_contents("cpp/blitzbuffers.hpp")
    b.skip_line(1)

    b.add_line("namespace bzb = blitzbuffers;")

    b.skip_line(1)


def for_each_def(b: OutputBuilder, ctx: DefinitionContext, fn_kind_map: Dict[DefKind, Callable]):
    for def_name in ctx["def_names"]:
        d = ctx["def_mapping"][def_name]
        if not "is_union_variant" in d:

            fn_kind_map[d["kind"]](b, d, ctx)


def add_forward_declarations(b: OutputBuilder, ctx: DefinitionContext):
    b.skip_line(1)
    b.add_line("//")
    b.add_line("// Forward declarations")
    b.add_line("//")
    for_each_def(
        b,
        ctx,
        {
            DefKind.ENUM: enum.add_forward_declaration,
            DefKind.STRUCT: struct.add_forward_declaration,
            DefKind.TAGGED_UNION: tagged_union.add_forward_declaration,
        },
    )


def add_declarations(b: OutputBuilder, ctx: DefinitionContext):
    b.skip_line(1)
    b.add_line("//")
    b.add_line("// Declarations")
    b.add_line("//")
    for_each_def(
        b,
        ctx,
        {
            DefKind.ENUM: enum.add_declaration,
            DefKind.STRUCT: struct.add_declaration,
            DefKind.TAGGED_UNION: tagged_union.add_declaration,
        },
    )


def add_definitions(b: OutputBuilder, ctx: DefinitionContext):
    b.skip_line(1)
    b.add_line("//")
    b.add_line("// Definitions")
    b.add_line("//")
    for_each_def(
        b,
        ctx,
        {
            DefKind.ENUM: enum.add_definition,
            DefKind.STRUCT: struct.add_definition,
            DefKind.TAGGED_UNION: tagged_union.add_definition,
        },
    )
