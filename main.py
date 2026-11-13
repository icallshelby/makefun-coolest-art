#!/usr/bin/env python3
import os
import shutil
import sys

def main():
    # Determine directory of this script so art.jpg is always loaded relative to main.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, "art.jpg")

    # Output directory from MAKEFUN_OUTPUT_DIR or default to /output
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    dest_path = os.path.join(out_dir, "entry.png")

    # Byte-for-byte copy
    shutil.copyfile(src_path, dest_path)

    # Post-copy verification: compare output file size with source file size
    src_size = os.path.getsize(src_path)
    dest_size = os.path.getsize(dest_path)

    if src_size != dest_size:
        print(f"Error: Output file size ({dest_size}) does not match source file size ({src_size})", file=sys.stderr)
        sys.exit(1)

    print(f"Output was verified to match the source; byte count: {dest_size}")

if __name__ == "__main__":
    main()
