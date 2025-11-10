#!/usr/bin/env python3
# Requires: angr, claripy
# pip install angr

import angr
import claripy
import logging

logging.getLogger('angr.sim_manager').setLevel(logging.DEBUG)

BINARY = "./super_angry_282177319491f1fe" # <- set your binary path here
ARGV_LEN = 32        # number of bytes to make symbolic (must be >= 32 here)

def main():
    proj = angr.Project(BINARY, auto_load_libs=False)
    sym_arg = claripy.BVS("sym_arg", 8 * ARGV_LEN)

    state = proj.factory.entry_state(args=[proj.filename, sym_arg])
    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=lambda s: b"Correct!" in s.posix.dumps(1), # dump stdout
                   avoid=lambda s: b"Incorrect!" in s.posix.dumps(1))
    # address should work but basic block could be wrongly identified, so try dump if needed
    if simgr.found:
        found = simgr.found[0]
        try:
            concrete = found.solver.eval(sym_arg, cast_to=bytes)
        except Exception:
            concrete = bytes(found.solver.eval(sym_arg, 8) for _ in range(ARGV_LEN))

        concrete_trimmed = concrete.split(b'\x00', 1)[0]
        print("Found candidate argv[1] (hex):", concrete_trimmed.hex())
        print("Found candidate argv[1] (ascii):", concrete_trimmed)
    else:
        print("No state found that reaches Correct! Try increasing ARGV_LEN or adjust the find address.")

if __name__ == "__main__":
    main()

