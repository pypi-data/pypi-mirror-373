import os
import shutil
import argparse
from datetime import datetime
from typing import Any
from . import compare_files, __version__

def format_val(val: Any) -> str:
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return str(val)

def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"deltadir {__version__} — compare directories. "
                    "Source (src) is never modified. Destination (dst) can be updated with -s/--sync."
    )
    parser.add_argument("src", help="Source directory (never modified)")
    parser.add_argument("dst", help="Destination directory (can be modified with -s/--sync)")
    parser.add_argument("-m", "--method", choices=["exists", "mtime", "size", "hash"], default="exists",
                        help="Comparison method (default: exists)")
    parser.add_argument("-s", "--sync", action="store_true",
                        help="Copy differences from src to dst")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite files in dst when syncing")
    parser.add_argument("-t", "--table", action="store_true",
                        help="Print full table (default: brief mode)")

    args = parser.parse_args()

    rows = []

    for root, _, files in os.walk(args.src):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, args.src)
            dst_file = os.path.join(args.dst, rel_path)

            is_diff, reason, src_val, dst_val = compare_files(src_file, dst_file, args.method)
            action_taken = "nothing(reported)"

            if is_diff:
                if args.sync:
                    if not os.path.exists(dst_file):
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                        action_taken = "created"
                    elif args.overwrite:
                        shutil.copy2(src_file, dst_file)
                        action_taken = "overwritten"
                    else:
                        action_taken = "skipped(no overwrite)"
                        print(f"SKIP: {rel_path} (overwrite not set)")
                rows.append((rel_path, reason, src_val, dst_val, action_taken))

    if not args.table:
        # Brief mode: only file names
        for r in rows:
            print(r[0])
    else:
        # Full table mode
        print(f"{'File':40} | {'Reason':15} | {'Src':20} | {'Dst':20} | {'Action':20}")
        print("-"*125)
        for r in rows:
            print(f"{r[0]:40} | {r[1]:15} | {format_val(r[2]):20} | {format_val(r[3]):20} | {r[4]:20}")
