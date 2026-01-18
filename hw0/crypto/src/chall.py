import math
import os
import random
import zipfile
from operator import and_, or_, xor

from Crypto.Util.number import sieve_base

r = random.SystemRandom()

ops = (xor, and_, or_)
primes = [p for p in sieve_base if p.bit_length() == 12]
p_bytes = 2


def encrypt(msg: bytes) -> bytes:
    # One-time pad, but stronger :)
    key = os.urandom(len(msg))
    op = r.choice(ops)
    ct = bytes(map(op, msg, key))
    return ct


def main():
    ps = r.sample(primes, 87)
    N = math.prod(ps)

    with open("flag.txt", "rb") as f:
        flag = f.read().strip()
    x = int.from_bytes(flag)
    assert x < N, "flag too long"
    y = pow(x, 0x101, N)

    with zipfile.ZipFile("output.zip", "w") as zf:
        for i, p in enumerate(ps):
            msg = ((i + 114) * y % p).to_bytes(p_bytes) + os.urandom(r.randrange(5, 14))
            with zf.open(f"{i}.bin", "w") as f:
                for _ in range(p):
                    f.write(encrypt(msg))


if __name__ == "__main__":
    main()
