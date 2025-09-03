from ..output_builder import OutputBuilder
from ..shared import DefinitionContext, Definition


#
# Forward declaration
#
def add_forward_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    if len(ctx["namespace"]) > 0:
        b.add_line(f"namespace { '::'.join(ctx['namespace']) }")
        b.add_line(f"{{")
        b.increment_indent()

    b.add_line(f"enum class { d['name'] } : { d['enum_underlying_type'] };")

    if len(ctx["namespace"]) > 0:
        b.decrement_indent()
        b.add_line(f"}}")


#
# Declaration
#
def add_declaration(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    if len(ctx["namespace"]) > 0:
        b.add_line(f"namespace { '::'.join(ctx['namespace']) }")
        b.add_line(f"{{")
        b.increment_indent()

    b.add_line(f"enum class { d['name'] } : { d['enum_underlying_type'] }")
    b.add_line(f"{{")
    b.increment_indent()
    for idx, variant in enumerate(d["variants"]):
        b.add_line(f"{ variant } = { idx },")
    b.decrement_indent()
    b.add_line(f"}};")
    b.skip_line(1)

    # Stream insertion operator
    b.add_line(f"inline std::ostream& operator<<(std::ostream& os, const { d['name'] }& value)")
    b.add_line(f"{{")
    b.increment_indent()

    b.add_line(f"switch (value)")
    b.add_line(f"{{")
    for idx, variant in enumerate(d["variants"]):
        b.add_line(f"case { d['name'] }::{ variant }:")
        b.increment_indent()
        b.add_line(f'os << "{ variant }";')
        b.add_line(f"break;")
        b.decrement_indent()

    b.add_line(f"default:")
    b.increment_indent()
    b.add_line(f"os << \"Unknown(\" << static_cast<{d['enum_underlying_type']}>(value) << \")\";")
    b.add_line(f"break;")
    b.decrement_indent()

    b.add_line(f"}}")

    b.add_line(f"return os;")

    b.decrement_indent()
    b.add_line(f"}}")
    b.skip_line(1)

    if len(ctx["namespace"]) > 0:
        b.decrement_indent()
        b.add_line(f"}}")


#
# Definition
#
def add_definition(b: OutputBuilder, d: Definition, ctx: DefinitionContext):
    pass
