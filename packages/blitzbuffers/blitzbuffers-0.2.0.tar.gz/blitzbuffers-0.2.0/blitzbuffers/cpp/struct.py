from .common import PRIMITIVE_TYPES, sanitize_name
from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition, is_enum, is_struct, is_tagged_union


#
# Forward declaration
#
def add_forward_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"// Struct forward declaration { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.add_line(f"    class Raw;")
    b.add_line(f"    class Viewer;")
    b.skip_line(1)
    b.add_line(f"    template <class>")
    b.add_line(f"    class Builder;")
    b.add_line(f"}}")


#
# Declaration
#
def add_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"// Struct declaration { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"constexpr static bzb::offset_t blitz_size()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['size'] };")
    b.add_line(f"}}")
    b.skip_line(1)

    add_raw_declaration(b, d, ctx)
    add_viewer_declaration(b, d, ctx)
    add_builder_declaration(b, d, ctx)

    b.add_line(f"template <class BufferBackend>")
    b.add_line(f"static Builder<BufferBackend> new_on(BufferBackend& backend)")
    b.add_line(f"{{")
    b.add_line(f"    auto offset = backend.get_size();")
    b.add_line(f"    auto buffer = backend.get_new_buffer({ d['fq_name'] }::blitz_size());")
    b.add_line(f"    return Builder(backend, buffer, offset);")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"static bool check(const uint8_t* buffer, const bzb::offset_t length)")
    b.add_line(f"{{")
    b.add_line(f"    return { d['fq_name'] }::Viewer::check(buffer, length);")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"static std::optional<Viewer> view(const uint8_t* buffer, const bzb::offset_t length)")
    b.add_line(f"{{")
    b.add_line(f"    if (!{ d['fq_name'] }::check(buffer, length)) {{")
    b.add_line(f"        return std::nullopt;")
    b.add_line(f"    }}")
    b.add_line(f"    return {{ Viewer(buffer) }};")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"static Viewer view_unchecked(const uint8_t* buffer)")
    b.add_line(f"{{")
    b.add_line(f"    return Viewer(buffer);")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"static { d['fq_name'] }::Raw raw()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['fq_name'] }::Raw {{}};")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"static { d['fq_name'] }::Raw raw({ d['fq_name'] }::Raw _raw)")
    b.add_line(f"{{")
    b.add_line(f"    return _raw;")
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")


#
# Definition
#
def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"// Struct definition { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()
    add_viewer_definition(b, d, ctx)
    add_builder_definition(b, d, ctx, True)
    b.decrement_indent()
    b.add_line(f"}}")


#
# Raw
#
def get_raw_field_type(ty: str, ctx: DefinitionContext, vector_ty="std::vector"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return f"{ vector_ty }<{ get_raw_field_type(ty['inner'], ctx, vector_ty) }>"

    if ty == "string":
        return "std::string"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        if is_struct(other):
            return other["fq_name"] + "::Raw"
        elif is_tagged_union(other):
            return other["fq_name"] + "::raw_variant_t"
        else:
            return other["fq_name"]

    if ty in PRIMITIVE_TYPES:
        return PRIMITIVE_TYPES[ty]
    return ty


def add_raw_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"class Raw {{")
    b.add_line(f"public:")
    b.increment_indent()

    for field in d["fields"]:
        match field["kind"]:

            case "vector":
                ty = get_raw_field_type(field["type"], ctx)
                b.add_line(f"{ ty } { sanitize_name(field['name']) };")

            case "string" | "primitive" | "embed":
                b.add_line(f"{ get_raw_field_type(field['type'], ctx) } { sanitize_name(field['name']) };")

            case _:
                b.add_line(f"// unknown kind { field['kind'] } { sanitize_name(field['name']) }")

    # Add default constructor if it's an empty struct
    if len(d["fields"]) == 0:
        b.add_line(f"Raw() {{}}")

    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)


