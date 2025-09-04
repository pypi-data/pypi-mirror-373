#!/usr/bin/env python3

#from pyfiglet import Figlet
from fire import Fire
import subprocess as sp
import os
import time
import sys
import random

from jusfltuls.check_new_version import is_there_new_version

#
#   NEEDS apt install toilet
#
#


lastp = []
lastp2 = []
lastp3 = []
MIN60 = 60


def get_uni(i, leng=False):
    uni=['\u2583','\u2584',
         '\u2585','\u2586',
         '\u2586','\u2587']
    if leng:
        # random number 1 .. len-1
        r = random.randint(0,len(uni)-2)+1
        #print("RANDOM",r)
        return r
    #print(i, len(uni) )
    k=i #% len(uni)
    #k=random.randint(0,k)
    return uni[k].encode("utf16","surrogatepass").decode("utf16")


def ping(who="192.168.0.1"):
    """
    one ping
    """
    global lastp,lastp2,lastp3
    CMD = "ping -w 1 -i 1 "+who
    l = get_uni(0, leng=True)
    try:
        res = sp.check_output(CMD.split()).decode("utf8")
        ok = "green"
        lastp.append(l)
        lastp2.append(l)
        lastp3.append(l)
    except:
        time.sleep(1)
        ok = "red"
        lastp.append(0)
        lastp2.append(0)
        lastp3.append(0)
    #print(lastp)
    #output(who,ok)
    return who,ok


def bar(  n=10 ):
    """
    do not run
    """
    global lastp,lastp2,lastp3
    while len(lastp)>n:
        lastp.pop(0)
    i = 0
    for color in lastp:
        i+=1
        if color==0:
            print('\033[0;31m', end="", flush=True)
        else:
            print('\033[0;32m', end="", flush=True)
        CHAR = get_uni( color )
        print(CHAR, flush=True, end="")
        if i>n: break
    print()

    #-----------second bar--------------
    i = 0
    suma = 0
    while len(lastp2)>MIN60*MIN60:
        lastp2.pop(0)
    for color in lastp2:
        i+=1
        if color!=0:color=1
        suma+= color
        if i>=MIN60:
            #print(i,suma)
            if suma==0:
                print('\033[0;31m', end="", flush=True)
            elif suma>=MIN60:
                print('\033[0;32m', end="", flush=True)
            else:
                print('\033[0;35m', end="", flush=True) #33ora 34blu
            CHAR = get_uni( 1 )
            print(CHAR, end="", flush=True)
            i = 0
            suma=0

    print()


    #-----------3rd bar--------------
    i = 0
    suma = 0
    while len(lastp3)>MIN60*MIN60*MIN60:
        lastp3.pop(0)
    for color in lastp3:
        i+=1
        if color!=0:color=1
        suma+= color
        if i>=MIN60*MIN60:
            if suma==0:
                print('\033[0;31m', end="", flush=True)
            elif suma==MIN60:
                print('\033[0;32m', end="", flush=True)
            else:
                print('\033[0;35m', end="", flush=True)
            CHAR = get_uni( 3 )
            print(CHAR, end="", flush=True)
            i = 0
            suma=0

    print()


def main():
    """
    indefinite ping wth minute and hour bars
    """

    is_there_new_version(package="jusfltuls", printit=True, printall=True)
    if len(sys.argv) < 2:
        print("Usage: pingy <addr>")
        sys.exit(1)
    addr = sys.argv[1]
    rang = MIN60

    for i in range(3600*24*7):
        #print("")
        time.sleep(0.1)
        #print(i)
        # ping fills lastp
        who,ok = ping(addr)
        os.system("clear")
        #print('\033[1;1H' + time.asctime(time.localtime()))
        print('\033[1;1H')
        output(who,ok)
        #print('\033[1;1H', " "*rang)
        # bar prints 1 bar
        bar( n = rang)
        #time.sleep(1)


def output(text="192.168.0.111", color="green"):
    """
    one shot ping
    """
    #f = Figlet(font='doom')  # too empty
    #f = Figlet(font='basic') # not clear
    #f = Figlet(font='colossal') # too large
    #f = Figlet(font='roman')  # too large
    #f = Figlet(font='univers') # too larrge
    #f = Figlet(font='rectangles') # too narrow
    #f = Figlet(font='computer') #worse than nancyj
    #f = Figlet(font='letters')

    #f = Figlet(font='nancyj') # better than letters

    CMD = "toilet -f mono9 "+text
    CMD = "toilet -f pagga "+text
    if color=="red":
        print('\033[0;31m', end="", flush = True)
        CMD = CMD + " f"
    if color=="green":
        print('\033[0;32m', end="", flush = True)
        CMD = CMD + " +"

    res = sp.check_call( CMD.split() )


    #print( f.renderText(text) )
    #print( res )

    #print( f.renderText("192 . 168 . 0 . 111 OK") )
    print('\033[0m', end="")

if __name__=="__main__":
    # Fire( {"o":output,
    #        "b":bar,
    #        "g":go,
    #        "p":ping})
    Fire( main )
