#!/usr/bin/env python3
import os
import shutil
import hashlib
import sys

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, 'art.jpg')
    
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    dst_path = os.path.join(output_dir, 'entry.png')
    
    if not os.path.exists(src_path):
        print(f"Error: Source file {src_path} not found.", file=sys.stderr)
        sys.exit(1)
        
    shutil.copyfile(src_path, dst_path)
    
    src_size = os.path.getsize(src_path)
    dst_size = os.path.getsize(dst_path)
    
    if src_size != dst_size:
        print(f"Error: Size mismatch! Source size ({src_size}) != Output size ({dst_size})", file=sys.stderr)
        sys.exit(1)
        
    src_hash = compute_sha256(src_path)
    dst_hash = compute_sha256(dst_path)
    
    if src_hash != dst_hash:
        print(f"Error: SHA-256 mismatch! Source hash ({src_hash}) != Output hash ({dst_hash})", file=sys.stderr)
        sys.exit(1)
        
    print(f"Verification passed: output verified to match source (size + sha256).")
    print(f"Output path: {dst_path}")
    print(f"Byte size: {dst_size}")
    print(f"SHA256: {dst_hash}")

if __name__ == '__main__':
    main()
