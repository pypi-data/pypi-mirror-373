import os
import sys
import argparse
from contextlib import closing
from functools import partial

from . import __version__, Result, learn, utils, enable_debug


def run(args: argparse.Namespace):
    input_dir = args.input_dir
    with closing(args.live_vars):
        live_vars = utils.get_live_vars(args.live_vars)
    vals_raw_neg = utils.get_valuations(os.path.join(args.input_dir, "neg"))
    vals_raw_pos = utils.get_valuations(os.path.join(args.input_dir, "pos"))
    vals_neg, vals_pos = utils.parse_valuation(vals_raw_neg, vals_raw_pos)
    result = learn(live_vars, vals_neg, vals_pos, args.pac_delta)

    output = args.output
    int_vars = sum(v.var_type == utils.VarType.INT for v in live_vars.values())
    output.write(f"[metadata] [live-variables] [total {len(live_vars)}] [int {int_vars}]\n")
    output.write("[metadata] [hypothesis-space]"
        f" [original {result.size_orig}] [final {result.size_final}]\n")
    output.write("[metadata] [valuation]"
        f" [neg {result.samples_neg}] [pos {result.samples_pos}]"
        f" [uniq {result.samples_neg + result.samples_pos}]"
        f" [init-neg {len(vals_neg)}] [init-pos {len(vals_pos)}]"
        f" [non-uniq {len(vals_neg) + len(vals_pos)}]\n")
    output.write(f"[metadata] [pac] [delta {args.pac_delta}]"
        f" [eps {result.pac_epsilon}]\n")
    output.write(f"[metadata] [pac-no-uniq] [delta {args.pac_delta}]"
        f" [eps {result.pac_epsilon_no_uniq}]\n")
    output.write("[final] --------------\n")
    result.inv_mgr.dump(output, args.output_smt)


def run_uni(args: argparse.Namespace):
    with closing(args.live_vars):
        live_vars = utils.get_live_vars(args.live_vars)
    if args.lv_file is not None:
        with closing(args.lv_file):
            used_lvs = utils.get_lv_file(args.lv_file)
        live_vars = {k: v for k, v in live_vars.items() if v.name in used_lvs}
    vals_raw_neg = utils.get_valuations(os.path.join(args.input_dir, "neg"))
    vals_raw_pos = utils.get_valuations(os.path.join(args.input_dir, "pos"))
    vals_neg, vals_pos = utils.parse_valuations_uni([],
        vals_raw_neg + vals_raw_pos)
    result = learn(live_vars, vals_neg, vals_pos, args.pac_delta)

    output = args.output
    int_vars = sum(v.var_type == utils.VarType.INT for v in live_vars.values())
    output.write(f"[metadata] [live-variables] [total {len(live_vars)}] [int {int_vars}]\n")
    output.write("[metadata] [hypothesis-space]"
        f" [original {result.size_orig}] [final {result.size_final}]\n")
    output.write("[metadata] [valuation]"
        f" [neg {result.samples_neg}] [pos {result.samples_pos}]"
        f" [uniq {result.samples_neg + result.samples_pos}]"
        f" [init-neg {len(vals_neg)}] [init-pos {len(vals_pos)}]"
        f" [non-uniq {len(vals_neg) + len(vals_pos)}]\n")
    output.write(f"[metadata] [pac] [delta {args.pac_delta}]"
        f" [eps {result.pac_epsilon}]\n")
    output.write(f"[metadata] [pac-no-uniq] [delta {args.pac_delta}]"
        f" [eps {result.pac_epsilon_no_uniq}]\n")
    output.write("[final] --------------\n")
    result.inv_mgr.dump(output, None)


def directory(path: str, read: bool) -> str:
    if not os.path.isdir(path):
        if read:
            raise argparse.ArgumentTypeError(f"{path} is not a directory")
        try:
            os.mkdir(path)
        except Exception as e:
            raise argparse.ArgumentTypeError(f"mkdir: {e}")
    return path


def main():
    arg_parser = argparse.ArgumentParser(prog="pacfix")
    arg_parser.add_argument("-v", "--version", action="version",
                            version=f"%(prog)s {__version__}")
    arg_subparsers = arg_parser.add_subparsers(dest="mode", required=True)
    arg_parser_base = argparse.ArgumentParser(add_help=False)
    arg_parser_base.add_argument("-i", "--input-dir", metavar="DIR",
        help="Input directory",
        type=partial(directory, read=True), required=True)
    arg_parser_base.add_argument("-l", "--live-vars", metavar="FILE",
        help="Live variables", type=argparse.FileType("r"), required=True)
    arg_parser_base.add_argument("-D", "--pac-delta", metavar="NUMBER",
        help="delta value for pac learning", type=float, default=0.01)
    arg_parser_base.add_argument("-o", "--output", metavar="FILE",
        help="Output file", type=argparse.FileType("w"), default=sys.stdout)
    arg_parser_base.add_argument("-d", "--debug", action="store_true",
                                 help="Enable debug log")
    arg_parser_run = arg_subparsers.add_parser("run",
        parents=[arg_parser_base])
    arg_parser_run.add_argument("-s", "--output-smt", metavar="DIR",
        help="Output directory for smt files",
        type=partial(directory, read=False))
    arg_parser_uni = arg_subparsers.add_parser("uni",
        parents=[arg_parser_base])
    arg_parser_uni.add_argument("-f", "--lv-file", metavar="FILE",
        help="Live variables file those are actually used",
        type=argparse.FileType("r"))
    args = arg_parser.parse_args()
    if args.debug:
        enable_debug()
    if args.mode == "run":
        with closing(args.output):
            run(args)
    elif args.mode == "uni":
        with closing(args.output):
            run_uni(args)


if __name__ == "__main__":
    main()
