import hmac
from hashlib import sha256

from fastecdsa.curve import P384
from fastecdsa.keys import gen_keypair
from Crypto.Cipher import AES
from fastecdsa.ecdsa import sign


def sign(sk: int, msg: bytes, *, curve=P384, hashfunc=sha256) -> tuple[int, int]:
    key = hashfunc(str(sk).encode()).digest()
    k = (
        int.from_bytes(hmac.new(key, msg, hashfunc).digest()) % curve.q
    )  # I don't trust randomness
    z = int.from_bytes(hashfunc(msg).digest()) % curve.q
    r = (k * curve.G).x % curve.q
    s = pow(k, -1, curve.q) * (z + r * sk) % curve.q
    return r, s


msgs = [
    b"https://www.youtube.com/watch?v=3RuCaE5ciNU",
    b"https://www.youtube.com/watch?v=t0xj5ZxWU3c",
    b"https://www.youtube.com/watch?v=lpPih3tTuM0",
    b"https://www.youtube.com/watch?v=RR0gRA0vhrI",
]


def main():
    with open("flag.txt", "rb") as f:
        flag = f.read().strip()

    sk, pk = gen_keypair(P384)
    sigs = [sign(sk, msg) for msg in msgs]

    key = (sk & ((1 << 128) - 1)).to_bytes(16)
    cipher = AES.new(key, AES.MODE_CTR)
    ct = cipher.nonce + cipher.encrypt(flag)

    print(f"{sigs = }")
    print(f"{ct = }")


if __name__ == "__main__":
    main()
