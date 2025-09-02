# nemo_library/adapter/gedys/__main__.py
import argparse
from nemo_library.adapter.gedys.flow import gedys_flow


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

    # Transform sub-step toggles
    parser.add_argument(
        "--sentiment",
        dest="tsentiment",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run transform: sentiment analysis (use --no-sentiment to skip).",
    )
    parser.add_argument(
        "--flatten",
        dest="tflatten",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run transform: flattening (use --no-flatten to skip).",
    )
    parser.add_argument(
        "--join",
        dest="tjoin",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run transform: join (use --no-join to skip).",
    )

    # Convenience: run exactly one transform sub-step
    parser.add_argument(
        "--only-transform",
        choices=["sentiment", "flatten", "join"],
        help="Run exactly one transform sub-step and skip the others.",
    )

    # Convenience: run define what to load
    parser.add_argument(
        "--only-load",
        choices=["entities", "joined", "all"],
        default="all",
        help="Run exactly one load step and skip the others.",
    )

    args = parser.parse_args()

    if args.only:
        args.bextract = args.only == "extract"
        args.btransform = args.only == "transform"
        args.bload = args.only == "load"

    if args.only_transform:
        args.tsentiment = args.only_transform == "sentiment"
        args.tflatten = args.only_transform == "flatten"
        args.tjoin = args.only_transform == "join"
        # Ensure transform runs if a sub-step was explicitly chosen
        args.btransform = True
        
    if args.only_load:
        args.lload_entities = args.only_load in ("entities", "all")
        args.lload_joined = args.only_load in ("joined", "all")
        # ensure load runs if a sub-step was explicitly chosen
        args.bload = True

    gedys_flow(
        bextract=args.bextract,
        btransform=args.btransform,
        bload=args.bload,
        tsentiment=args.tsentiment,
        tflatten=args.tflatten,
        tjoin=args.tjoin,
        lload_entities=args.lload_entities,
        lload_joined=args.lload_joined,
    )


if __name__ == "__main__":
    main()
