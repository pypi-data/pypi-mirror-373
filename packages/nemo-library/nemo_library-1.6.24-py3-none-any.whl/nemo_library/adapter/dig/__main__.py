import argparse

from nemo_library.adapter.dig.generate_templates import generate_templates
from nemo_library.adapter.dig.flow import dig_flow

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the DIG ETL flow with optional switches"
    )

    # Main step toggles
    parser.add_argument(
        "--generate_templates", dest="bgenerate_templates", action=argparse.BooleanOptionalAction, default=False,
        help="Run generate_templates step"
    )

    args = parser.parse_args()
    if args.bgenerate_templates:
        generate_templates()
    else:
        dig_flow()

if __name__ == "__main__":
    main()
