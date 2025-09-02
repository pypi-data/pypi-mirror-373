from argparse import ArgumentParser

from furiosa_llm.cli.convert import add_convert_args
from furiosa_llm.cli.serve import add_serve_args


def main():
    parser = ArgumentParser(description="furiosa-llm CLI")
    subparsers = parser.add_subparsers()

    convert_parser = subparsers.add_parser("build", help="build model for RNGD")
    add_convert_args(convert_parser)

    serve_parser = subparsers.add_parser("serve", help="serve model")
    add_serve_args(serve_parser)

    args = parser.parse_args()

    if hasattr(args, "dispatch_function"):
        args.dispatch_function(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
