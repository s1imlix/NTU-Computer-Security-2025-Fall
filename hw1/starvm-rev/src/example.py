#!/usr/bin/env python3
with open("payload", "wb") as f:
    f.write(b"STARP")

    # function
    f.write(p32(1))
    f.write(p32(0))

    # storage
    f.write(p32(0))

    # program
    program = b""
    program += p8(0x01)
    #  program += p8(0x60) ?
    program += p8(0x00)
    f.write(p32(len(program)))
    f.write(program)
