from tqdm import tqdm
import random

rng1_out = None 
rng2_out = None 
flag_enc = None
with open('./output.txt', 'r') as f:
    data = bytes.fromhex(f.read())
    rng1_out = data[:4096]
    rng2_out = data[4096:8192]
    flag_enc = data[8192:]

"""
crack rng1
"""
from sage.all import *


n = sum([i for i in range(48,763,35)]) # can be seen as one big lfsr
print('linear complexity n:', n)
print('required bits >=', 2*n)
F = GF(2)

observed_bits = []
for byte in rng1_out:
    for i in range(8):
        observed_bits.append(F((byte >> (7-i)) & 1))

required_bits = observed_bits[:2*n] # need at least 2n bits to crack LFSR of length n

from sage.matrix.berlekamp_massey import berlekamp_massey 
print('cracking rng1...')
P = berlekamp_massey(required_bits)
L = P.degree() 
state = observed_bits[:L]
# print(P, P[:5])
"""
print('Verifying LFSR of degree:', L)
for i in tqdm(range(L, len(observed_bits))):
    next_bit = sum([P[j]*state[j] for j in range(0, L)]) 
    assert next_bit == observed_bits[i]
    state.pop(0)
    state.append(next_bit)
"""
print(f'continue to predict rng1 for {len(flag_enc)*8} bits...')
state = observed_bits[-L:] # reset state
predicted_rng1 = []
for _ in tqdm(range(len(flag_enc)*8)):
    next_bit = sum([P[j]*state[j] for j in range(0, L)]) 
    predicted_rng1.append(int(next_bit))
    state.pop(0)
    state.append(next_bit)

print('rng1 done')

"""
crack rng2
solve system of linear equations in GF(2) with gf2bv
"""
from gf2bv import LinearSystem
from gf2bv.crypto.mt import MT19937

N = 624
BITS = 32
STATE_BITS = N * BITS

observed = []
for byte in rng2_out:
    for i in range(8):
        observed.append((byte >> (7-i)) & 1)

#observed_bits = [rand.getrandbits(1) for _ in range(STATE_BITS)] 
#print(observed_bits)
observed_bits = observed[:STATE_BITS]


ls = LinearSystem([32]*N) 
mt = ls.gens()
# shamelessly copied from https://github.com/maple3142/gf2bv/blob/master/examples/mt.py
rng = MT19937(mt)
zeros = [rng.getrandbits(1) ^ o for o in observed_bits] + [mt[0] ^ 0x80000000] # wtf?
print('solving rng2...')
sol = ls.solve_one(zeros)
rng2 = MT19937(sol).to_python_random()

print('verifying rng2 for', len(observed_bits), 'bits...')
assert all(rng2.getrandbits(1) == observed[i] for i in range(len(observed)))
print('rng2 verified')
print('continue to predict rng2 for', len(flag_enc)*8, 'bits...')


predicted_rng2 = []
for i in tqdm(range(len(flag_enc)*8)):
    predicted_rng2.append(rng2.getrandbits(1))
print('rng2 done')

"""
decrypt flag
"""
print('decrypting flag...')
# group bits into bytes
rng_bits = [sum([a,b]) & 1 for a, b in zip(predicted_rng1, predicted_rng2)]
rng_bytes = []
for i in range(0, len(rng_bits), 8):
    byte = 0
    for j in range(8):
        byte = (byte << 1) | rng_bits[i+j]
    rng_bytes.append(byte)

flag = bytes(a ^ b for a, b in zip(flag_enc, rng_bytes))
print('flag:', flag)



