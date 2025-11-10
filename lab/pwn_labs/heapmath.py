from pwn import *

p = remote('10.113.0.1', 10405)

def calc_tcache(malloc_dict, free_list, chunk_size):
    tcache = []
    for free in reversed(free_list):
        msize = malloc_dict[free]
        if msize > chunk_size - 0x8 - 0x10 and msize <= chunk_size - 0x8:
            tcache.append(free)
    return tcache

def get_chunk_size(a: int):
    for s in range(0x20, 0x100, 0x10):
        if a > s - 0x8 - 0x10 and a <= s - 0x8:
            return s
    return 0x100

# tcache chall
prob = p.recvuntil(b'\n\n')
prob = [b.decode() for b in prob.split(b'\n')[1:-2]]

print(prob)

# separate lines starting with char and with free
frees = []
mallocs = {}
for line in prob:
    if line.startswith('free'):
        frees.append(line.split('(')[1].split(')')[0])
    else:
        tmp = line.split('=')
        name = tmp[0].split('*')[1].strip()
        size = int(tmp[1].split('malloc(')[1].split(')')[0], 16)
        mallocs[name] = size

print(mallocs)

p.recvlines(2)
p.recvuntil(b'>')
tcache_sizes = [0x30, 0x40]
for size in tcache_sizes:
    tcache = calc_tcache(mallocs, frees, size)
    if tcache:
        ans = ' --> '.join(calc_tcache(mallocs, frees, size)) + ' --> NULL'
    else:
        ans = 'NULL'
    p.sendline(ans.encode())
    p.recvlines(2)

prob = p.recvlines(3)[1:]
target, value = [a.decode().strip() for a in prob[0].split(b'(')[1].split(b')')[0].strip().split(b'==')]
info(f'{target} == {value}')
value = int(value, 16)
ask = prob[1].decode()[0]

for c in range(ord(target), ord(ask)):
    csize = mallocs[chr(c)]
    after_round = get_chunk_size(csize)
    info(f'{hex(csize)} -> {hex(after_round)}')
    value += after_round

# value += 0x10 # Last one's header

info(f'{ask} == {hex(value)}')
p.sendline(str(hex(value)).encode())
p.interactive()
"""
----------- ** index chall ** -----------
unsigned long *X = (unsigned long *) malloc(0x50);
unsigned long *Y = (unsigned long *) malloc(0x50);
Y[8] = 0xdeadbeef;
X[?] == 0xdeadbeef	(just send an integer, e.g. "8")
> $ 20
unsigned long = 8 bytes, (0x50 + 0x10) / 8 + 8 = 20


----------- ** tcache fd chall ** -----------
free(X);
free(Y);
assert( Y == 0x55d7ad54f440 );
fd of Y == ?	(send as hex format, e.g. "0x55d7ad54f440")
> $ 0x55d7ad54f3e0

tcache fd points to mem start

----------- ** fastbin fd chall (final) ** -----------
[*] Restore the chunk to X and Y
Y = (unsigned long *) malloc(0x50);
X = (unsigned long *) malloc(0x50);
[*] Do something to fill up 0x60 tcache -> so it goes fastbin
...
[*] finish
free(X);
free(Y);
assert( Y == 0x55d7ad54f440 );
fd of Y == ?	(send as hex format, e.g. "0x55d7ad54f440")
> $ 0x55d7ad54f3d0

fastbin fd points to chunk header
"""
