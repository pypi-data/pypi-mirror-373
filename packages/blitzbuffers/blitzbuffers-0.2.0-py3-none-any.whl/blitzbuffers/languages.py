from enum import Enum
from io import TextIOWrapper
from typing import Callable, TypedDict

from .shared import DefinitionContext

from .cpp import generate as cpp_generate
from .rust import generate as rust_generate


class OutputKind(Enum):
    CPP = 0
    RUST = 1


class LangConfig(TypedDict):
    extension: str
    gen_function: Callable[[TextIOWrapper, DefinitionContext], None]


LANG_CONFIG: dict[OutputKind, LangConfig] = {
    OutputKind.CPP: LangConfig(extension=".h", gen_function=cpp_generate.write_to_file_cpp),
    OutputKind.RUST: LangConfig(extension=".rs", gen_function=rust_generate.write_to_file_rust),
}

LANG_KEYS = {
    "cpp": OutputKind.CPP,
    "c++": OutputKind.CPP,
    "rust": OutputKind.RUST,
    "rs": OutputKind.RUST,
}
