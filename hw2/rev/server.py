from Crypto.Cipher import ChaCha20


key   = bytes.fromhex("73ebe3380b21ca9adc6c021c55fe4a0e00c2a95ed9d31f472373cbf74f8e019b")
nonce = bytes.fromhex("e294175f7b8fd703822be472")
cipher = ChaCha20.new(key=key, nonce=nonce)
CTR = int(input("Enter CTR value: ")) # flag was 9

HEXFILE = './test.txt'
SAVEFILE = './test.jpg'


with open(HEXFILE, "r") as file:
    hex = file.read()
    print(len(hex))
    bytes_data = bytes.fromhex(hex)
    cipher.seek(CTR*64)    
    plaintext = cipher.decrypt(bytes_data)
    # save as jpg
    with open(SAVEFILE, "wb") as img_file:
        img_file.write(plaintext)
    print(f"Image saved as {SAVEFILE}")
"""
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
"""
