import re


PRIMITIVE_TYPES = {
    "bool": "bool",
    "u8": "uint8_t",
    "u16": "uint16_t",
    "u32": "uint32_t",
    "u64": "uint64_t",
    "u128": "uint128_t",
    "i8": "int8_t",
    "i16": "int16_t",
    "i32": "int32_t",
    "i64": "int64_t",
    "i128": "int128_t",
    "f32": "float",
    "f64": "double",
}

ENUM_SIZE_TO_TYPE = {
    1: "uint8_t",
    2: "uint16_t",
    4: "uint32_t",
}


def sanitize_name(name):
    if name[0].isdigit():
        return "_" + name
    return name


# Made from: https://stackoverflow.com/a/1176023/2236416
pattern1 = re.compile("(.)([A-Z][a-z]+)")
pattern2 = re.compile("__([A-Z])")
pattern3 = re.compile("([a-z0-9])([A-Z])")


def to_snake_case(name):
    name = pattern1.sub(r"\1_\2", name)
    name = pattern2.sub(r"_\1", name)
    name = pattern3.sub(r"\1_\2", name)
    return name.lower()
