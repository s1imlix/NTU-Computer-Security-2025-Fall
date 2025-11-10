import secrets
from typing import Callable

poly1 = [0, 2, 11, 21, 23]
poly2 = [0, 1, 61, 114, 519]
poly3 = [0, 13, 37, 68, 87]

BitRNG = Callable[[], int]


class LFSR:
    def __init__(self, poly: list[int], state: int):
        # the characteristic polynomial is exactly sum(x**e for e in poly)
        self._tap = poly[:-1]
        self._state = state
        self._shift = poly[-1] - 1
        self._mask = sum([1 << i for i in self._tap])

    def __call__(self):
        f = 0
        for i in self._tap:
            f ^= (self._state >> i) & 1
        x = self._state & 1
        self._state = (self._state >> 1) | (f << self._shift)
        return x

    @staticmethod
    def random_with_poly(poly: list[int]):
        return LFSR(poly, secrets.randbits(poly[-1]))


class CombinedBitRNG:
    def __init__(self, rng1: BitRNG, rng2: BitRNG, rng3: BitRNG):
        self.rng1 = rng1
        self.rng2 = rng2
        self.rng3 = rng3

    def __call__(self):
        return (3 * self.rng1() + 5 * self.rng2() + 7 * self.rng3()) % 11 % 2


def randbyte(rng):
    b = 0
    for i in range(8):
        b = (b << 1) | rng()
    return b


def randbytes(rng, n):
    return bytes(randbyte(rng) for _ in range(n))


def main():
    lfsr1 = LFSR.random_with_poly(poly1)
    lfsr2 = LFSR.random_with_poly(poly2)
    lfsr3 = LFSR.random_with_poly(poly3)
    rng = CombinedBitRNG(lfsr1, lfsr2, lfsr3)

    with open("flag.txt", "rb") as f:
        flag = f.read().strip()

    out = bytes(x ^ y for x, y in zip(randbytes(rng, len(flag)), flag))
    out += randbytes(rng, 512)
    print(out.hex())


if __name__ == "__main__":
    main()
