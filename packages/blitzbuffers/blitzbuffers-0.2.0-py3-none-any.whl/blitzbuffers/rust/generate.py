from io import TextIOWrapper

from .prepare import prepare_context
from ..output_builder import OutputBuilder
from ..shared import DefKind, DefinitionContext
from . import struct, enum, tagged_union


def write_to_file_rust(file: TextIOWrapper, ctx: DefinitionContext):
    builder = OutputBuilder()
    prepare_context(ctx)
    add_file_contents(builder, ctx)
    file.write(builder.make())


def add_file_contents(b: OutputBuilder, ctx: DefinitionContext):
    add_header(b, ctx)

    bzb_path = ["blitzbuffers"]
    for ns in ctx["namespace"]:
        bzb_path.append("super")
        b.add_line(f"pub mod { ns } {{")
        b.increment_indent()

    bzb_path.reverse()

    b.add_line(f"use std::{{borrow::Borrow, iter::Zip}};")
    b.add_line(
        f"use { '::'.join(bzb_path) }::{{self as bzb, BlitzBuilder, BlitzCalcSize, BlitzCheck, BlitzCopyFrom, BlitzSized, BlitzVector, BlitzViewer, PrimitiveByteFunctions}};"
    )
    b.skip_line(1)

    for def_name in ctx["def_names"]:
        d = ctx["def_mapping"][def_name]
        match d["kind"]:
            case DefKind.ENUM:
                enum.add_definition(b, d, ctx)
            case DefKind.STRUCT:
                struct.add_definition(b, d, ctx)
            case DefKind.TAGGED_UNION:
                tagged_union.add_definition(b, d, ctx)

    for ns in ctx["namespace"]:
        b.decrement_indent()
        b.add_line(f"}}")


def add_header(b: OutputBuilder, ctx: DefinitionContext):
    b.add_line("#![cfg_attr(rustfmt, rustfmt_skip)]")
    b.add_line("#![allow(unused, non_camel_case_types, non_snake_case)]")
    b.add_line("#![allow(clippy::all)]")
    b.add_text(
        f"""
/**
 * This file has been auto-generated via blitzbuffers. Do not edit it directly.
 */
"""
    )

    b.add_file_contents("rust/blitzbuffers.rs")
    b.skip_line(1)
