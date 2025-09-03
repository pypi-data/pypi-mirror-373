from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition


def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    # b.add_line(f"{{% set underlying_type = "u" + ((def.enum_size * 8) | string) %}}")
    underlying_type = f"u{ d['enum_size'] * 8 }"

    b.add_line(f"#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, PartialOrd, Ord, Hash)]")
    b.add_line(f"#[repr({ underlying_type })]")
    b.add_line(f"pub enum { d['name'] } {{")
    b.increment_indent()

    if len(d["variants"]) > 0:
        b.add_line(f"#[default]")

    for idx, variant in enumerate(d["variants"]):
        b.add_line(f"{ variant } = { idx },")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"impl From<{ d['name'] }> for { underlying_type } {{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn from(val: { d['name'] }) -> Self {{")
    b.add_line(f"        val as { underlying_type }")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    # Into enum from underlying type
    b.add_line(f"impl From<{ underlying_type }> for { d['name'] } {{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn from(val: { underlying_type }) -> Self {{")
    b.increment_indent()

    b.add_line(f"match val {{")
    b.increment_indent()

    for idx, variant in enumerate(d["variants"]):
        b.add_line(f"{ idx }{underlying_type} => { d['name'] }::{ variant },")

    b.add_line(f"v => {{")
    b.increment_indent()
    b.add_line(f"eprintln!(\"No matching enum found for '{ d['name'] }' with value: {{:?}}\", v);")
    b.add_line(f"{ d['name'] }::default()")
    b.decrement_indent()
    b.add_line(f"}},")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"impl bzb::PrimitiveByteFunctions for { d['name'] } {{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    unsafe fn write_le_bytes(&self, bytes: &mut [u8]) {{")
    b.add_line(f"        let v: { underlying_type } = (*self).into();")
    b.add_line(f"        v.write_le_bytes(bytes)")
    b.add_line(f"    }}")
    b.skip_line(1)

    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    unsafe fn read_le_bytes(bytes: &[u8]) -> Self {{")
    b.add_line(f"        { underlying_type }::read_le_bytes(bytes).into()")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzSized
    b.add_line(f"impl bzb::BlitzSized for { d['name'] } {{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn get_blitz_size() -> u32 {{")
    b.add_line(f"        { d['enum_size'] }")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCalcSize
    b.add_line(f"impl bzb::BlitzCalcSize for { d['name'] } {{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn calc_blitz_size(&self) -> u32 {{")
    b.add_line(f"        { d['enum_size'] }")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCheck
    b.add_line(f"impl bzb::BlitzCheck for { d['name'] } {{")
    b.increment_indent()
    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn blitz_check(buffer: &[u8]) -> Result<(), String>")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_lines(
        f"if buffer.len() < Self::get_blitz_size() as usize {{",
        f"    return Err(format!(\"[{ d['name'] }] Expected buffer to be minimum {{}} bytes, but it was only {{}} bytes.\", Self::get_blitz_size(), buffer.len()));",
        f"}}",
    )
    b.skip_line(1)

    enum_ty = f"u{ d['enum_size'] * 8 }"
    b.add_line(f"let tag = unsafe {{ { enum_ty }::read_le_bytes(buffer) }};")

    b.add_line(f"match tag {{")
    b.increment_indent()
    for idx, variant in enumerate(d["variants"]):
        b.add_line(f"{ idx }{underlying_type} => Ok(()),")

    b.add_line(f"v => Err(format!(\"[{ d['name'] }] Unknown tag {{}}\", v)),")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
