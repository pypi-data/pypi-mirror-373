from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition
from . import struct


#
# Forward declaration
#
def add_forward_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):

    b.add_line(f"// Tagged union variants forward declarations for { d['fq_name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()

    # The "none" viewer variant
    b.add_line(f"class _None")
    b.add_line(f"{{}};")
    b.skip_line(1)

    # Equality and stream insertion operators
    b.add_lines(
        f"inline bool operator==(const _None& lhs, const _None& rhs)",
        f"{{",
        f"    return true;",
        f"}}",
        f"",
        f"inline std::ostream& operator<<(std::ostream& os, const _None& value)",
        f"{{",
        f"    os << \"{ d['name'] }\";",
        f"    return os;",
        f"}}",
    )
    b.skip_line(1)

    for variant in d["variants"]:
        b.add_line(f"// Variant forward declaration { variant['name'] }")
        b.add_line(f"namespace _ns::{ variant['name'] }")
        b.add_line(f"{{")
        b.add_line(f"    class Raw;")
        b.skip_line(1)
        b.add_line(f"    template <class>")
        b.add_line(f"    class Builder;")
        b.add_line(f"}}")
        b.add_line(f"class { variant['name'] };")
        b.skip_line(1)

    b.add_line(f"// Tagged union forward declaration { d['name'] }")

    b.add_line(f"enum class _Tag : { d['enum_underlying_type'] };")
    b.add_line(f"class Viewer;")
    b.skip_line(1)
    b.add_line(f"template <class>")
    b.add_line(f"class Builder;")
    b.skip_line(1)

    view_variants = ", ".join([f"{ d['fq_name'] }::{ variant['name'] }" for variant in d["variants"]])
    raw_variants = ", ".join([f"{ d['fq_name'] }::_ns::{ variant['name'] }::Raw" for variant in d["variants"]])

    b.add_line(f"using view_variant_t = std::variant<{ d['fq_name'] }::_None, { view_variants }>;")
    b.add_line(f"using raw_variant_t  = std::variant<{ raw_variants }>;")
    b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


#
# Declaration
#
def add_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    sub_path = d["path"][:]
    sub_path.append(d["name"])

    b.add_line(f"// Tagged union variant declarations for { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()

    # The defined variants
    for variant in d["variants"]:
        b.add_line(f"// Variant declaration { variant['name'] }")
        b.add_line(f"namespace _ns::{ variant['name'] }")
        b.add_line(f"{{")
        b.increment_indent()

        struct.add_raw_declaration(b, variant["type"], ctx)
        struct.add_builder_declaration(b, variant["type"], ctx)

        b.decrement_indent()
        b.add_line(f"}}")

        b.skip_line(1)
        struct.add_viewer_declaration(b, variant["type"], ctx, viewer_name=variant["name"], raw_path=f"_ns::{ variant['name'] }::Raw")
        b.skip_line(1)

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"// Tagged union declaration { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"enum class _Tag : { d['enum_underlying_type'] }")
    b.add_line(f"{{")
    b.increment_indent()
    b.add_line(f"_None = 0,")

    for variant in d["variants"]:
        b.add_line(f"{ variant['name'] } = { variant['tag'] },")

    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)

    add_viewer_declaration(b, d, ctx)
    add_builder_declaration(b, d, ctx)
    b.skip_line(1)

    b.add_line(f"constexpr static bzb::offset_t blitz_size()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['size'] };")
    b.add_line(f"}}")
    b.skip_line(1)

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
    b.add_line(f"    return Viewer::check(buffer, length);")
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

    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)


