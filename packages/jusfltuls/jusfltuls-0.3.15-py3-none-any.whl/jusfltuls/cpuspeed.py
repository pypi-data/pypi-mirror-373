#!/usr/bin/env python3

import numpy as np
import timeit
import random
import platform
import subprocess as sp
import re
from multiprocessing import Process, current_process
import decimal
import psutil


from fire import Fire
#https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python

# https://stackoverflow.com/questions/28284996/python-pi-calculation
#https://stackoverflow.com/questions/45887641/running-python-on-multiple-cores

# https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n?answertab=votes#tab-top
#https://github.com/vgratian/CosineBenchmark/blob/master/util/randvect.py
#https://github.com/vgratian/CosineBenchmark
#https://github.com/vgratian/CosineBenchmark/tree/master/lib/py_numpy

from jusfltuls.check_new_version import is_there_new_version

is_there_new_version(package="jusfltuls", printit=True, printall=True)





#------------------------------ global things ....................
# import itertools
# import sys
repe = 100
n0 = 1000*1000 # leave 1M
n = n0

# r = timeit.repeat( f'primesfrom2to({n})', setup="from __main__ import primesfrom2to" , repeat=repe, number=1 )
#print(f"{r:.4f} s for {repe}x {n/1000000} M ")
#print(f"{1000*r*n0/n:.3f} ms (avg {1000*ra*n0/n:.3f} ms) on milion primes:  {1/r:.0f} ")


minv=-10
maxv=10
size = 100
repe = 40

tenthousands = 10000
tenthousands = 10000 # this is usual.....
###tenthousands = 100000 # i try to x 10k
#tenthousands = 100000 # test me






