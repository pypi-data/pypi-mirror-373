import argparse
from pathlib import Path
from typing import Any

from .figure import Fig, FigError


def cmd_build(args: argparse.Namespace) -> int:
    fig = Fig(args.json_file)
    fig.fig_dir = args.outdir
    fig.pdf_filename = args.output
    fig.verbose = args.verbose
    try:
        fig.create_pdf()
    except FigError as e:
        print(f"[ERROR] {e}")
        return 2
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        Fig(args.json_file)  # load + validate
    except FigError as e:
        print(f"[ERROR] {e}")
        return 2
    print("OK")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    try:
        f = Fig(args.json_file)
    except FigError as e:
        print(f"[ERROR] {e}")
        return 2
    for k, v in f.list.items():
        t = v.get("type")
        print(f"{k}\t{t}")
    return 0


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="paperfig", description="Build figures from JSON spec")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build and concatenate figures")
    p_build.add_argument("json_file", type=Path, help="Path to JSON spec")
    p_build.add_argument("-o", "--output", default="figures.pdf", help="Output PDF filename")
    p_build.add_argument("-d", "--outdir", default="fig", help="Output directory")
    p_build.add_argument("-v", "--verbose", type=int, default=1, help="Verbosity (0/1/2)")
    p_build.set_defaults(func=cmd_build)

    p_val = sub.add_parser("validate", help="Validate JSON spec only")
    p_val.add_argument("json_file", type=Path, help="Path to JSON spec")
    p_val.set_defaults(func=cmd_validate)

    p_list = sub.add_parser("list", help="List figures in JSON spec")
    p_list.add_argument("json_file", type=Path, help="Path to JSON spec")
    p_list.set_defaults(func=cmd_list)

    args = p.parse_args(argv)
    raise SystemExit(args.func(args))