#
# Viewer
#
def get_viewer_field_type(ty: str, ctx: DefinitionContext, vector_format_str="bzb::Vector<%s>"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return vector_format_str % get_viewer_field_type(ty["inner"], ctx, vector_format_str)

    if ty == "string":
        return "bzb::StringPointer<const char*>"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        if is_enum(other):
            return f"bzb::PrimitiveContainer<{ other['fq_name'] }, const uint8_t*>"
        else:
            return other["fq_name"] + "::Viewer"

    if ty in PRIMITIVE_TYPES:
        return f"bzb::PrimitiveContainer<{ PRIMITIVE_TYPES[ty] }, const uint8_t*>"

    return ty


def add_viewer_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext, viewer_name="Viewer", raw_path=None):
    b.add_line(f"class { viewer_name }")
    b.add_line(f"{{")

    # private fields and methods
    b.add_line(f"private:")
    b.increment_indent()

    b.add_line(f"const uint8_t* __buffer;")
    b.skip_line(1)

    for field in d["fields"]:
        match field["kind"]:
            case "string" | "vector":
                b.add_line(f"bzb::PrimitiveContainer<bzb::offset_t, const uint8_t*> _get_offset_{ field['name'] }() const")
                b.add_line(f"{{")
                b.add_line(f"    return {{ this->__buffer + { field['offset'] } }};")
                b.add_line(f"}}")
                b.skip_line(1)

            case "primitive":
                return_ty = get_viewer_field_type(field["type"], ctx)
                b.add_line(f"{ return_ty } _get_container_{ field['name'] }() const")
                b.add_line(f"{{")
                b.add_line(f"    return { return_ty }(this->__buffer + { field['offset'] });")
                b.add_line(f"}}")
                b.skip_line(1)

    b.decrement_indent()
    b.skip_line(1)

    # Public fields and methods
    b.add_line(f"public:")
    b.increment_indent()

    b.add_line(f"constexpr static bzb::offset_t blitz_size()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['size'] };")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"{ viewer_name }(const uint8_t* buffer);")
    b.skip_line(1)

    for field in d["fields"]:
        match field["kind"]:
            case "string":
                b.add_line(f"const char* get_{ field['name'] }() const")
                b.add_line(f"{{")
                b.add_line(f"    if (this->_get_offset_{ field['name'] }() == 0)")
                b.add_line(f"    {{")
                b.add_line(f'        return "";')
                b.add_line(f"    }}")
                b.add_line(f"    return (const char*)(__buffer + this->_get_offset_{ field['name'] }() + { field['offset'] });")
                b.add_line(f"}}")
                b.skip_line(1)

            case "primitive":
                return_ty = field["type"]
                if return_ty in PRIMITIVE_TYPES:
                    return_ty = PRIMITIVE_TYPES[return_ty]

                b.add_line(f"{ return_ty } get_{ field['name'] }() const")
                b.add_line(f"{{")
                b.add_line(f"    return this->_get_container_{ field['name'] }().value();")
                b.add_line(f"}}")
                b.skip_line(1)

            case _:
                return_ty = get_viewer_field_type(field["type"], ctx)
                b.add_line(f"{ return_ty } get_{ field['name'] }() const")
                b.add_line(f"{{")
                b.add_line(f"    return { return_ty }(this->__buffer + { field['offset'] });")
                b.add_line(f"}}")
                b.skip_line(1)

    b.skip_line(1)

    if raw_path != None:
        b.add_line(f"static { raw_path } raw()")
        b.add_line(f"{{")
        b.add_line(f"    return { raw_path } {{}};")
        b.add_line(f"}}")
        b.skip_line(1)

        b.add_line(f"static { raw_path } raw({ raw_path } _raw)")
        b.add_line(f"{{")
        b.add_line(f"    return _raw;")
        b.add_line(f"}}")
        b.skip_line(1)

    b.add_line(f"static bool check(const uint8_t* buffer, const bzb::offset_t length)")
    b.add_line(f"{{")
    b.increment_indent()

    checks = []
    for field in d["fields"]:
        match field["kind"]:
            case "embed":
                other = ctx["def_mapping"][field["type"]]
                checks.append(f"{other['fq_name']}::check(buffer + { field['offset'] }, length - { field['offset']})")
            case "string":
                checks.append(f"bzb::check_string(buffer + { field['offset'] }, length - { field['offset']})")
            case "vector":
                checks.append(
                    f"bzb::check_vector<{ get_viewer_field_type(field['type']['inner'], ctx, 'bzb::Vector<%s>') }>(buffer + { field['offset'] }, length - { field['offset']})"
                )
            case "primitive":
                pass

    b.add_line_without_newline(f"return length >= { d['size'] }")
    b.increment_indent()
    for check in checks:
        b.add_line_pre_newline(f"&& {check}")
    b.add_text(f";\n")
    b.decrement_indent()

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Equality operator
    b.add_line(f"friend bool operator==(const { viewer_name }& lhs, const { viewer_name }& rhs);")
    b.skip_line(1)

    # Stream insertion operator
    b.add_line(f"friend std::ostream& operator<<(std::ostream& os, const { viewer_name }& value);")
    b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}};")


