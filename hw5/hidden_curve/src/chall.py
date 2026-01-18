from hashlib import sha256

from Crypto.Cipher import AES
from fastecdsa.curve import Curve
from fastecdsa.ecdsa import sign, verify
from fastecdsa.keys import gen_keypair
from fastecdsa.point import Point
from secret import a, b, flag, gx, gy, n, p

MyCurve = Curve("custom", p, a, b, n, gx, gy)


def encrypt(key: bytes, msg: bytes) -> bytes:
    cipher = AES.new(sha256(key).digest(), AES.MODE_CTR)
    return cipher.nonce + cipher.encrypt(msg)


def point_to_bytes(P: Point) -> bytes:
    return P.x.to_bytes(64, "big") + P.y.to_bytes(64, "big")


def elgamal(pk: Point, m: bytes):
    tsk, tpk = gen_keypair(MyCurve)
    S = tsk * pk
    ct = encrypt(point_to_bytes(S), m)
    return point_to_bytes(tpk) + ct


def main():
    sk, pk = gen_keypair(MyCurve)
    enc = elgamal(pk, flag)
    sig = sign(enc, sk, MyCurve)
    assert verify(sig, enc, pk, MyCurve)

    G = point_to_bytes(MyCurve.G)
    Y = point_to_bytes(pk)
    print(f"{p = }")
    print(f"{G = }")
    print(f"{Y = }")
    print(f"{enc = }")
    print(f"{sig = }")


if __name__ == "__main__":
    main()
