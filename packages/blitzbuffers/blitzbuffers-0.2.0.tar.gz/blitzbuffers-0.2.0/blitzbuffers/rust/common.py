PRIMITIVE_TYPES = {
    "bool": "bool",
    "u8": "u8",
    "u16": "u16",
    "u32": "u32",
    "u64": "u64",
    "u128": "u128",
    "i8": "i8",
    "i16": "i16",
    "i32": "i32",
    "i64": "i64",
    "i128": "i128",
    "f32": "f32",
    "f64": "f64",
}

RESERVED_NAMES = set(["type"])


def sanitize_name(name):
    if name[0].isdigit() or name in RESERVED_NAMES:
        return "_" + name

    return name


def get_fq_name_from_type(type, ctx):
    if type[0].isupper():
        return ctx["def_mapping"][type]["fq_name"]

    return type
