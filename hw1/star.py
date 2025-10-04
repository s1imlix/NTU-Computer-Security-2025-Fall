#!/usr/bin/env python3
from pwn import *
import subprocess 
import os 
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("--delete", action="store_true", help="Delete the temporary file")
args = parser.parse_args()

# Executes cleanly
valid = [0, 1, 96]

# Implemented, but crashed with "index out of bounds"
maybe_valid = list(range(16, 21)) + list(range(32, 36)) + list(range(48, 51)) + list(range(64, 70))

with open('payload', 'wb') as f:
    f.write(b"STARP")

    # function
    f.write(p32(1))
    f.write(p32(0))

    # storage
    f.write(p32(0))

    # program
    program = b""
    program += p8(0x01)
    program += p8(0x00)
    f.write(p32(len(program)))
    f.write(program)
    f.flush()
    

    result = subprocess.run(["./starvm", f.name], capture_output=True)
    print(f"output:\n{result.stderr.decode()}")

    if args.delete:
        os.remove(f.name)
    else:
        print(f"Temporary file kept at: {f.name}")
