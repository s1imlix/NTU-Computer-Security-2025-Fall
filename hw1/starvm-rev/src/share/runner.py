#!/usr/bin/env python3
from tempfile import NamedTemporaryFile
from subprocess import Popen, TimeoutExpired, STDOUT
import sys
import os

size = int(input("size > "))
with NamedTemporaryFile(delete=False) as f:
    buffer = b""
    while len(buffer) < size:
        buffer += sys.stdin.buffer.read(size - len(buffer))
    f.write(buffer)
    fn = f.name
try:
    p = Popen(["./starvm", fn], stderr=STDOUT)
    p.wait(60)
except TimeoutExpired:
    print("timeout")
    p.kill()
finally:
    os.remove(fn)
