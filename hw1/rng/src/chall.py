import secrets
import random
from typing import Callable


RNG = Callable[[], int]


class RNGType1:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __call__(self):
        self.a <<= 1
        self.a |= (self.a & self.b).bit_count() & 1
        return self.a

    @staticmethod
    def random(n):
        a = secrets.randbits(n)
        b = secrets.randbits(n)
        return RNGType1(a, b)


class RNGType2:
    def __init__(self, rand: random.Random):
        self.rand = rand

    def __call__(self):
        return self.rand.getrandbits(1)


class CombinedRNG:
    def __init__(self, rngs: list[RNG]):
        self.rngs = rngs

    def __call__(self):
        return sum(rng() for rng in self.rngs) & 1


def randbyte(rng):
    b = 0
    for i in range(8):
        b = (b << 1) | rng()
    return b


def randbytes(rng, n):
    return bytes(randbyte(rng) for _ in range(n))


def main():
    rng1 = CombinedRNG([RNGType1.random(n) for n in range(48, 763, 35)])
    rng2 = RNGType2(random.Random())
    rng = CombinedRNG([rng1, rng2])
    with open("flag.txt", "rb") as f:
        flag = f.read().strip()

    out = b""
    out += randbytes(rng1, 4096)
    out += randbytes(rng2, 4096)
    out += bytes(x ^ y for x, y in zip(randbytes(rng, len(flag)), flag))
    print(out.hex())


if __name__ == "__main__":
    main()