def primesfrom2to(n):
    # https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    """ Input n>=6, Returns a array of primes, 2 <= p < n """
    sieve = np.ones(n//3 + (n%6==2), dtype=bool)
    sieve[0] = False
    for i in range(int( int(n**0.5)/3+1) ):
        if sieve[i]:
            k=3*i+1|1
            sieve[      int((k*k)/3)      ::2*k] = False
            sieve[int((k*k+4*k-2*k*(i&1))/3)::2*k] = False
    r = np.r_[2,3,((3*np.nonzero(sieve)[0]+1)|1)]
    #print(f"i... n={len(r)}, last={r[-1]}" )
    return r#np.r_[2,3,((3*np.nonzero(sieve)[0]+1)|1)]



def get_cosine_similarity( size ):
    """
    goes approximatelly linear with the size of a vector (1000 )
    """

    #size=10000
    a = np.array([ random.uniform(minv,maxv) for __ in range(size) ])
    random.shuffle(a)

    b = np.array([random.uniform(minv,maxv) for __ in range(size)])
    random.shuffle(b)

    eucl_magn = np.linalg.norm(a) * np.linalg.norm(b)
    return a.dot(b) / eucl_magn if eucl_magn else None





#----------- varies by fact 3 during calculation 100-6400
def pi():
    """
    Compute Pi to the current precision.

    Examples
    --------
    >>> print(pi())
    3.141592653589793238462643383

    Notes
    -----
    Taken from https://docs.python.org/3/library/decimal.html#recipes
    """
    decimal.getcontext().prec += 2  # extra digits for intermediate steps
    three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    decimal.getcontext().prec -= 2
    # print(s)
    return +s               # unary plus applies the new precision





# ------------ from 25ms to 0.4ms  100 - 51200
def pislow(size):
    pi = 0
    accuracy = size
    for i in range(0, accuracy):
        pi += ((4.0 * (-1)**i) / (2*i + 1))

    #print(pi)



# CORES ----- factor 3 differences in performace between 100-6400
def cores(size):
    worker_count = size
    worker_pool = []
    #print("started", end="")

    #decimal.getcontext().prec = size
    for _ in range(worker_count):
        # p = Process(target=get_cosine_similarity, args=(size,))
        # p = Process(target=pi, args=())

        p = Process(target=pislow, args=(200000,))

        p.start()
        worker_pool.append(p)
    #    print("X", end="")
    #print("i... FINISHING:", end="")
    for p in worker_pool:
        p.join()  # Wait for all of the workers to finish.
    #    print("X", end="")

    #print()
    # Allow time to view results before program terminates.
    # a = input("Finished")  # raw_input(...) in Python 2.
    # print(a)
    return None



##################################################################################

###if __name__=='__main__':

def benchmark_cores(core):
    module_name = __name__  # Get the current module name
    setup_code = f"from {module_name} import cores"
    r = timeit.repeat(f'cores({core})', setup=setup_code, repeat=3, number=1)
    return r#print(f"Timing results: {r}")

def benchmark_simil(size):
    module_name = __name__  # Get the current module name
    setup_code = f"from {module_name} import get_cosine_similarity"
    r = timeit.repeat(f'get_cosine_similarity({size})', setup=setup_code, repeat=3, number=1)
    return r#print(f"Timing results: {r}")


def main(mode = None):
    """
    two timeit calls
    """
    global size

    #=================================== get info===============
    pr = "CPU?"
    coremax = 0
    command = "cat /proc/cpuinfo"
    # pr = sp.check_output(command, shell=True).strip()
    all_info = sp.check_output(command, shell=True).decode("utf8").strip()
    for line in all_info.split("\n"):
        # print(line)
        if "model name" in line:
            pr = re.sub( ".*model name.*:", "", line,1)
            pr =  pr.replace("     "," ")
            pr =  pr.replace("    "," ")
            pr =  pr.replace("   "," ")
            pr =  pr.replace("  "," ")
        if "Model" in line:
            pr = re.sub( ".*Model.*:", "", line,1)
        if "processor" in line:
            coremax+=1
            # print("*")
    corereal = psutil.cpu_count(logical = False)
    if corereal is None:
        corereal = coremax
    # print(f"corereal == {corereal}")



    print(" ......... parallel tests, pi calculation .........")
    onecore = 0
    speedupl = []
    for core in range(1,coremax+4): # real number of cores...
        r = benchmark_cores(core)
        #r = timeit.repeat( f'cores({core})', setup="from __main__ import cores" , repeat=3, number=1 )
        ra = sum(r)/len(r)
        r = min(r)
        norm  = r*1000/core
        norma = ra*1000/core
        if onecore==0:
            onecore = norm
        real = "   "
        if corereal == core:
            real = "###"
        speedup = 1/(norm/onecore)
        speedupl.append( speedup )
        print(f"pi  10^5-iters{core:3d} cores {real} {norm:6.2f} ms (avg {norma:6.2f} ms)  speedup: {speedup:3.1f}x")



    print(" ......... one core speed with numpy norms .........")
    while True:
        r = benchmark_simil(size)
        #r = timeit.repeat(f'get_cosine_similarity({size})',setup="from __main__ import get_cosine_similarity",repeat=repe,number=1)
        ra = sum(r)/len(r)
        r = min(r)

        norm  = r/size*1000
        norma = ra/size*1000
        print(f"vector size {size:7d} : time = {r:.4f}s : min={1000*norm:.2f} ms (avg {1000*norma:.3f} ms) ... CPU (numpy): {1/norm:.0f}")

        if mode is  None:
            if r>0.1: # I dont want long  calculation
                print(" ... break with r>0.1", r, "    (time limit constraint)")
                break
            if 2*size>tenthousands: # I see at 12 000  there is a delay, it dissappears at 100 000
                print(" ... break with 10 0001", size)
                break
        size=size*2





    # print(f"{platform.node():15s} | {pr} | {core} cores  ")
    # print(f"1 core rating   | {1/norm:6.0f} |")
    print()

    # mark comes from CPU-Benchmark-API
    # origin	https://github.com/DarkAssassin23/CPU-Benchmark-API (fetch)


    print(f"| Hostname     | machine  | processor model                              | cores |real| speed/c |mark/c | mark |")
    print(f"|--------------|----------|----------------------------------------------|-------|----|---------|-------|------|")
    print( "| rpi03a1      | armv6l   |  Raspberry Pi Zero W Rev 1.1                 |     2 | 1.6|       9 |       |      |")
    print( "| rpi3b6b6     | aarch64  |  Raspberry Pi 3 Model B Plus Rev 1.3         |     4 | 2.9|      56 |       |      |")
    print( "| rpi4b71d     | armv7l   |  Raspberry Pi 4 Model B Rev 1.4              |     4 | 3.6|     112 |       |      |")
    print( "| janca20      | x86_64   |  Intel(R) Core(TM) i3-2367M CPU @ 1.40GHz    |     4 | 2.8|     188 |       | 830  |")
    print( "| tabs7fe      | aarch64  | CPU?                                         |     8 | 4.6|     310 |       |      |")
    print(f"|--------------|----------|----------------------------------------------|-------|----|---------|-------|----  |")
    print( "| mc2          | x86_64   |  Intel(R) Core(TM) i3-4005U CPU @ 1.70GHz    |     4 | 1.8|     260 |       | 1656 |")
    print( "| optic        | x86_64   |  Intel(R) Core(TM) i7 CPU 975 @ 3.33GHz      |     8 | 4.7|     438 |       | 3400 |")
    print( "| troja        | x86_64   |  Intel(R) Core(TM) i7-3610QM CPU @ 2.30GHz   |     8 | 4.3|     469 |       | 5106 |")
    print( "| zotac2       | x86_64   |  Intel(R) Core(TM) i7-2600K CPU @ 3.40GHz    |     8 | 4.5|     491 |       | 5488 |")
    print( "| zd84         | x86_64   |  Intel(R) Core(TM) i7-2600K CPU @ 3.40GHz    |     8 | 4.2|     507 |       | 5488 |")
    print( "| gigajm       | x86_64   |  Intel(R) Core(TM) i7-6500U CPU @ 2.50GHz    |     4 | 2.0|     572 |       | 3275 |")
    print( "| gigavg       | x86_64   |  Intel(R) Core(TM) i7-6500U CPU @ 2.50GHz    |     4 | 2.0|     583 |       | 3275 |")
    print( "| Filip        | x86_64   |  Intel(R) Core(TM) i5-4690K CPU @ 3.50GHz    |     4 | 3.4|     660 |       | 5663 |")
    print( "| casi         | x86_64   |  Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz     |     4 | 3.7|     712 |       | 6029 |")
    print( "| zen          | x86_64   |  Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz    |     8 | 3.3|     780 | 2127  | 6011 |")
    print( "| i3g10n1      | x86_64   |  Intel(R) Core(TM) i3-10100 CPU @ 3.60GHz    |     8 | 3.9|     812 | 2586  | 8716 |")
    print( "| core6a       | x86_64   |  Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz     |    12 | 5.8|     803 | 2633  | 12786|")
    print( "| core6b       | x86_64   |  Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz     |    12 | 5.8|     869 | 2633  | 12786|")
    print( "| zaba         | x86_64   |  12th Gen Intel(R) Core(TM) i3-12100         |     8 | 5.1|    1246 | 3276  | 12778|")
    print( "| super        | x86_64   |  AMD EPYC 7453 28-Core Processor             |    56 |23.8|     805 | 2522  | 50575|")
    print(f"|--------------|----------|----------------------------------------------|-------|----|---------|-------|      |")
    # print(f"| {platform.node():12s} | {platform.machine():8s} | {pr:44s} | {coremax:5d} | {corereal:2d} |  {1/norm:6.0f} |" )
    print(f"| {platform.node():12s} | {platform.machine():8s} | {pr:44s} | {coremax:5d} |{max(speedupl):4.1f}|  {1/norm:6.0f} |       |      |" )

    print()
    print("... sudo apt install linux-tools-common linux-tools-`uname -r`")
    print("... cpupower frequency-set -g performance powersave ondemand " )


if __name__ == "__main__":
    Fire(main)
    print("i...   check also   https://www.cpubenchmark.net/cpu_list.php")
