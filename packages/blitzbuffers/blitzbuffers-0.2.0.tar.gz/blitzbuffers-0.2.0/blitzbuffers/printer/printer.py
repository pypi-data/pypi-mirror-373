from heapq import heappop, heappush
from pprint import pprint
import struct

from ..shared import OFFSET_BYTE_SIZE, PRIMITIVE_BYTE_SIZES, DefKind, DefinitionContext, Definition

ENUM_SIZE_TO_TYPE = {
    1: "u8",
    2: "u16",
    4: "u32",
}


class ChunkManager:
    def __init__(self, data: bytearray):
        self.data = data
        self.next_chunks = []
        self.chunks = []

    def claim_chunk(self, start: int, length: int, content):
        self.chunks.append(
            {
                "_data": self.data[start : start + length],
                "_offset": start,
                "_length": length,
                "content": content,
            }
        )

    def add_next(self, kind: str, offset: int):
        heappush(self.next_chunks, (offset, kind))

    def pop_next(self):
        return heappop(self.next_chunks)

    def finish(self):
        parsed_chunks = self.chunks
        sorted(parsed_chunks, key=lambda e: e["_offset"])
        self.chunks = []

        current_offset = 0
        for idx, chunk in enumerate(parsed_chunks):
            diff = chunk["_offset"] - current_offset
            if diff > 0:
                # Unclaimed chunk
                self.chunks.append(
                    {
                        {
                            "_data": self.data[current_offset : current_offset + diff],
                            "_offset": current_offset,
                            "_length": diff,
                            "content": "## UNCLAIMED ##",
                        }
                    }
                )
            elif diff < 0:
                raise Exception(f"Overlapping chunks:\n\n{parsed_chunks[idx-1]}\n\n{chunk}")

            self.chunks.append(chunk)
            current_offset += chunk["_length"]

        return self.chunks


def print_layout(data: bytearray, def_name: str, ctx: DefinitionContext):
    if def_name not in ctx["def_mapping"]:
        raise Exception(f"Definition '{def_name}' not found in context.")

    cm = ChunkManager(data)
    cm.add_next(def_name, 0)
    pprint(parse_chunks(cm, ctx))


def parse_chunks(cm: ChunkManager, ctx: DefinitionContext):
    while len(cm.next_chunks) > 0:
        (offset, kind) = cm.pop_next()

        if isinstance(kind, str):
            if kind == "string":
                parse_string_chunk(offset, cm)
            else:
                if kind not in ctx["def_mapping"]:
                    raise Exception(f"Definition '{kind}' not found in context.")
                d = ctx["def_mapping"][kind]
                parse_def_chunk(d, offset, cm, ctx)
        else:
            if "inner" in kind:
                parse_vector_chunk(offset, kind["inner"], cm, ctx)

    return cm.finish()


def parse_string(offset: int, cm: ChunkManager):
    length = 0
    while cm.data[offset + length] != 0:
        length += 1

    return cm.data[offset : offset + length].decode("utf-8")


def parse_string_chunk(offset: int, cm: ChunkManager):
    string = parse_string(offset, cm)

    cm.claim_chunk(
        offset,
        len(string) + 1,
        {
            "kind": "string",
            "value": string,
        },
    )


def parse_vector_chunk(vec_offset: int, inner_type, cm: ChunkManager, ctx: DefinitionContext):
    length = struct.unpack("<I", cm.data[vec_offset : vec_offset + OFFSET_BYTE_SIZE])[0]
    entry_size = get_size_of_type(inner_type, ctx)
    byte_length = OFFSET_BYTE_SIZE + entry_size * length

    values = []

    handler_fn = None
    if isinstance(inner_type, str):
        if inner_type in PRIMITIVE_BYTE_SIZES:

            def parse_primitive_entry(idx: int, entry_offset: int, cm: ChunkManager):
                buffer = cm.data[entry_offset : entry_offset + PRIMITIVE_BYTE_SIZES[inner_type]]
                value = parse_primitive(inner_type, buffer, ctx)
                values.append(
                    {
                        "_buffer": buffer,
                        "_idx": idx,
                        "value": value,
                    }
                )

            handler_fn = parse_primitive_entry

        elif inner_type == "string":

            def parse_string_entry(idx: int, entry_offset: int, cm: ChunkManager):
                buffer = cm.data[entry_offset : entry_offset + OFFSET_BYTE_SIZE]
                offset = struct.unpack("<I", buffer)[0]
                if offset > 0:
                    offset += entry_offset
                    cm.add_next(inner_type, offset)

                    values.append(
                        {
                            "_buffer": buffer,
                            "_idx": idx,
                            "offset": offset,
                        }
                    )
                else:
                    values.append(
                        {
                            "_buffer": buffer,
                            "_idx": idx,
                            "offset": None,
                        }
                    )

            handler_fn = parse_string_entry
        else:
            if inner_type not in ctx["def_mapping"]:
                raise Exception(f"Definition '{inner_type}' not found in context.")
            d = ctx["def_mapping"][inner_type]

            def parse_def_entry(idx: int, entry_offset: int, cm: ChunkManager):
                parsed_def = parse_def(d, entry_offset, cm, ctx)
                parsed_def["_idx"] = idx
                values.append(parsed_def)

            handler_fn = parse_def_entry
    else:
        if "inner" in inner_type:

            def parse_vector_entry(idx, entry_offset, cm):
                buffer = cm.data[entry_offset : entry_offset + OFFSET_BYTE_SIZE]
                offset = struct.unpack("<I", buffer)[0]
                if offset > 0:
                    offset += entry_offset
                    cm.add_next(inner_type, offset)
                    values.append(
                        {
                            "_buffer": buffer,
                            "_idx": idx,
                            "offset": offset,
                        }
                    )
                else:
                    values.append(
                        {
                            "_buffer": buffer,
                            "_idx": idx,
                            "offset": None,
                        }
                    )

            handler_fn = parse_vector_entry

    if handler_fn is None:
        raise Exception(f"Could not handle vector entry type: {inner_type}")

    offset = vec_offset + OFFSET_BYTE_SIZE
    for idx in range(0, length):
        handler_fn(idx, offset, cm)
        offset += entry_size

    cm.claim_chunk(
        vec_offset,
        byte_length,
        {
            "_kind": "vector",
            "_inner": inner_type,
            "_vec_length": length,
            "values": values,
        },
    )