def add_viewer_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"class Viewer {{")

    # Private fields and methods
    b.add_line(f"private:")
    b.increment_indent()
    b.add_line(f"const uint8_t* __buffer;")
    b.skip_line(1)

    b.add_line(f"inline bzb::PrimitiveContainer<_Tag, const uint8_t*> _tag() const")
    b.add_line(f"{{")
    b.add_line(f"    return {{ this->__buffer }};")
    b.add_line(f"}}")
    b.skip_line(1)

    for variant in d["variants"]:
        b.add_line(f"inline {d['fq_name']}::{variant['name']} { variant['snake_name'] }() const")
        b.add_line(f"{{")
        b.add_line(f"    return {{ this->__buffer + { d['enum_size'] } }};")
        b.add_line(f"}}")
        b.skip_line(1)

    b.decrement_indent()
    b.skip_line(1)

    # Public fields and methods
    b.add_line(f"public:")
    b.skip_line(1)
    b.increment_indent()

    b.add_line(f"Viewer(const uint8_t* buffer);")
    b.skip_line(1)

    # get function
    b.add_line(f"view_variant_t as_variant() const")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"switch (this->_tag())")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"case static_cast<_Tag>(0):")
    b.add_line(f"{{")
    b.add_line(f"    return {{}};")
    b.add_line(f"}}")

    for variant in d["variants"]:
        b.add_line(f"case _Tag::{ variant['name'] }:")
        b.add_line(f"{{")
        b.add_line(f"    return this->{ variant['snake_name'] }();")
        b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.add_line(f'throw std::invalid_argument("Unknown tag encountered.");')

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Direct accessors
    for variant in d["variants"]:
        b.add_line(f"inline std::optional<{d['fq_name']}::{variant['name']}> as_{ variant['name'] }()")
        b.add_line(f"{{")
        b.add_line(f"    if (this->_tag() != _Tag::{ variant['name'] }) {{")
        b.add_line(f"        return std::nullopt;")
        b.add_line(f"    }}")
        b.add_line(f"    return this->{ variant['snake_name'] }();")
        b.add_line(f"}}")
        b.skip_line(1)

    # Implicit conversion
    b.add_line(f"operator view_variant_t() const")
    b.add_line(f"{{")
    b.add_line(f"    return this->as_variant();")
    b.add_line(f"}}")
    b.skip_line(1)

    # Check function
    b.add_line(f"static bool check(const uint8_t* buffer, const bzb::offset_t length)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"if (length < { d['size'] }) {{")
    b.add_line(f"    return false;")
    b.add_line(f"}}")

    b.add_line(f"const auto tag = bzb::PrimitiveContainer<_Tag, const uint8_t*>(buffer);")
    b.add_line(f"switch (tag)")
    b.add_line(f"{{")
    b.increment_indent()

    for variant in d["variants"]:
        b.add_line(f"case _Tag::{ variant['name'] }:")
        b.increment_indent()
        b.add_line(f"return { d['fq_name'] }::{ variant['name'] }::check(buffer + { d['enum_size'] }, length - { d['enum_size'] });")
        b.decrement_indent()

    b.add_line(f"default:")
    b.increment_indent()
    b.add_line(f"return false;")
    b.decrement_indent()

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Equality operator
    b.add_line(f"friend bool operator==(const Viewer& lhs, const Viewer& rhs);")
    b.skip_line(1)

    # Stream insertion operator
    b.add_line(f"friend std::ostream& operator<<(std::ostream& os, const Viewer& value);")
    b.skip_line(1)

    # End class
    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)


def add_builder_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"template <class BufferBackend>")
    b.add_line(f"class Builder : bzb::BufferWriterBase<BufferBackend> {{")
    b.skip_line(1)

    b.add_line(f"private:")
    b.increment_indent()

    b.add_line(f"inline bzb::PrimitiveContainer<_Tag, uint8_t*> _tag()")
    b.add_line(f"{{")
    b.add_line(f"    return {{ this->__buffer }};")
    b.add_line(f"}}")
    b.skip_line(1)

    for variant in d["variants"]:
        b.add_line(f"inline { d['fq_name'] }::_ns::{ variant['name'] }::Builder<BufferBackend> _{ variant['snake_name'] }()")
        b.add_line(f"{{")
        b.add_line(f"    return {{ this->__backend, this->__buffer + { d['enum_size'] }, this->__self_offset + { d['enum_size'] } }};")
        b.add_line(f"}}")
        b.skip_line(1)

    b.decrement_indent()
    b.skip_line(1)

    b.add_line(f"public:")
    b.increment_indent()
    b.skip_line(1)

    b.add_line(f"constexpr static uint32_t blitz_size()")
    b.add_line(f"{{")
    b.add_line(f"    return { d['size'] };")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"Builder(BufferBackend& _backend, uint8_t* _buffer, bzb::offset_t _self_offset);")
    b.skip_line(1)

    for variant in d["variants"]:
        b.add_line(f"inline _ns::{ variant['name'] }::Builder<BufferBackend> make_{ variant['name'] }()")
        b.add_line(f"{{")
        b.add_line(f"    this->_tag() = _Tag::{ variant['name'] };")
        b.add_line(f"    return this->_{ variant['snake_name'] }();")
        b.add_line(f"}}")
        b.skip_line(1)

    # Direct assignment
    b.add_line(f"Builder& operator=(raw_variant_t variant)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"blitzbuffers::match(")
    b.increment_indent()

    b.add_line_without_newline(f"variant")

    for variant in d["variants"]:
        b.add_line_unindented(f",")
        b.add_line(f"[this]({ d['fq_name'] }::_ns::{ variant['name'] }::Raw _raw)")
        b.add_line(f"{{")
        b.add_line(f"    this->_tag() = _Tag::{ variant['name'] };")
        b.add_line(f"    this->_{ variant['snake_name'] }() = _raw;")
        b.add_line_without_newline(f"}}")

    b.add_line_unindented(f"")
    b.decrement_indent()
    b.add_line(f");")
    b.skip_line(1)

    b.add_line(f"return *this;")

    b.decrement_indent()
    b.add_line(f"}}")

    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)


#
# Definition
#
def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    for variant in d["variants"]:
        b.add_line(f"// Variant definition { variant['name'] }")
        b.add_line(f"namespace { d['fq_name_def'] }")
        b.add_line(f"{{")
        b.increment_indent()

        b.add_line(f"namespace _ns::{ variant['name'] }")
        b.add_line(f"{{")
        b.increment_indent()

        struct.add_builder_definition(b, variant["type"], ctx, raw_assignments=True)

        b.decrement_indent()
        b.add_line(f"}}")

        struct.add_viewer_definition(b, variant["type"], ctx, viewer_name=variant["name"])

        b.decrement_indent()
        b.add_line(f"}}")
        b.skip_line(1)

    b.add_line(f"// Tagged union definition { d['name'] }")
    b.add_line(f"namespace { d['fq_name_def'] }")
    b.add_line(f"{{")
    b.increment_indent()

    add_viewer_definition(b, d, ctx)
    add_builder_definition(b, d, ctx)

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_viewer_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"inline Viewer::Viewer(const uint8_t* _buffer)")
    b.add_line(f": __buffer(_buffer)")

    b.add_line(f"{{}}")
    b.skip_line(1)

    # Equality operator
    b.add_line(f"inline bool operator==(const Viewer& lhs, const Viewer& rhs)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"const auto lhs_tag = bzb::PrimitiveContainer<_Tag, const uint8_t*>(lhs.__buffer);")
    b.add_line(f"const auto rhs_tag = bzb::PrimitiveContainer<_Tag, const uint8_t*>(rhs.__buffer);")
    b.add_line(f"if (lhs_tag != rhs_tag) {{")
    b.add_line(f"    return false;")
    b.add_line(f"}}")
    b.skip_line(1)

    b.add_line(f"return lhs.as_variant() == rhs.as_variant();")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    # Stream insertion operator
    b.add_line(f"inline std::ostream& operator<<(std::ostream& os, const Viewer& value)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"const auto tag = bzb::PrimitiveContainer<_Tag, const uint8_t*>(value.__buffer);")

    b.add_line(f"switch (tag)")
    b.add_line(f"{{")

    b.add_line(f"case static_cast<_Tag>(0):")
    b.increment_indent()
    b.add_line(f"os << \"{ d['name'] }::_None\";")
    b.add_line(f"break;")
    b.decrement_indent()

    for variant in d["variants"]:
        b.add_line(f"case _Tag::{ variant['name'] }:")
        b.increment_indent()
        b.add_line(f"os << \"{ d['name'] }::{ variant['name'] }(\" << value.{ variant['snake_name'] }() << \")\";")
        b.add_line(f"break;")
        b.decrement_indent()

    b.add_line(f"default:")
    b.increment_indent()
    b.add_line(f"os << \"{ d['name'] }::UnknownTag(\" << static_cast<{ d['enum_underlying_type'] }>(tag.value()) << \")\";")
    b.add_line(f"break;")
    b.decrement_indent()

    b.add_line(f"}}")

    b.add_line(f"return os;")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)


def add_builder_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    b.add_line(f"template <class BufferBackend>")
    b.add_line(f"inline Builder<BufferBackend>::Builder(BufferBackend& _backend, uint8_t* _buffer, bzb::offset_t _self_offset)")
    b.add_line(f": bzb::BufferWriterBase<BufferBackend>(_backend, _buffer, _self_offset)")

    b.add_line(f"{{}}")
    b.skip_line(1)
