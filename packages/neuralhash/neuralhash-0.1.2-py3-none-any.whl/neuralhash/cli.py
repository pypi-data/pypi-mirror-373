import argparse
import sys
from neuralhash import get_neuralhash_hex

def main():
    parser = argparse.ArgumentParser(
        prog="neuralhash",
        description="Compute NeuralHash (hex) for one or more images."
    )
    parser.add_argument(
        "images",
        nargs="+",
        help="Path(s) to image files"
    )
    parser.add_argument(
        "--output-only",
        action="store_true",
        help="Print only the hash output(s), without filenames"
    )
    args = parser.parse_args()

    for image_path in args.images:
        try:
            hash_hex = get_neuralhash_hex(image_path)
            if args.output_only:
                print(hash_hex)
            else:
                print(f"{image_path}: {hash_hex}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}", file=sys.stderr)
            sys.exit(1)
