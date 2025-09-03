from .common import ENUM_SIZE_TO_TYPE, to_snake_case
from ..shared import Definition, DefinitionContext, is_enum, is_tagged_union


def prepare_context(ctx: DefinitionContext):
    for def_name in ctx["def_names"]:
        d = ctx["def_mapping"][def_name]
        update_definition_for_cpp(d, ctx)


def get_fully_qualified_name(definition: Definition, context: DefinitionContext):
    def_name = definition["name"]
    path = definition["path"]
    if len(path) == 0 or is_enum(definition):
        return "::".join([part for part in [*context["namespace"], def_name]])

    prefix_namespace = "::".join(context["namespace"])
    fq_name = prefix_namespace + "::" + ("::".join(path))

    return f"{fq_name}::{def_name}"


# Determine and add names used to refer to the classes of this definition
def add_class_names(definition: Definition, context: DefinitionContext):
    fq_name = get_fully_qualified_name(definition, context)
    definition["fq_name_def"] = fq_name
    definition["fq_name"] = "::" + fq_name


# Update the definition dictionary with information used during C++ generation
def update_definition_for_cpp(definition: Definition, context: DefinitionContext):
    def_name = definition["name"]
    add_class_names(definition, context)

    if is_enum(definition) or is_tagged_union(definition):
        # Add the underlying C++ type for the enum class based on the enum size
        size = definition["enum_size"]
        if size not in ENUM_SIZE_TO_TYPE:
            raise Exception(f"No matching size for '{def_name}': '{size}'")

        definition["enum_underlying_type"] = ENUM_SIZE_TO_TYPE[size]

    if is_tagged_union(definition):
        # Change all variants of a tagged union to be structs
        sub_path = definition["path"][:]
        sub_path.append(def_name)

        for variant in definition["variants"]:
            variant["snake_name"] = to_snake_case(variant["name"])

            if variant["type"] != None and "name" in variant["type"]:
                add_class_names(variant["type"], context)
                update_definition_for_cpp(variant["type"], context)
