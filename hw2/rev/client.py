from Crypto.Cipher import ChaCha20

key   = bytes.fromhex("b77e4e717e701fd6b3455339ed30ff61541455d9b81e8911ff95d22e90c68363")
nonce = bytes.fromhex("15e3d227e0241ef0b4fd88ed")

# Encrypt
cipher = ChaCha20.new(key=key, nonce=nonce)
# Input ciphertext as hex (replace with your ciphertext)
while True:
	block = int(input("block id:"))
	if block==-1:
		break
	cipher.seek(block*64)
	ciphertext_hex = input("Enter ciphertext hex: ").replace(" ", "").replace("\n", "")
	ciphertext = bytes.fromhex(ciphertext_hex)
	plaintext = cipher.decrypt(ciphertext)

	# Output plaintext bytes in hex
	print(plaintext)