def add_viewer_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext, viewer_name="Viewer"):
    b.add_line(f"inline { viewer_name }::{ viewer_name }(const uint8_t* _buffer)")
    b.add_line(f": __buffer(_buffer)")
    b.add_line(f"{{}}")
    b.skip_line(1)

    # Equality operator
    b.add_line(f"inline bool operator==(const { viewer_name }& lhs, const { viewer_name }& rhs)")
    b.add_line(f"{{")
    b.increment_indent()
    b.add_line(f"return true")
    b.increment_indent()

    for field in d["fields"]:
        b.add_line(f"&& lhs.get_{ field['name'] }() == rhs.get_{ field['name'] }()")

    b.decrement_indent()
    b.add_line(f";")
    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Stream insertion operator
    b.add_line(f"inline std::ostream& operator<<(std::ostream& os, const { viewer_name }& value)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"os << \"{ d['name'] }{{\";")

    for field in d["fields"]:
        match field["kind"]:
            case "vector":
                b.add_line(f'os << "{ field["name"] }=" << value.get_{ field["name"] }() << "; ";')
            case "string":
                b.add_line(f'os << "{ field["name"] }=\\"" << value.get_{ field["name"] }() << "\\"; ";')
            case _:
                if field["type"] == "u8" or field["type"] == "i8":
                    # If it's a byte-size, printing it will result in char rendering instead of a number
                    b.add_line(f'os << "{ field["name"] }=" << (int)(value.get_{ field["name"] }()) << "; ";')
                else:
                    b.add_line(f'os << "{ field["name"] }=" << value.get_{ field["name"] }() << "; ";')

    b.add_line(f'os << "}}";')
    b.add_line(f"return os;")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


#
# Builder
#
def get_builder_field_type(ty: str, ctx: DefinitionContext, vector_format_str="bzb::VectorWriter<%s, BufferBackend>"):
    if isinstance(ty, dict) and "name" in ty:
        ty = ty["name"]

    if isinstance(ty, dict) and "inner" in ty:
        return vector_format_str % get_builder_field_type(ty["inner"], ctx, vector_format_str)

    if ty == "string":
        return "bzb::StringWriter<BufferBackend>"

    if ty[0].isupper():
        other = ctx["def_mapping"][ty]
        if is_enum(other):
            return f"bzb::PrimitiveContainer<{ other['fq_name'] }, uint8_t*>"
        else:
            return other["fq_name"] + "::Builder<BufferBackend>"

    if ty in PRIMITIVE_TYPES:
        return f"bzb::PrimitiveContainer<{PRIMITIVE_TYPES[ty]}, uint8_t*>"

    return ty


