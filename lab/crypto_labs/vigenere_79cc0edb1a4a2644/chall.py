import string
import itertools
import random
import hashlib

charset = string.ascii_letters + string.digits + " ,.\n"
char_to_int = {c: i for i, c in enumerate(charset)}
n = len(charset)
keylen = 87


def filter_message(message):
    return "".join(c for c in message if c in charset)


def encode(message: str) -> list[int]:
    return [char_to_int[c] for c in message]


def decode(encoded: list[int]) -> str:
    return "".join(charset[i] for i in encoded)


def random_key(length: int) -> str:
    return "".join(random.choice(charset) for _ in range(length))


def encrypt(message: str, key: str) -> str:
    out = []
    for m, k in zip(encode(message), itertools.cycle(encode(key))):
        out.append((m + k) % n)
    return decode(out)


def main():
    with open("message.txt") as f:
        # this file contains an English text
        message = filter_message(f.read().strip())
    key = random_key(keylen)
    ciphertext = encrypt(message, key)
    print(f"{ciphertext = }")

    with open("flag.txt", "rb") as f:
        flag = f.read().strip()
    h = hashlib.shake_128(key.encode()).digest(len(flag))
    enc_flag = bytes(a ^ b for a, b in zip(flag, h))
    print(f"{enc_flag = }")


if __name__ == "__main__":
    main()
