import argparse
import os

from blitzbuffers.arg_util import OptionalSecondArgAction, OptionalSecondArgFormatter
from blitzbuffers.printer import printer
from blitzbuffers.parsing import parse_blitzbuffers
from blitzbuffers.languages import LANG_KEYS, LANG_CONFIG

parser = argparse.ArgumentParser(
    prog="blitzbuffers",
    description="Generates code that implements blitzbuffers based on a given schema",
    formatter_class=OptionalSecondArgFormatter,
)

parser.add_argument("schema", help="Path to your blitzbuffers schema file")

parser.add_argument(
    "-l",
    "--lang",
    type=str,
    nargs="+",
    metavar="LANG",
    action=OptionalSecondArgAction,
    optsecond="OUTPUT_PATH",
    help="The language and optionally output path used for code generation. Can be specified multiple times.",
)

parser.add_argument(
    "-p",
    "--print",
    type=str,
    nargs=2,
    metavar=("DEF_NAME", "BIN_PATH"),
    help="Print the layout of the given binary data file.",
)


def run_generate(args):
    with open(args.schema, "r", encoding="utf8") as file:
        input_schema = file.read()

    ctx = parse_blitzbuffers(input_schema)

    for lang in args.lang:
        if not lang[0] in LANG_KEYS:
            print(f"Unknown language specifier: '{lang[0]}'.")
            continue

        lang_kind = LANG_KEYS[lang[0]]
        lang_config = LANG_CONFIG[lang_kind]

        if len(lang) > 1:
            output_path = lang[1]
        else:
            output_path = os.path.splitext(args.schema)[0] + lang_config["extension"]

        with open(output_path, "w+", encoding="utf8", newline="\n") as file:
            lang_config["gen_function"](file, ctx)


def run_print(args):
    with open(args.schema, "r", encoding="utf8") as file:
        input_schema = file.read()

    ctx = parse_blitzbuffers(input_schema)

    with open(args.print[1], "rb") as file:
        printer.print_layout(file.read(), args.print[0], ctx)


def run(args):
    if args.lang is not None:
        run_generate(args)
        return

    if args.print is not None:
        run_print(args)
        return

    print("Missing action argument.")


if __name__ == "__main__":
    run(parser.parse_args())