def add_builder_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"template <class BufferBackend>")
    b.add_line(f"class Builder : bzb::BufferWriterBase<BufferBackend>")
    b.add_line(f"{{")
    b.add_line(f"private:")

    b.increment_indent()
    for field in d["fields"]:
        if field["kind"] in ["string", "vector"]:
            b.add_line(f"bzb::PrimitiveContainer<bzb::offset_t, uint8_t*> _offset_{ field['name'] }()")
            b.add_line(f"{{")
            b.add_line(f"    return {{ this->__buffer + { field['offset'] } }};")
            b.add_line(f"}}")
            b.skip_line(1)

    b.decrement_indent()
    b.skip_line(1)

    b.add_line(f"public:")

    b.increment_indent()
    b.add_line(f"constexpr static bzb::offset_t blitz_size()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['size'] };")
    b.add_line(f"}}")
    b.skip_line(1)

    for field in d["fields"]:
        match field["kind"]:
            case "primitive":
                b.add_line(f"{ get_builder_field_type(field['type'], ctx) } { sanitize_name(field['name']) }()")
                b.add_line(f"{{")
                b.add_line(f"    return {{ this->__buffer + { field['offset'] } }};")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"void set_{ field['name'] }({ get_raw_field_type(field['type'], ctx) } value)")
                b.add_line(f"{{")
                b.add_line(f"    this->{ sanitize_name(field['name']) }() = value;")
                b.add_line(f"}}")
                b.skip_line(1)

            case "embed":
                b.add_line(f"{ get_builder_field_type(field['type'], ctx) } { sanitize_name(field['name']) }()")
                b.add_line(f"{{")
                b.add_line(f"    return {{ this->__backend, this->__buffer + { field['offset'] }, this->__self_offset + { field['offset'] } }};")
                b.add_line(f"}}")
                b.skip_line(1)

            case "string":
                b.add_line_unindented(f"#ifdef __cpp_lib_string_view")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }(std::string_view value)")
                b.add_line(f"{{")
                b.add_line(f"    this->_offset_{ field['name'] }() = this->__backend.add_string(value.data(), value.length()) - this->__self_offset - { field['offset'] };")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line_unindented(f"#else // __cpp_lib_string_view")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }(const std::string& value)")
                b.add_line(f"{{")
                b.add_line(f"    this->_offset_{ field['name'] }() = this->__backend.add_string(value.c_str(), value.size()) - this->__self_offset - { field['offset'] };")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }(const char* value)")
                b.add_line(f"{{")
                b.add_line(f"    this->_offset_{ field['name'] }() = this->__backend.add_string(value, strlen(value)) - this->__self_offset - { field['offset'] };")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line_unindented(f"#endif // __cpp_lib_string_view")
                b.skip_line(1)

            case "vector":
                ty = get_builder_field_type(field["type"], ctx)
                ptr_ty = get_builder_field_type(field["type"], ctx, "bzb::VectorWriterPointer<%s, BufferBackend>")
                raw_vec_ty = get_raw_field_type(field["type"], ctx)
                raw_vec_inner_ty = get_raw_field_type(field["type"]["inner"], ctx)
                raw_span_ty = get_raw_field_type(field["type"], ctx, "std::span")
                raw_init_ty = get_raw_field_type(field["type"], ctx, "std::initializer_list")

                b.add_line(f"{ ty } insert_{ field['name'] }(bzb::offset_t _size)")
                b.add_line(f"{{")
                b.add_line(f"    return { ty }::make_and_set_offset(this->__backend, _size, this->__self_offset + { field['offset'] }, this->_offset_{ field['name'] }());")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line_unindented(f"#ifdef __cpp_lib_span")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }({ raw_span_ty } data)")
                b.add_line(f"{{")
                b.add_line(f"    auto vector_ptr = { ptr_ty }(this->__backend, this->_offset_{ field['name'] }(), this->__self_offset + { field['offset'] });")
                b.add_line(f"    vector_ptr.insert(data);")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line_unindented(f"#endif // __cpp_lib_span")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }(const { raw_vec_ty }& _raw_vec)")
                b.add_line(f"{{")
                b.add_line(f"    auto vector_ptr = { ptr_ty }(this->__backend, this->_offset_{ field['name'] }(), this->__self_offset + { field['offset'] });")
                b.add_line(f"    vector_ptr.insert(_raw_vec);")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }({ raw_init_ty } data)")
                b.add_line(f"{{")
                b.add_line(f"    auto vector_ptr = { ptr_ty }(this->__backend, this->_offset_{ field['name'] }(), this->__self_offset + { field['offset'] });")
                b.add_line(f"    vector_ptr.insert(data);")
                b.add_line(f"}}")
                b.skip_line(1)

                b.add_line(f"void insert_{ field['name'] }(const { raw_vec_inner_ty }* data, const bzb::offset_t data_length)")
                b.add_line(f"{{")
                b.add_line(f"    auto vector_ptr = { ptr_ty }(this->__backend, this->_offset_{ field['name'] }(), this->__self_offset + { field['offset'] });")
                b.add_line(f"    vector_ptr.insert(data, data_length);")
                b.add_line(f"}}")
                b.skip_line(1)

    b.add_line(f"Builder<BufferBackend>& operator=(Raw _raw);")
    b.skip_line(1)
    b.add_line(f"Builder(BufferBackend& _backend, uint8_t* _buffer, bzb::offset_t _self_offset);")
    b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}};")


def add_builder_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext, raw_assignments=False):
    b.add_line(f"template <class BufferBackend>")
    b.add_line(f"inline Builder<BufferBackend>::Builder(BufferBackend& _backend, uint8_t* _buffer, bzb::offset_t _self_offset)")
    b.add_line(f": bzb::BufferWriterBase<BufferBackend>(_backend, _buffer, _self_offset)")
    b.add_line(f"{{}}")
    b.skip_line(1)

    if raw_assignments:
        b.add_line(f"template <class BufferBackend>")
        b.add_line(f"inline Builder<BufferBackend>& Builder<BufferBackend>::operator=(Raw _raw)")
        b.add_line(f"{{")
        b.increment_indent()

        for field in d["fields"]:
            if field["kind"] in ["string", "vector"]:
                b.add_line(f"this->insert_{ field['name'] }(_raw.{ field['name'] });")
            else:
                b.add_line(f"this->{ sanitize_name(field['name']) }() = _raw.{ sanitize_name(field['name']) };")

        b.add_line(f"return *this;")

        b.decrement_indent()
        b.add_line(f"}}")
