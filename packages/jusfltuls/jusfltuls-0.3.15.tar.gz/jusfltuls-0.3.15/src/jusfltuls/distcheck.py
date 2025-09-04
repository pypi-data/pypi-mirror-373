#!/usr/bin/env python3


# -----------  jsut checking number of parameters.
# --- this script is called from py wrapper
# --- and paramters are passed using sys.argv
# --- and compatible with uv uvx
#

import subprocess as sp
import shlex
#from fire import Fire
import os
import sys

from jusfltuls.check_new_version import is_there_new_version

def main():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)
    command=f"distcheck.sh"

    if len(sys.argv) < 2:
        print("In python wrapper: Usage: distcheck")
#    else:
#        for i in sys.argv[1:]:
#            command = f"{command} {i}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("D... ...", script_dir)
    full_command = os.path.join(script_dir, command)
    print("D... ...", full_command)
    CMD = shlex.split(full_command)
    # it is interactive... FULL INTERACTIVITY
    result = sp.run( CMD )#, capture_output=True, text=True )
    #if result.returncode != 0:
    #    print("X... error calling", command)
    #print(result.stdout ) ####   REPOERT THE OUTPUT
    return
if __name__ == "__main__":
    main
