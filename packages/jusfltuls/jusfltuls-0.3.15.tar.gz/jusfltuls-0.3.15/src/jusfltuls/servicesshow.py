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
import click

from jusfltuls.check_new_version import is_there_new_version

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-n', '--no-decoration', is_flag=True, help='Disable decoration')
def main(no_decoration):


    is_there_new_version(package="jusfltuls", printit=True, printall=True)


    command=f"servicesshow.sh"

    #if len(sys.argv) > 1 and sys.argv[1].find("h") >= 0:
    #    # If any parameter : help
    #    print("HELP:  In python wrapper: Usage:    sudo `which ssshow`     <par> [par2 ...]")
    #    sys.exit(0)

    #if len(sys.argv) > 1 and sys.argv[1].find("") >= 0:
    #else:
    if no_decoration:
        command = f"{command} no_decoration"
    #    for i in sys.argv[1:]:
    #        command = f"{command} {i}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    #print("D... ...", script_dir)
    full_command = os.path.join(script_dir, command)
    #print("D... ...", full_command)
    CMD = shlex.split(full_command)
    # IF it is interactive... FULL INTERACTIVITY    result = sp.run( CMD )
    # ELSE
    result = sp.run( CMD, capture_output=True, text=True )
    if result.returncode != 0:
        print("X... error calling", command)
    print(result.stdout ) ####   REPOERT THE OUTPUT
    return
if __name__ == "__main__":
    main()