def parse_def_chunk(d: Definition, offset: int, cm: ChunkManager, ctx: DefinitionContext):
    output = parse_struct(d, offset, cm, ctx)

    cm.claim_chunk(
        offset,
        d["size"],
        {
            "kind": d["name"],
            "value": output,
        },
    )


def parse_def(d: Definition, offset: int, cm: ChunkManager, ctx: DefinitionContext):
    match d["kind"]:
        case DefKind.STRUCT:
            return parse_struct(d, offset, cm, ctx)
        case _:
            print(f"Unhandled kind for '{ d['name'] }': { d['kind'] }")


def parse_struct(d: Definition, def_offset: int, cm: ChunkManager, ctx: DefinitionContext):
    def_buffer = cm.data[def_offset : def_offset + d["size"]]

    output = {}
    output["_def"] = d["name"]
    out_fields = output["fields"] = []

    for field in d["fields"]:
        field_data = {
            "_buffer": def_buffer[field["offset"] : field["offset"] + field["size"]],
            "name": field["name"],
            "type": field["type"],
        }
        out_fields.append(field_data)
        match field["kind"]:
            case "primitive":
                field_data["value"] = parse_primitive(field["type"], field_data["_buffer"], ctx)
            case "string" | "vector":
                offset = struct.unpack("<I", field_data["_buffer"])[0]
                if offset > 0:
                    offset += def_offset + field["offset"]
                    field_data["offset"] = offset
                    cm.add_next(field["type"], offset)
                else:
                    field_data["offset"] = None

    return output


def parse_primitive(type: str, data: bytearray, ctx: DefinitionContext):
    match type:
        case "bool":
            return struct.unpack("?", data)[0]
        case "u8":
            return struct.unpack("B", data)[0]
        case "u16":
            return struct.unpack("<H", data)[0]
        case "u32":
            return struct.unpack("<I", data)[0]
        case "u64":
            return struct.unpack("<L", data)[0]
        case "u128":
            return struct.unpack("<Q", data)[0]
        case "i8":
            return struct.unpack("b", data)[0]
        case "i16":
            return struct.unpack("<h", data)[0]
        case "i32":
            return struct.unpack("<i", data)[0]
        case "i64":
            return struct.unpack("<l", data)[0]
        case "i128":
            return struct.unpack("<q", data)[0]
        case "f32":
            return struct.unpack("<f", data)[0]
        case "f64":
            return struct.unpack("<d", data)[0]

        case other:
            if other[0].isupper():
                if not other in ctx["def_mapping"]:
                    raise Exception(f"Could not find primitive '{other}'")

                d = ctx["def_mapping"][other]
                val = parse_primitive(ENUM_SIZE_TO_TYPE[d["size"]], data, ctx)
                if val < len(d["variants"]):
                    return d["variants"][val]
                else:
                    return f"_Unknown({val})"


def get_size_of_type(type: str, ctx: DefinitionContext):
    if isinstance(type, str):
        if type in PRIMITIVE_BYTE_SIZES:
            return PRIMITIVE_BYTE_SIZES[type]

        if type == "string":
            return OFFSET_BYTE_SIZE

        if type[0].isupper():
            if not type in ctx["def_mapping"]:
                raise Exception(f"Unknown definition {type}")

            return ctx["def_mapping"][type]["size"]

    if isinstance(type, dict) and "inner" in type:
        return OFFSET_BYTE_SIZE

    raise Exception("Unknown size")
