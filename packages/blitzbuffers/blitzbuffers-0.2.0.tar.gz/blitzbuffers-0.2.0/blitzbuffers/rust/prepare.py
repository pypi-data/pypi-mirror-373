from ..shared import DefinitionContext, StructDefinition, is_tagged_union


def prepare_context(ctx: DefinitionContext):
    for d in ctx["def_mapping"].values():
        prepare_struct(d, ctx)


def prepare_struct(d: StructDefinition, ctx: DefinitionContext):
    d["fq_name"] = "_".join([*d["path"], d["name"]])
    if is_tagged_union(d):
        for variant in d["variants"]:
            variant["fq_name"] = "_".join([*d["path"], d["name"], variant["name"]])
            prepare_struct(variant["type"], ctx)
