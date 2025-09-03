from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition, is_enum
from .common import PRIMITIVE_TYPES, get_fq_name_from_type, sanitize_name


#
# Definition
#
def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    add_raw(b, d, ctx)
    add_raw_methods(b, d, ctx)
    add_builder(b, d, ctx)
    add_builder_methods(b, d, ctx)
    add_viewer(b, d, ctx)
    add_viewer_methods(b, d, ctx)


def add_raw(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"#[derive(Debug, Clone, Default, PartialEq, PartialOrd)]")
    b.add_line(f"pub struct { d['fq_name'] } {{")
    b.increment_indent()

    for field in d["fields"]:
        b.add_line(f"pub { sanitize_name(field['name']) }: { get_raw_field_type(field['type'], ctx) },")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def get_raw_field_type(ty: str, ctx: DefinitionContext, vector_format_str="Vec<%s>"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return vector_format_str % get_raw_field_type(ty["inner"], ctx, vector_format_str)

    if ty == "string":
        return "String"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        return other["fq_name"]

    if ty in PRIMITIVE_TYPES:
        return PRIMITIVE_TYPES[ty]

    return ty


def add_raw_methods(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    # BlitzSized
    b.add_lines(
        f"impl bzb::BlitzSized for { d['fq_name'] } {{",
        f"    #[inline(always)]",
        f"    fn get_blitz_size() -> u32 {{",
        f"        { d['size'] }",
        f"    }}",
        f"}}",
    )
    b.skip_line(1)

    # BlitzCalcSize
    b.add_line(f"impl bzb::BlitzCalcSize for { d['fq_name'] } {{")
    b.increment_indent()
    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn calc_blitz_size(&self) -> u32")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"let mut size = 0;")

    for field in d["fields"]:
        sanitized = sanitize_name(field["name"])
        b.add_line(f"size += self.{ sanitized }.calc_blitz_size();")

    b.add_line(f"size")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Directly to blitz buffer
    b.add_lines(
        f"impl { d['fq_name'] } {{",
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
    b.add_line(f"impl bzb::BlitzCheck for { d['fq_name'] } {{")
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

    for field in d["fields"]:
        match field["kind"]:
            case "embed" | "string" | "primitive":
                b.add_line(f"{ get_raw_field_type(field['type'], ctx) }::blitz_check(unsafe {{ buffer.get_unchecked({ field['offset'] }..) }})")
                b.add_line(f"    .map_err(|err| format!(\"[{ field['name'] }] {{}}\", err))?;")
            case "vector":
                ty = get_raw_field_type(field["type"], ctx, vector_format_str="BlitzVector::<%s>")
                b.add_line(f"{ ty }::blitz_check(unsafe {{ buffer.get_unchecked({ field['offset'] }..) }})")
                b.add_line(f"    .map_err(|err| format!(\"[{ field['name'] }] {{}}\", err))?;")
            case _:
                raise Exception(f"Unhandled field kind in check: { field['kind'] }")

    b.add_line(f"Ok(())")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Impl methods
    b.add_line(f"impl { d['fq_name'] } {{")
    b.increment_indent()

    b.add_lines(
        f"#[inline(always)]",
        f"pub fn new_on<'a, Backend>(",
        f"    backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>,",
        f") -> { d['fq_name'] }Builder<'a, Backend>",
        f"where",
        f"    Backend: bzb::BlitzBufferBackend,",
        f"{{",
        f"    let offset = backend.get_size();",
        f"    let buffer = backend.get_new_buffer({ d['size'] });",
        f"    { d['fq_name'] }Builder::new_blitz_builder(backend, buffer, offset)",
        f"}}",
    )
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


# Add builder struct and methods
def add_builder(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"pub struct { d['fq_name'] }Builder<'a, Backend> {{")
    b.increment_indent()

    b.add_line(f"backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>,")
    b.add_line(f"buffer: &'a mut [u8],")
    b.add_line(f"self_offset: u32,")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_lines(
        f"impl<Backend> bzb::BlitzSized for { d['fq_name'] }Builder<'_, Backend> {{",
        f"    #[inline(always)]",
        f"    fn get_blitz_size() -> u32 {{",
        f"        { d['size'] }",
        f"    }}",
        f"}}",
    )
    b.skip_line(1)

    b.add_line(f"impl<'a, Backend> bzb::BlitzBuilder<'a, Backend> for { d['fq_name'] }Builder<'a, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    # Constructor
    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn new_blitz_builder(")
    b.add_line(f"    backend: &'a bzb::UnsafeBlitzBufferBackend<Backend>,")
    b.add_line(f"    buffer: &'a mut [u8],")
    b.add_line(f"    self_offset: u32,")
    b.add_line(f") -> Self {{")
    b.increment_indent()

    b.add_line(f"{ d['fq_name'] }Builder {{")
    b.increment_indent()
    b.add_line(f"backend,")
    b.add_line(f"buffer,")
    b.add_line(f"self_offset,")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCopyFrom raw method
    # Reference
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<&{ d['fq_name'] }> for { d['fq_name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn copy_from(&mut self, other: &{ d['fq_name'] }) {{")
    b.increment_indent()

    for field in d["fields"]:
        sanitized_name = sanitize_name(field["name"])
        match field["kind"]:
            case "primitive":
                b.add_line(f"self.set_{ field['name'] }(other.{ sanitized_name });")
            case "string":
                b.add_line(f"self.insert_{ field['name'] }(&other.{ sanitized_name });")
            case "embed":
                b.add_line(f"self.{ sanitized_name }().copy_from(&other.{ sanitized_name });")
            case "vector":
                b.add_line(f"self.copy_from_{ field['name'] }(&other.{ sanitized_name });")
            case kind:
                b.add_line(f"todo!(\"Unsupported blitzbuffers kind '{kind}' for field: { field['name'] }\");")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Owned
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<{ d['fq_name'] }> for { d['fq_name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn copy_from(&mut self, other: { d['fq_name'] }) {{")
    b.increment_indent()
    b.add_line(f"self.copy_from(&other);")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # BlitzCopyFrom view method
    # Refenrence
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<&{ d['fq_name'] }Viewer<'_>> for { d['fq_name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn copy_from(&mut self, other: &{ d['fq_name'] }Viewer<'_>) {{")
    b.increment_indent()

    for field in d["fields"]:
        sanitized_name = sanitize_name(field["name"])
        match field["kind"]:
            case "primitive":
                b.add_line(f"self.set_{ field['name'] }(other.get_{ field['name'] }());")
            case "string":
                b.add_line(f"self.insert_{ field['name'] }_bytes(other.get_{ field['name'] }_bytes());")
            case "embed":
                b.add_line(f"self.{ sanitized_name }().copy_from(&other.get_{ field['name'] }());")
            case "vector":
                b.add_line(f"self.copy_from_{ field['name'] }(other.get_{ field['name'] }());")
            case kind:
                b.add_line(f"todo!(\"Unsupported blitzbuffers kind '{kind}' for field: { field['name'] }\");")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Owned
    b.add_line(f"impl<Backend> bzb::BlitzCopyFrom<{ d['fq_name'] }Viewer<'_>> for { d['fq_name'] }Builder<'_, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn copy_from(&mut self, other: { d['fq_name'] }Viewer<'_>) {{")
    b.increment_indent()
    b.add_line(f"self.copy_from(&other);")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_builder_methods(b: OutputBuilder, d: Definition, ctx: DefinitionContext):

    b.add_line(f"impl<'a, Backend> { d['fq_name'] }Builder<'a, Backend>")
    b.add_line(f"where")
    b.add_line(f"    Backend: bzb::BlitzBufferBackend,")
    b.add_line(f"{{")
    b.increment_indent()

    for field in d["fields"]:
        match field["kind"]:
            case "embed":
                other_fq_name = get_fq_name_from_type(field["type"], ctx)

                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn { sanitize_name(field['name']) }(&mut self) -> { get_builder_field_type(field['type'], ctx) } {{")
                b.increment_indent()
                b.add_line(f"{ other_fq_name }Builder::new_blitz_builder(")
                b.increment_indent()
                b.add_line(f"self.backend,")
                b.add_line(f"unsafe {{ &mut *std::ptr::slice_from_raw_parts_mut(self.buffer.as_mut_ptr().add({ field['offset'] }), { field['size'] }) }},")
                b.add_line(f"self.self_offset + { field['offset']},")
                b.decrement_indent()
                b.add_line(f")")
                b.decrement_indent()
                b.add_line(f"}}")

            case "primitive":
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn set_{ field['name'] }(&mut self, v: { get_fq_name_from_type(field['type'], ctx) }) {{")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        v.write_le_bytes(")
                b.add_line(f"            self.buffer.get_unchecked_mut({ field['offset'] }..{ field['offset'] + field['size'] })")
                b.add_line(f"        );")
                b.add_line(f"    }}")
                b.add_line(f"}}")

            case "string":
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn insert_{ field['name'] }(&mut self, v: impl AsRef<str>) {{")
                b.add_line(f"    let offset = self.backend.add_string(v) - self.self_offset - { field['offset'] };")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        self.buffer")
                b.add_line(f"            .get_unchecked_mut({ field['offset'] }..{ field['offset'] + field['size'] })")
                b.add_line(f"            .copy_from_slice(&offset.to_le_bytes());")
                b.add_line(f"    }}")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn insert_{ field['name'] }_bytes(&mut self, v: &[u8]) {{")
                b.add_line(f"    let offset = self.backend.add_string_bytes(v) - self.self_offset - { field['offset'] };")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        self.buffer")
                b.add_line(f"            .get_unchecked_mut({ field['offset'] }..{ field['offset'] + field['size'] })")
                b.add_line(f"            .copy_from_slice(&offset.to_le_bytes());")
                b.add_line(f"    }}")
                b.add_line(f"}}")

            case "vector":

                # Get pointer
                ty = get_builder_field_type(field["type"], ctx, "bzb::BlitzVectorWriterPointer<'a, Backend, %s>")
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn ptr_{ field['name'] }(&mut self)")
                b.add_line(f"-> { ty } {{")
                b.add_line(f"    bzb::BlitzVectorWriterPointer::new_at_offset(self.backend, self.buffer, self.self_offset, { field['offset'] })")
                b.add_line(f"}}")
                b.skip_line(1)

                # Insert
                ty = get_builder_field_type(field["type"], ctx, "bzb::BlitzVectorWriter<'a, Backend, %s>")
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn insert_{ field['name'] }(")
                b.add_line(f"    &mut self,")
                b.add_line(f"    len: u32,")
                b.add_line(f") -> { ty } {{")
                b.add_line(f"    let offset = self.backend.get_size() - self.self_offset - { field['offset'] };")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        self.buffer")
                b.add_line(f"            .get_unchecked_mut({ field['offset'] }..{ field['offset'] + field['size'] })")
                b.add_line(f"            .copy_from_slice(&offset.to_le_bytes());")
                b.add_line(f"    }}")
                b.add_line(f"    bzb::BlitzVectorWriter::new(self.backend, len)")
                b.add_line(f"}}")
                b.skip_line(1)

                # Insert iter
                iter_ty = get_builder_field_type(field["type"]["inner"], ctx, "bzb::BlitzIterWriterPointer<'a, Backend, bzb::BlitzIterWriter<'a, Backend, %s>>")
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn insert_{ field['name'] }_iter(")
                b.add_line(f"    &mut self,")
                b.add_line(f"    len: u32,")
                b.add_line(f") -> bzb::BlitzIterWriter<'a, Backend, { iter_ty }> {{")
                b.add_line(f"    let ptr_buffer = unsafe {{ &mut *std::ptr::slice_from_raw_parts_mut(self.buffer.as_mut_ptr().add({ field['offset'] }), { field['size'] }) }};")
                b.add_line(f"    bzb::BlitzIterWriter::alloc_with_len(self.backend, ptr_buffer, self.self_offset + { field['offset'] }, len)")
                b.add_line(f"}}")
                b.skip_line(1)

                # Insert iter zip
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn insert_{ field['name'] }_iter_zip<U>(")
                b.add_line(f"    &mut self,")
                b.add_line(f"    other_iter: U,")
                b.add_line(f") -> Zip<U, bzb::BlitzIterWriter<'a, Backend, { iter_ty }>>")
                b.add_line(f"where")
                b.add_line(f"    U: ExactSizeIterator")
                b.add_line(f"{{")
                b.add_line(f"    let iter = self.insert_{ field['name'] }_iter(other_iter.len() as u32);")
                b.add_line(f"    other_iter.zip(iter)")
                b.add_line(f"}}")
                b.skip_line(1)

                # Copy from methods
                inner_ty = get_inner_type(field["type"])
                if True or inner_ty[0].islower() and inner_ty != "string":
                    b.add_line(f"#[inline(always)]")

                    nest_types = []
                    current_ty = field["type"]
                    while isinstance(current_ty, dict) and "inner" in current_ty:
                        nest_types.append(f"U{ len(nest_types) + 1 }")
                        current_ty = current_ty["inner"]
                    nest_types.append(f"U{ len(nest_types) + 1 }")

                    b.add_line(f"pub fn copy_from_{ field['name'] }<{ ', '.join(nest_types) }>(&mut self, other: U1)")
                    b.add_line(f"where")
                    b.increment_indent()

                    for ty1, ty2 in zip(nest_types[:-1], nest_types[1:]):
                        b.add_line(f"{ ty1 }: IntoIterator<Item = { ty2 }>,")
                        b.add_line(f"{ ty1 }::IntoIter: ExactSizeIterator,")

                    b.add_line(f"{ get_builder_field_type(inner_ty, ctx) }: BlitzCopyFrom<{ nest_types[-1] }>,")

                    b.decrement_indent()
                    b.add_line(f"{{")
                    b.increment_indent()

                    b.add_line(f"self.ptr_{ field['name'] }().copy_from(other);")

                    b.decrement_indent()
                    b.add_line(f"}}")

        b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}}")


def get_builder_field_type(ty: str, ctx: DefinitionContext, vector_format_str="Vec<%s>"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return vector_format_str % get_builder_field_type(ty["inner"], ctx, vector_format_str)

    if ty == "string":
        return "bzb::BlitzStringWriter<'a, Backend>"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        return other["fq_name"] + "Builder<'a, Backend>"

    if ty in PRIMITIVE_TYPES:
        return f"bzb::BlitzPrimitiveWriter<'a, {PRIMITIVE_TYPES[ty]}>"

    return ty


def get_inner_type(ty):
    if isinstance(ty, dict) and "inner" in ty:
        return get_inner_type(ty["inner"])
    return ty


def get_borrow_type(ty, ctx: DefinitionContext):
    if ty == "string":
        return "AsRef<str>"

    if isinstance(ty, dict):
        return f"Borrow<{ty['fq_name']}>"

    if ty in PRIMITIVE_TYPES:
        return f"Borrow<{PRIMITIVE_TYPES[ty]}>"

    return f"Borrow<{ ty }>"


def add_viewer(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"#[derive(Debug, PartialEq, PartialOrd)]")
    b.add_line(f"pub struct { d['fq_name'] }Viewer<'a> {{")
    b.increment_indent()

    b.add_line(f"buffer: &'a [u8],")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_lines(
        f"impl bzb::BlitzSized for { d['fq_name'] }Viewer<'_> {{",
        f"    #[inline(always)]",
        f"    fn get_blitz_size() -> u32 {{",
        f"        { d['size'] }",
        f"    }}",
        f"}}",
    )
    b.skip_line(1)

    b.add_line(f"impl<'a> bzb::BlitzViewer<'a> for { d['fq_name'] }Viewer<'a>")
    b.add_line(f"{{")
    b.increment_indent()

    # Constructor
    b.add_line(f"#[inline(always)]")
    b.add_line(f"fn new_blitz_view(buffer: &'a [u8]) -> Self {{")
    b.increment_indent()

    b.add_line(f"{ d['fq_name'] }Viewer {{")
    b.increment_indent()
    b.add_line(f"buffer,")
    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_viewer_methods(b: OutputBuilder, d: Definition, ctx: DefinitionContext):

    b.add_line(f"impl<'a> { d['fq_name'] }Viewer<'a>")
    b.add_line(f"{{")
    b.increment_indent()

    for field in d["fields"]:
        match field["kind"]:
            case "embed":
                ty = f"{ get_fq_name_from_type(field['type'], ctx) }Viewer"
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn get_{ field['name'] }(&self) -> { ty } {{")
                b.increment_indent()

                b.add_line(f"{ ty }::new_blitz_view(")
                b.increment_indent()
                b.add_line(f"unsafe {{ &*std::ptr::slice_from_raw_parts(self.buffer.as_ptr().add({ field['offset'] }), { field['size'] }) }},")
                b.decrement_indent()
                b.add_line(f")")

                b.decrement_indent()
                b.add_line(f"}}")
                pass

            case "primitive":
                ty = get_fq_name_from_type(field["type"], ctx)
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn get_{ field['name'] }(&self) -> { ty } {{")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        { ty }::read_le_bytes(")
                b.add_line(f"            self.buffer.get_unchecked({ field['offset'] }..{ field['offset'] + field['size'] })")
                b.add_line(f"        )")
                b.add_line(f"    }}")
                b.add_line(f"}}")

            case "string":
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn get_{ field['name'] }(&self) -> Result<&str, std::str::Utf8Error> {{")
                b.add_line(f"    let offset = unsafe {{ u32::read_le_bytes(self.buffer.get_unchecked({ field['offset'] }..{ field['offset'] + field['size'] })) }};")
                b.add_line(f"    if offset == 0 {{")
                b.add_line(f'        return Ok("");')
                b.add_line(f"    }}")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        std::ffi::CStr::from_ptr(self.buffer.as_ptr().add(offset as usize + { field['offset'] }) as *const i8)")
                b.add_line(f"            .to_str()")
                b.add_line(f"    }}")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn get_{ field['name'] }_bytes(&self) -> &[u8] {{")
                b.add_line(f"    let offset = unsafe {{ u32::read_le_bytes(self.buffer.get_unchecked({ field['offset'] }..{ field['offset'] + field['size'] })) }};")
                b.add_line(f"    if offset == 0 {{")
                b.add_line(f"        return &[];")
                b.add_line(f"    }}")
                b.add_line(f"    unsafe {{")
                b.add_line(f"        let ptr = self.buffer.as_ptr().add(offset as usize + { field['offset'] });")
                b.add_line(f"        let mut len = 0;")
                b.add_line(f"        while *ptr.add(len) != 0 {{")
                b.add_line(f"            len += 1;")
                b.add_line(f"        }}")
                b.add_line(f"        std::slice::from_raw_parts(ptr, len)")
                b.add_line(f"    }}")
                b.add_line(f"}}")

            case "vector":
                b.add_line(f"#[inline(always)]")
                b.add_line(f"pub fn get_{ field['name'] }(&self) -> { get_viewer_field_type(field['type'], ctx) } {{")
                b.add_line(f"    let field_buffer = unsafe {{ &self.buffer.get_unchecked({ field['offset'] }..) }};")
                b.add_line(f"    bzb::BlitzVector::new_blitz_view(field_buffer)")
                b.add_line(f"}}")

        b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}}")


def get_viewer_field_type(ty: str, ctx: DefinitionContext, vector_format_str="bzb::BlitzVector<%s>"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return vector_format_str % get_viewer_field_type(ty["inner"], ctx, vector_format_str)

    if ty == "string":
        return "&str"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        if is_enum(other):
            return other["fq_name"]
        else:
            return other["fq_name"] + "Viewer<'a>"

    if ty in PRIMITIVE_TYPES:
        return PRIMITIVE_TYPES[ty]

    return ty
