import argparse
from pathlib import Path


def _csv_to_list(value):
    return value.split(",")


def get_args():
    parser = argparse.ArgumentParser(description="Python Code Splitter")
    parser.add_argument("file_path", type=Path, help="Path to the Python file to split")
    parser.add_argument("--git", action="store_true", help="Enable git commit")
    parser.add_argument(
        "--targets",
        type=_csv_to_list,
        default=["class", "function"],
        help="Target block types to split (comma-separated values)",
    )
    args = parser.parse_args()
    return args
