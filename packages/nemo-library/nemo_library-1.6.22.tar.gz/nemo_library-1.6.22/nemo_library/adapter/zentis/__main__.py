from nemo_library.adapter.zentis.flow import zentis_flow


import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Gedys ETL flow with optional step toggles."
    )

    # Main step toggles
    parser.add_argument(
        "--extract",
        dest="bextract",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run extract step (use --no-extract to skip).",
    )
    parser.add_argument(
        "--transform",
        dest="btransform",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run transform step (use --no-transform to skip).",
    )
    parser.add_argument(
        "--load",
        dest="bload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run load step (use --no-load to skip).",
    )

    # Convenience: run exactly one main step
    parser.add_argument(
        "--only",
        choices=["extract", "transform", "load"],
        help="Run exactly one main step and skip the others.",
    )

    args = parser.parse_args()

    if args.only:
        args.bextract = args.only == "extract"
        args.btransform = args.only == "transform"
        args.bload = args.only == "load"

    zentis_flow(
        bextract=args.bextract,
        btransform=args.btransform,
        bload=args.bload,
    )


if __name__ == "__main__":
    main()
