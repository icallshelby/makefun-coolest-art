#!/usr/bin/env python3
import os
import shutil
import hashlib
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, 'art.jpg')
    
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    
    dest_path = os.path.join(output_dir, 'entry.png')
    
    shutil.copyfile(src_path, dest_path)
    
    src_size = os.path.getsize(src_path)
    dest_size = os.path.getsize(dest_path)
    
    if src_size != dest_size:
        print(f"Error: Size mismatch! Source size ({src_size}) != Destination size ({dest_size})", file=sys.stderr)
        sys.exit(1)
        
    print(f"Output verified to match source, byte count: {dest_size}")
    
    sha256 = hashlib.sha256()
    with open(dest_path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    file_hash = sha256.hexdigest()
    
    print(f"Output path: {dest_path}")
    print(f"SHA256: {file_hash}")

if __name__ == '__main__':
    main()
