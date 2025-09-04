#!/usr/bin/env python3
"""
Whatever number on system will be displayed in a graph:
 get_temp()
 get_lamax() #hcitool
 get_mem()
get_dbm() # control panel in router with selenium
"""
#import plotext.plot as plx
import matplotlib
#matplotlib.use('module://drawilleplot')
#matplotlib.use('module://matplotlib-sixel')
import matplotlib.pyplot as plt
import numpy as np
import subprocess as sp
import time
import os

from fire import Fire

import datetime as dt
from jusfltuls.check_new_version import is_there_new_version

def move (y, x):
    print("\033[%d;%dH" % (y, x))




def graph_update(tlis,ymin=50,ymax=105, label="label", show=True):
    #os.system("clear")

    if type(tlis) == dict:
        x = tlis['x']
        y = tlis['y']
    else:
        x=range(len(tlis))
        y=tlis

    #print('x:',x)
    #print('y:',y)


    # DOESNT WORK
    #fig = plt.figure(figsize=(5, 2))
    plt.plot( x,y , '.' , label=label)
    plt.ylim(top=ymax) #ymax is your value
    plt.ylim(bottom=ymin) #ymin is your value
    #plt.legend()
    #print("\033c", end="")
    #os.system('cls' if os.name == 'nt' else 'clear')
    if show:
        #plt.show()
        #plt.clf()
        NAME = "/tmp/jutu_graphs.jpg"
        print("saving ", NAME)
        print("use  neowatch kitty +kitten icat /tmp/jutu_graphs.jpg "   )
        plt.savefig(NAME)
        time.sleep(1)
    #print(chr(27) + "[2J")









def get_temp():
    res=sp.check_output('cat /sys/class/thermal/thermal_zone2/temp'.split()).decode('utf8')
    #res=sp.check_output('cat /sys/class/thermal/thermal_zone0/temp'.split()).decode('utf8')
    res=int(res)/1000
    print("temp:", res)
    return res

def get_lamax():
    res=sp.check_output('hcitool lq 4F:BE:4C:63:9E:7C'.split()).decode('utf8').strip()
    #print(res)
    res=res.split(":")[-1].strip()
    #print("/{}/".format(res))
    res=int(res)
    return res


def get_mem():
    res=sp.check_output('cat /proc/meminfo'.split()).decode('utf8').strip()
    res = res.split("\n")
    tot = [x for x in res if x.find("MemTotal")>=0 ]
    ava = [x for x in res if x.find("MemAvailable")>=0 ]
    res = [x for x in res if x.find("MemFree")>=0 ]
    #print(res)
    res=res[0].split()[1].strip()
    tot=tot[0].split()[1].strip()
    ava=ava[0].split()[1].strip()
    #print(f"/{res}/")
    res=int(res)/1000000
    tot=int(tot)/1000000
    ava=int(ava)/1000000
    return tot,ava,res






def mem():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    tlis=[]
    tlis2=[]
    maxx=60*3

    maxy=1000
    miny=1000
    os.system("clear")
    while 1==1:
        tot,ava,res=get_mem()
        #if res>maxy: maxy=res
        #if res<miny: miny=res
        #res=get_lamax()
        tlis.append(res)
        tlis2.append(ava)

        if len(tlis)>maxx:
            tlis=tlis[1:]
            tlis2=tlis2[1:]
        if len(tlis)<4:
            continue
        move(1,1)
        graph_update(tlis2,0,tot,"MEMA",show=False)
        graph_update(tlis,0,tot,"MEMF")

    return res









#=====================================webscrape DLINK

"""
  pip install selenium
  pip install webdriver_manager
"""
def get_dbm():
    print("consider workon dlink ")
    print("consider workon dlink ")
    print("consider workon dlink \n\n\n")
    from bs4 import BeautifulSoup as bs
    import time
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager

    webpage = r'https://192.168.0.1/controlPanel.html'
    ########################### ALL DRIVER HERE ######################
    #=========== it started to make errors with 83.
    options = webdriver.ChromeOptions()

    options.add_argument('--headless') # NO VISIBLE BROWSER WINDOW

    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    #ignore INVALID CERTIFICATE
    options.add_argument('--ignore-certificate-errors')
    #ChromeDriverManager().clearPreferences()
    #ChromeDriverManager().setup()
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    except:
        print("X... there was an exception in installing ChromDrive...maybe ok")
        driver = webdriver.Chrome(options=options)
        #driver = webdriver.Chrome()
        #


    driver.maximize_window()

    driver.get( webpage )
    #time.sleep(1)

    txt = driver.page_source
    #print(txt)
    #print("################################################# GOT COUNTRIES")


    username = driver.find_element('xpath', '//*[@id ="tf1_usrName"]')
    password = driver.find_element('xpath', '//*[@id ="tf1_password"]')

    #print(username)
    #print(password)

    username.send_keys("admin")
    password.send_keys("")


    #driver.find_element("name","btSave").click()
    driver.find_element("xpath",'//*[@id ="btSave"]').click()


    driver.get(webpage)
    #time.sleep(2.5)

    #print("searching operator")
    operator = driver.find_element("xpath",'//*[@id ="tf1_tmpl_cpinternetinfo"]')
    #print(operator)
    opt = operator.text.split()
    dec = [ float(x.split("dBm")[0]) for x in opt if x.find("dBm")>0 ][0]
    #print(opt)
    #print( dec)
    res = dec
    return res


def dbm():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)


    #pip install selenium
    #pip install webdriver_manager


    tlisx=[]
    tlisy=[]
    maxx=60*3
    start = dt.datetime.now()

    os.system("clear")
    while 1==1:
        #res=get_temp()
        res=get_dbm()
        #res = -89

        tlisx.append( (dt.datetime.now() - start).total_seconds() )
        tlisy.append(res)

        if len(tlisx)>maxx:
            tlisx=tlisx[1:]
        if len(tlisy)>maxx:
            tlisy=tlisy[1:]
        if len(tlisx)<4:
            continue
        tlis = { 'x':tlisx, 'y':tlisy }
        #print(tlis)
        graph_update(tlis,-130,0,"signal")



def temp():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    tlis=[]
    maxx=60*3

    os.system("clear")
    while 1==1:
        res=get_temp()
        #res=get_lamax()
        tlis.append(res)

        if len(tlis)>maxx:
            tlis=tlis[1:]
        if len(tlis)<4:
            continue
        #print(tlis)
        graph_update(tlis,10,105,"CPU temp")



def lamax():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    tlis=[]
    maxx=60*3

    os.system("clear")
    while 1==1:
        #res=get_temp()
        res=get_lamax()
        tlis.append(res)

        if len(tlis)>maxx:
            tlis=tlis[1:]
        if len(tlis)<4:
            continue
        graph_update(tlis,0,405,"LAMAX")

if __name__ == "__main__":
    Fire( {"temp":temp,
           "mem":mem,
           "dbm":dbm,
           "lamax":lamax} )
