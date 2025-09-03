from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition
from . import struct


#
# Definition
#
def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    add_raw(b, d, ctx)
    add_raw_methods(b, d, ctx)
    add_builder(b, d, ctx)
    add_viewer(b, d, ctx)

    for variant in d["variants"]:
        struct.add_definition(b, variant["type"], ctx)


def add_raw(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"#[derive(Debug, Default, Clone, PartialEq, PartialOrd)]")
    b.add_line(f"pub enum { d['name'] } {{")
    b.increment_indent()
    b.add_line(f"#[default]")
    b.add_line(f"_None,")

    for variant in d["variants"]:
        b.add_line(f"{ variant['name'] }({ variant['fq_name'] }),")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_raw_methods(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    # BlitzSized
    b.add_lines(
        f"impl bzb::BlitzSized for { d['name'] } {{",
        f"    #[inline(always)]",
        f"    fn get_blitz_size() -> u32 {{",
        f"        return { d['size'] };",
        f"    }}",
        f"}}",
    )
    b.skip_line(1)

    # BlitzCalcSize
    b.add_line(f"impl bzb::BlitzCalcSize for { d['name'] } {{")
    b.increment_indent()
    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn calc_blitz_size(&self) -> u32")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"match self {{")
    b.increment_indent()
    b.add_line(f"{ d['name'] }::_None => { d['size'] },")

    for variant in d["variants"]:
        b.add_line(f"{ d['name'] }::{ variant['name'] }(v) => v.calc_blitz_size() - { variant['size'] } + { d['size'] },")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Directly to blitz buffer
    b.add_lines(
        f"impl { d['name'] } {{",
        f"  #[inline(always)]",
        f"  pub fn to_blitz_buffer(&self) -> Vec<u8> {{",
        f"      let size = self.calc_blitz_size();",
        f"      let backend = unsafe {{ bzb::UnsafeDirectBufferBackend::new(size as usize) }};",
        f"      self.copy_onto(&backend);",
        f"      backend.into_buffer()",
        f"  }}",
        f"}}",
    )
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
    b.add_line(f"0{ enum_ty } => Ok(()),")

    for variant in d["variants"]:
        b.add_line(f"{ variant['tag'] }{ enum_ty } => { variant['fq_name'] }::blitz_check(unsafe {{ buffer.get_unchecked({ d['enum_size'] }..) }}),")

    b.add_line(f"v => Err(format!(\"[{ d['name'] }] Unknown tag {{}}.\", v)),")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Constructors
    b.add_line(f"impl { d['name'] } {{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"pub fn new_on<'a, Backend>(")
    b.add_line(f"    backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>,")
    b.add_line(f") -> { d['name'] }Builder<'a, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.add_line(f"    let offset = backend.get_size();")
    b.add_line(f"    let buffer = backend.get_new_buffer({ d['size'] });")
    b.add_line(f"    { d['name'] }Builder::new_blitz_builder(backend, buffer, offset)")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_lines(
        f"#[inline(always)]",
        f"pub fn copy_onto<'a, Backend>(&self, backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>)",
        f"where",
        f"    Backend: bzb::BlitzBufferBackend,",
        f"{{",
        f"    let mut builder = Self::new_on(backend);",
        f"    builder.copy_from(self);",
        f"}}",
    )
    b.skip_line(1)

    b.add_lines(
        f"#[inline(always)]",
        f"pub fn view_unchecked<'a>(buffer: &'a [u8]) -> { d['fq_name'] }Viewer<'a>",
        f"{{",
        f"    { d['fq_name'] }Viewer::new_blitz_view(buffer)",
        f"}}",
    )
    b.skip_line(1)

    b.add_lines(
        f"#[inline(always)]",
        f"pub fn view<'a>(buffer: &'a [u8]) -> Result<{ d['fq_name'] }Viewer<'a>, String>",
        f"{{",
        f"    Self::blitz_check(buffer)?;",
        f"    Ok({ d['fq_name'] }Viewer::new_blitz_view(buffer))",
        f"}}",
    )

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_builder(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"pub struct { d['name'] }Builder<'a, Backend> {{")
    b.add_line(f"    backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>,")
    b.add_line(f"    buffer: &'a mut [u8],")
    b.add_line(f"    self_offset: u32,")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"impl<Backend> bzb::BlitzSized for { d['name'] }Builder<'_, Backend> {{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn get_blitz_size() -> u32 {{")
    b.add_line(f"        return { d['size'] };")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"impl<'a, Backend> bzb::BlitzBuilder<'a, Backend> for { d['name'] }Builder<'a, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn new_blitz_builder(backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>, buffer: &'a mut [u8], self_offset: u32) -> Self {{")
    b.add_line(f"        { d['name'] }Builder {{")
    b.add_line(f"            backend,")
    b.add_line(f"            buffer,")
    b.add_line(f"            self_offset,")
    b.add_line(f"        }}")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCopyFrom raw
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<&{ d['name'] }> for { d['name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn copy_from(&mut self, other: &{ d['name'] }) {{")
    b.add_line(f"        match other {{")
    b.increment_indent(3)
    b.add_line(f"{ d['name'] }::_None => self.clear(),")

    for variant in d["variants"]:
        b.add_line(f"{ d['name'] }::{ variant['name'] }(other) => self.make_{ variant['name'] }().copy_from(other),")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCopyFrom view
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<&{ d['name'] }Viewer<'_>> for { d['name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.add_line(f"    #[inline(always)]")
    b.add_line(f"    fn copy_from(&mut self, other: &{ d['name'] }Viewer<'_>) {{")
    b.add_line(f"        match other {{")
    b.increment_indent(3)
    b.add_line(f"{ d['name'] }Viewer::_None => self.clear(),")

    for variant in d["variants"]:
        b.add_line(f"{ d['name'] }Viewer::{ variant['name'] }(other) => self.make_{ variant['name'] }().copy_from(other),")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # General methods
    b.add_line(f"impl<'a, Backend> { d['name'] }Builder<'a, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"pub fn clear(&mut self) {{")
    b.add_line(f"    unsafe {{")
    b.add_line(f"        self.buffer")
    b.add_line(f"            .get_unchecked_mut(..{ d['enum_size'] })")
    b.add_line(f"            .copy_from_slice(&0u{ d['enum_size'] * 8 }.to_le_bytes());")
    b.add_line(f"    }}")
    b.add_line(f"}}")
    b.skip_line(1)

    for variant in d["variants"]:
        b.add_line(f"#[inline(always)]")
        b.add_line(f"pub fn make_{ variant['name'] }(&mut self) -> { variant['fq_name'] }Builder<'a, Backend> {{")
        b.add_line(f"    unsafe {{ self.buffer.get_unchecked_mut(..{ d['enum_size']}).copy_from_slice(&{ variant['tag'] }u{ d['enum_size'] * 8 }.to_le_bytes()); }}")
        b.add_line(f"    let buffer = unsafe {{")
        b.add_line(f"        &mut *std::ptr::slice_from_raw_parts_mut(self.buffer.as_mut_ptr().add({ d['enum_size'] }), { variant['size'] })")
        b.add_line(f"    }};")
        b.add_line(f"    { variant['fq_name'] }Builder::new_blitz_builder(")
        b.add_line(f"        self.backend,")
        b.add_line(f"        buffer,")
        b.add_line(f"        self.self_offset + { d['enum_size'] },")
        b.add_line(f"    )")
        b.add_line(f"}}")
        b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_viewer(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"#[derive(Debug, PartialEq, PartialOrd)]")
    b.add_line(f"pub enum { d['name'] }Viewer<'a> {{")
    b.increment_indent()
    b.add_line(f"_None,")

    for variant in d["variants"]:
        b.add_line(f"{ variant['name'] }({ variant['fq_name'] }Viewer<'a>),")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    enum_ty = f"u{ d['enum_size'] * 8 }"
    b.add_line(f"impl<'a> bzb::BlitzViewer<'a> for { d['name'] }Viewer<'a>")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn new_blitz_view(buffer: &'a [u8]) -> Self {{")
    b.increment_indent()

    b.add_line(f"let tag = unsafe {{ { enum_ty }::read_le_bytes(buffer) }};")
    b.add_line(f"match tag {{")
    b.increment_indent()

    for variant in d["variants"]:
        b.add_line(
            f"{ variant['tag'] }{ enum_ty } => { d['name'] }Viewer::{ variant['name'] }({ variant['fq_name'] }Viewer::new_blitz_view(unsafe {{ buffer.get_unchecked({ d['enum_size'] }..) }})),"
        )

    b.add_line(f"_ => { d['name'] }Viewer::_None,")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)
