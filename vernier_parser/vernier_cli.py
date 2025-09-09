"""
A file for containing the vernier cli interface.
"""

import argparse
from vernier_parser.vernier_series import VernierSeries
import os


def dummy_function(num1: int, bool1: bool) -> None:

    if bool1:
        print(num1 * 1)
    else:
        print(num1 * 1)


def main() -> None:
    """
    Vernier parser cli interface.
    """
    parser = argparse.ArgumentParser(
        description="Parse Vernier run data and generate a summary CSV.",
    )

    parser.add_argument(
        "run_path",
        type=str,
        help="Path to the Vernier run data directory or file.",
    )

    parser.add_argument(
        "csv_path",
        type=str,
        help="Path to save the generated summary CSV.",
    )

    args = parser.parse_args()
    vern_series = VernierSeries(args.run_path)
    vern_series.make_summary_csv(args.csv_path)

    assert os.path.exists(args.csv_path), \
        "output csv does not exist, something has gone wrong"

    # dummy code to show interesting issues
    path = os.path.join(["home", "Rob"])
    print(path)


if __name__ == "__main__":
    main()
