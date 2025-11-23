from Crypto.Cipher import ChaCha20

key   = bytes.fromhex("73ebe3380b21ca9adc6c021c55fe4a0e00c2a95ed9d31f472373cbf74f8e019b")
nonce = bytes.fromhex("e294175f7b8fd703822be472")
cipher = ChaCha20.new(key=key, nonce=nonce)
CTR = 9

ciphertext_hex = input("Enter ciphertext hex: ").replace(" ", "").replace("\n", "")
ciphertext = bytes.fromhex(ciphertext_hex)
plaintext = cipher.decrypt(ciphertext)
print(plaintext)
