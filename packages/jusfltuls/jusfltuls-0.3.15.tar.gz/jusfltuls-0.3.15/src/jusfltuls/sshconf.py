#!/usr/bin/env python3
#
# OUTDATED/USING CHRONY       ##### ntpsec-ntpdate ntp
#
#  chrony confing: +bindcmdaddress 0.0.0.0; +cmdallow all
#
# FIREWALL CHECK
# sudo ufw allow proto tcp from 1.3 to any port 8000 # sudo ufw allow proto tcp from 1.3 to any port 8099
#  for mass copy to SMB
# ls -1tr | tail -1 | xargs -I III  smbclient -U user%pass  //x.x.x.x/DATA   -c 'put "III"'
#
#
#### import pyautogui
import numpy as np # convert screen (black) to array

from terminaltables import AsciiTable,SingleTable

from blessings import Terminal  #
import time
import datetime

import threading

import fire

import subprocess as sp
import shlex

import socket
import os

#import ray
from influxdb import InfluxDBClient
from threading import Thread
import sys


import copy # to copy dict !

# from fire import Fire
from PIL import ImageGrab

from colorclass import Color, toggles    #
from console import fg, bg, fx
pause_main = False




# it is updated in functions
t = Terminal()


real_width = 10 # i try to mesure the width of the table

# source of IPs
CONFFORI = os.path.expanduser("~/.ssh/config")
CONFF = os.path.expanduser("~/.ssh/config")


tab_src = [ ['n', 'host','user','hostname','label', 'inf', 'ntp', 'cam','vnc','mys','ser','bor','mgo'] ] # LOWER!
# I dont spam 5678 etc...anymore
tab_src = [ ['n', 'host','user','hostname','label', 'inf', 'ntp', 'cam'] ] # LOWER!
selected_n = '0'
alldics_origin = {}
alldics = {}
DEBUG = False



import socket


def launch_command(name=None):
    CMD = name#"sleep 7"
    args = shlex.split(CMD)
    env = os.environ.copy()
    process = sp.Popen(args, env=env, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    process.poll()



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
#print(get_ip())


#--------https://stackoverflow.com/questions/2408560/python-nonblocking-console-input
# ON ENTER
# CALL WITH CALLBACK FUNCTION AS A PARAMETER
class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        self.block = False
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return

    def pause(self):
        self.block = True

    def unpause(self):
        self.block = False





def my_callback(inp):
    """
    Read input + enter from keyboard. In the thread.
    """
    global alldics, alldics_origin, selected_n, pause_main
    #evaluate the keyboard input
    r = "autored"
    ybg = "autobgyellow"
    b = "autoblack"
    w = "autowhite"


    print('You Entered: /{}/'.format(inp) , flush = True)
    #time.sleep(2)

    if inp == 'r': #### KEY ####
        load_resources( CONFF)
        return


    already_selected = False
    for i in alldics.keys():
        # remove color
        if alldics[i]['host'].find("*")>0:
            already_selected = True
            #print("D... ALREADY SELECTED", alldics[i]['host'])
        #print("callback",alldics[i]['host'])
        #alldics[i]['host'] = alldics[i]['host'].rstrip("*")
        alldics[i]['host']  = Color('{'+w+'}'+alldics_origin[i]['host'] +'{/'+w+'}') # ONE COLOR ONLY
        alldics[i]['label']  = Color('{'+w+'}'+alldics_origin[i]['label'] +'{/'+w+'}') # ONE COLOR ONLY
        # set color

    if not already_selected:
        for i in alldics.keys():
            # if alldics[i]['n']==inp:
            if alldics[i]['n'] in inp:
                #alldics[i]['host']+="*"
                alldics[i]['host']  = Color('{'+ybg+'}'+'{'+b+'}'+alldics_origin[i]['host'] +'*{/'+b+'}'+'{/'+ybg+'}') #yellow
                alldics[i]['label']  = Color('{'+ybg+'}'+'{'+b+'}'+alldics_origin[i]['label'] +'*{/'+b+'}'+'{/'+ybg+'}') #yellow
                selected_n = inp
        return



    #========================= GO THROUGH ALL SELECTED
    #========================= GO THROUGH ALL SELECTED
    #========================= GO THROUGH ALL SELECTED

    if selected_n != '0': #### if something i selected, go one by one.... ###

        # ----------precalculate screens ----------------
        screenset = []
        if "c" in inp:
            # img = ImageGrab.grab() ###  NOT WITH UBUNTU 22 AND WAYLAND... X11
            # xmaxw = img.size[0]
            # ymaxh = img.size[1]

            # -----variant with py
            #img = pyautogui.screenshot()
            #--------------------------------------------  REMOVING THIS GRAB
            #img = ImageGrab.grab()
            #img = np.array(img.convert("RGB"))
            ymaxh = 1920#img.shape[0]
            xmaxw = 1080#img.shape[1]

            nimg = len(selected_n)
            if xmaxw>(640*(nimg)):
                print(f"ONE ROW  {xmaxw} ...  #=={nimg} need=={640*nimg}" )
                print(f"ONE ROW  {xmaxw} ...  #=={nimg} need=={640*nimg}" )
                for i in range(nimg):
                    screenset.append( f"{(i)*640+1}x{1}")
            else:
                print("TWO ROWS for now")
                jaj=0
                for i in range(nimg):
                    if (i+1)*640<=xmaxw:# <=nimg/2:
                        jaj=i
                        screenset.append( f"{(i)*640+1}x{1}")
                    else:
                        screenset.append( f"{(i-jaj-1)*640+1}x{481}")

            print( f"{xmaxw} {screenset}")
            print( f"{xmaxw} {screenset}")
            print( f"{xmaxw} {screenset}")
            print( f"{xmaxw} {screenset}")



        #### clusterssh ##### and return after
        if (len(selected_n)>1) and ('s' in inp): #### KEY ####
            #print("D... ssh "+alldics_origin[i]['host'])
            CMD = "clusterssh "
            CMD = "mssh "
            for i in alldics.keys():
                if alldics[i]['n'] in selected_n:
                    if CONFF!=CONFFORI: # no xforwarding and things in the case of not.config
                        CMD = CMD + alldics_origin[i]['user']+"@"+alldics_origin[i]['hostname']+"  "
                    else:
                        CMD = CMD +alldics_origin[i]['host']+"  "
            CMD+=" &"
            print(CMD)
            os.system(CMD)
            #launch_command(CMD)
            return






        #### Why I dont have a problem with "s" ???
        # --------------------------------   "s" in  vs.  "s" == ----------------
        for i in alldics.keys():


            ### not cluster, single terminals
            if alldics[i]['n'] in selected_n:

                print(f"D... i am in selected dictkey {selected_n} , input {inp}")
                if inp == 'h': #### KEY ####
                    ####  #####
                    HELP = f"""HELP______________________________________
  inf ... check for influx - port 8086
  ntp ... check chronyc -h IP tracking  NOT /ntpdig -dc HOST/  d-time  in [ms]
        .  NOT install ntp ntpsec-ntpdate; ufw allow 123/udp on client
  cam ... check port 8000 - expect video
    (c) .  flashcam uni :8000/video -p ~/.flashcam_HOST
  vnc ... check for VNCserver on port 5600
    (v) .  vncviewer -passwd ~/.vnc/HOST
  mys ... see 5678 myservice
    (m) .  see cronvice NOT myservice infinite on HOST
"""
                    with open("/tmp/sshconf.help","w") as f:
                        f.write(HELP)
                    #os.system(f"terminator -e 'bash -c \"cat /tmp/sshconf.help ; sleep 25\" '")
                    CMD = f"xterm -e 'bash -c \"cat /tmp/sshconf.help ; sleep 25\" '"
                    launch_command(CMD)



                 ############ --------- ############
                 ############  ssh      ############
                 ############ --------- ############
                if 's' == inp: #### KEY ####
                    #print("D... ssh "+alldics_origin[i]['host'])

                    if CONFF!=CONFFORI: # no xforwarding and things in the case of not.config
                        CMD = "xterm -e 'bash -c \"ssh \""+alldics_origin[i]['user']+"\"@"+alldics_origin[i]['hostname']+"; \" '"
                    else:
                        CMD = "xterm -e 'bash -c \"ssh "+alldics_origin[i]['host']+"; \" '"
                    print(CMD)
                    #
                    launch_command(CMD)
                    #args = shlex.split(CMD) # env=env,
                    #process = sp.Popen(args,  stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    #process.poll()
                    #
                    #os.system(CMD)


                 ############ --------- ############
                 ############   SSH interm##########
                 ############ --------- ############
                if inp == 'S': #### KEY ####
                    #print("D... ssh "+alldics_origin[i]['host'])
                    ###kthread.pause()
                    pause_main = True
                    os.system("ssh "+alldics_origin[i]['host'] )
                    #CMD = "ssh "+alldics_origin[i]['host']
                    #launch_command(CMD) # NOTHERE!!!!!!!!!!
                    pause_main = False
                    ###kthread.unpause()





                               #### pingy ##### for ANY IN
                 ############ --------- ############
                 ############  pingy    ############
                 ############ --------- ############
                if 'p' in inp: #### KEY ####
#                    os.system("xterm -geometry 65x12 -e 'bash -c \"pingy.py  "+alldics_origin[i]['hostname']+"; \" '")
                    #os.system("terminator -e 'bash -c \"pingy.py  "+alldics_origin[i]['hostname']+"; \" '")
                    CMD = "xterm -e 'bash -c \"pingy     "+alldics_origin[i]['hostname']+"; \" '"
                    launch_command(CMD)


                                 #### rsync ~/DATA/ ##### for ANY IN
                 ############ --------- ############
                 ############  rsync    ############
                 ############ --------- ############
                if ('R' in inp): #### KEY ####
                    #print("D... rsync -av "+alldics_origin[i]['host'])
                    CMD = "rsync -av --progress "
                    CMD = CMD + alldics_origin[i]['user']+"@"+alldics_origin[i]['host']+":~/DATA/  "
                    CMD+=" ~/DATA/REMOTEDATA/ "

                    #CMD = f"xterm -geometry 100x20+10+600 -e \"bash -c ' {CMD} ; echo ALL OK; sleep 5' \" & "
                    CMD = f"xterm -geometry 100x20+10+600 -e 'bash -c \" {CMD} ; echo ALL OK; sleep 5\" '"
                    print(CMD)
                    launch_command(CMD)
                    #os.system(CMD)
                    # return # with clusterssh i had return not to mess up



                               #### camera ##### 5000
                 ############ --------- ############
                 ############  C 5000   ############
                 ############ --------- ############
                if 'C' == inp: #### KEY #### PORT 5000 !!
                    code = os.path.expanduser("flashcam")
                    code = os.path.expanduser("pogucam")

                    mXY=""
                    if len(screenset)>0: mXY=f"-X {screenset.pop(0)}"

                    PASFILE="~/.pycam_"+i
                    PASFILE="~/.config/flashcam/.flashcam_upw_"+i
                    PASFILE=os.path.expanduser(PASFILE)
                    if not os.path.isfile(PASFILE):
                        print("D... NO PASFILE ",PASFILE)
                        print("D... NO PASFILE ",PASFILE)
                        print("D... NO PASFILE ",PASFILE)
                        PASFILE=""
                    else:
                        PASFILE=" -q "+PASFILE

                    CMD = "terminator -e 'BASH_ENV=~/.bashrc bash -c \"  export PATH=$PATH:$HOME/.local/bin;  "+code+" uni http://"+alldics_origin[i]['hostname']+":5000/video  "+PASFILE+" \" ; sleep 5'"

                    CMD = "xterm -T "+alldics_origin[i]['hostname']+":5000  -geometry 80x5 -bg black -fg yellow -e 'BASH_ENV=~/.bashrc bash -c \" export PATH=$PATH:$HOME/.local/bin; "+code+" uni http://"+alldics_origin[i]['hostname']+f":5000/video {mXY} "+PASFILE+" \" ;  sleep 1' &"

                    CMD = "xterm -T "+alldics_origin[i]['hostname']+":5000  -geometry 130x5 -bg black -fg yellow -e 'BASH_ENV=~/.bashrc bash -c \" export PATH=$PATH:$HOME/.local/bin; "+code+"  http://"+alldics_origin[i]['hostname']+f":5000/video  \" ' &"
                    print(CMD)
                    print(CMD)
                    print(CMD)
                    os.system(CMD)
                    #launch_command(CMD)

                    time.sleep(2)
                                  #### camera ##### 8000
                 ############ --------- ############
                 ############  c 8000   ############
                 ############ --------- ############
                elif 'c' in inp: #### KEY ####
                    # code = os.path.expanduser("~/02_GIT/GITLAB/pycamfw/better_imagezmq/izmq_send2.py")
                    # uniwrec.py disp -v http://...video # no /@end
                    # code = os.path.expanduser("~/02_GIT/GITLAB/pycamfw/better_imagezmq/uniwrec.py")
                    #
                    #code = os.path.expanduser("~/02_GIT/GITLAB/flashcam/bin_flashcam.py")
                    code = os.path.expanduser("flashcam")
                    code = os.path.expanduser("pogucam")
                    #

                    PASFILE="~/.pycam_"+i
                    PASFILE="~/.config/flashcam/.flashcam_upw_"+i
                    PASFILE=os.path.expanduser(PASFILE)
                    if not os.path.isfile(PASFILE):
                        print("D... NO PASFILE ",PASFILE)
                        print("D... NO PASFILE ",PASFILE)
                        print("D... NO PASFILE ",PASFILE)
                        PASFILE=""
                    else:
                        PASFILE=" -q "+PASFILE
                    # CMD = "terminator -e 'bash -c \""+code+" disp -v http://"+alldics_origin[i]['hostname']+":8000/video "+PASFILE+"; \" '"
                    mXY=""
                    if len(screenset)>0: mXY=f"-X {screenset.pop(0)}"
                    #                    CMD = "terminator -e 'BASH_ENV=~/.bashrc bash -c \" export PATH=$PATH:$HOME/.local/bin; "+code+" uni http://"+alldics_origin[i]['hostname']+f":8000/video {mXY} "+PASFILE+" \" ;  sleep 5'"

                    CMD = "xterm -T +"+alldics_origin[i]['hostname']+":8000 -geometry 80x5 -bg black -fg yellow -e 'BASH_ENV=~/.bashrc bash -c \" export PATH=$PATH:$HOME/.local/bin; "+code+" uni http://"+alldics_origin[i]['hostname']+f":8000/video {mXY} "+PASFILE+" \" ' &"
                    # POGUCAM
                    CMD = "xterm -T +"+alldics_origin[i]['hostname']+":8000 -geometry 130x5 -bg black -fg yellow -e 'BASH_ENV=~/.bashrc bash -c \" export PATH=$PATH:$HOME/.local/bin; "+code+"  http://"+alldics_origin[i]['hostname']+f":8000/video  \"  ' &"
                    print(CMD)
                    #print(CMD)
                    ##print(CMD)
                    #print(CMD)
                    #print(CMD)
                    #time.sleep(5)
                    #with open("debug","a") as f:
                    #    f.write(CMD)

                    os.system(CMD)
                    #launch_command(CMD)  # cannot do here with all this

                    time.sleep(2)





                #                #### vnc #####
                #  ############ --------- ############
                #  ############  vnc      ############
                #  ############ --------- ############
                # if 'v' in inp: #### KEY ####
                #     passwfile = os.path.expanduser('~/.vnc/'+alldics_origin[i]['host'])
                #     if os.path.isfile(passwfile):
                #         #os.system("terminator -e 'bash -c \"vncviewer -passwd "+passwfile+" "+alldics_origin[i]['hostname']+"; \" '")
                #         CMD = "xterm -e 'bash -c \"vncviewer -passwd "+passwfile+" "+alldics_origin[i]['hostname']+"; \" '"
                #         launch_command(CMD)

                #     else:
                #         #os.system("terminator -e 'bash -c \"echo create passw:; echo vncpass "+passwfile+"; sleep 1;vncviewer "+alldics_origin[i]['hostname']+"; \" '")
                #         CMD = "xterm -e 'bash -c \"echo create passw:; echo vncpass "+passwfile+"; sleep 1;vncviewer "+alldics_origin[i]['hostname']+"; \" '"
                #         launch_command(CMD)


                 ############ --------- ############
                 ############  cris     ############
                 ############ --------- ############
                #### myservice #####
                if 'm' in inp: #### KEY ####
                    # CMD = "xterm -geometry 100x20 -e 'bash -c \"ssh "+alldics_origin[i]['host']+" \"script /dev/null;myservice2 infinite;\"  \" '"
                    # CMD = "xterm -geometry 100x20 -e 'bash -c \"ssh "+alldics_origin[i]['host']+" myservice2 a;  \" '"
                    # CMD = "xterm -geometry 100x20 -e 'bash -c \"ssh "+alldics_origin[i]['host']+" myservice2 a; read; \" '"

                    # xterm -geometry 100x20 -e "bash -c \"ssh -t  ojr@janca screen -x myservice2_infinite; sleep 3\" "

                    CMD = "ssh -t "+alldics_origin[i]['host']+" ~/.local/bin/cronvice"
                    #CMD =  "xterm -geometry 100x20 -e \"bash -c ' " + CMD + " ' \" "
                    CMD =  "xterm -geometry 100x20 -e \"bash -c ' " + CMD + " ' \"  "



                    print("D... ", CMD )
                    #os.system( CMD)
                    launch_command(CMD)





#--------------------end callback--------------------
#--------------------end callback--------------------
#--------------------end callback--------------------
#--------------------end callback--------------------
#--------------------end callback--------------------
#--------------------end callback--------------------
#--------------------end callback--------------------






def user_from_scan22(host):
    CMD = f"nmap -sV {host} -p 22"
    res = sp.check_output(CMD.split()).decode("utf8")
    res = res.split("\n")
    res = [x for x in res if x.find("Ubuntu")>=0 ]
    res = [x for x in res if x.find("OpenSSH")>=0 ]
    # i am using ubuntu user for
    if len(res)>0 and res[0].find("8.9p1")>0:
        return "ubuntu"
    elif len(res)>0:
        return "pi"
    else:
        return "none"


def get_all_arp():
    CMD = f"arp -na"
    print(f"D... get_all_arp ... CMD=={CMD}", file = sys.stderr)
    try:
        res = sp.check_output(CMD.split()).decode("utf8")
        res = res.split("\n")
    except:
        print("X... arp problem ... are you on android?", file = sys.stderr)
        res=[]
    ddd = {}
    for i in res:
        if len(i.split())<3: break
        #print("D...",i, i.split())
        ip = i.split()[1]
        mac = i.split()[3]
        if ip in ddd.keys(): continue
        ip = ip.replace("(","")
        ip = ip.replace(")","")
        ddd[ip] = mac
    return ddd





#---------------------------------------------------------------------
def myip():
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

import ipaddress

def load_resources( param=""):
    """
    loads the data from ~/.ssh/config
    only if "#Label something" is in the record, it is taken into the table
    IF _given_ CONFIG exists => scans and creates and NEW NAME
    """
    global CONFF
    n = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    global alldics, alldics_origin, tab_src
    alldics = {}
    alldics_origin = {}

    if os.path.exists( os.path.expanduser( f"~/.ssh/{param}" ) ):
        CONFF = os.path.expanduser( f"~/.ssh/{param}" )
        print(f"i... file {CONFF} exists - I use a specific config")
        #sys.exit(0)


    if param == "arp":
        print("D... I do   arp scan")
        # me = myip()+"/24"
        CMD = f"arp -na"
        print(f"D... CMD=={CMD}")
        res = sp.check_output(CMD.split()).decode("utf8")
        res = res.split("\n")
        ddd = {}
        for i in res:
            if len(i.split())<3: break
            #print("D...",i, i.split())
            ip = i.split()[1]
            mac = i.split()[3]
            if ip in ddd.keys(): continue
            ip = ip.replace("(","")
            ip = ip.replace(")","")
            ddd[ip] = mac
        # ddd = sorted([(value,key) for (key,value) in ddd.items()])
        # ddd = sorted( (value,key) for (key,value) in ddd.items(), key = ipaddress.IPv4Address )

        # ddd = sorted(zip(ddd.values(), ddd.keys()),  key = ipaddress.IPv4Address )

        # ddd = {k: v for k, v in sorted(ddd.items(), key = ipaddress.IPv4Address, key=lambda item: item[1])}
        # sorted(ddd.values(), key = ipaddress.IPv4Address )
        MYCONFIG = ""
        mactaken = []
        for host in  sorted( ddd.keys() , key = ipaddress.IPv4Address ):  #
            if ddd[host].find("b8:27:eb")>=0:
                label = "raspberry 3/z"
                user = "pi"
            elif ddd[host].find("dc:a6:32:")>=0:
                label = "raspberry 4"
                user = "pi"
            else:
                continue
                user = "ooo"
                label = "some"
            if ddd[host] in mactaken:
                continue

            # get influx hostname

            remhost = host
            try:
                CMD = f'tdb_io ls infl  -ip {host}'
                res = sp.check_output(CMD.split()).decode("utf8")
                res = res.split("\n")
                res = [ x for x in res if x.find("i_am_")>=0]
                remhost = res[0].split("i_am_")[1]
            except:
                print(f"D... no influx on {host} OR tdb_io not installed")

            MYCONFIG+= f"\nHost {remhost}\n    HostName {host}\n    User {user}\n    #Label {label}\n"
            mactaken.append( ddd[host] )


        # print(res)
        print( MYCONFIG )
        #with open( os.path.expanduser("~/.ssh/config"),"w" ) as f:
        #    f.write(MYCONFIG)
        sys.exit(1)


    if param == "nmap":
        print("i... I do nmap ping scan, safe also on android ", file = sys.stderr)
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        h_name = s.getsockname()[0]
        print( "i... my IP address", h_name , file = sys.stderr )
        s.close()

        # import  scapy
        # from scapy.all import scapy,ARP,Ether,srp,arp ing
        # ans,unans = arping("192.168.0.0/24", verbose=0)
        # for s,r in ans:
        #     print("{} {}".format(r[Ether].src,s[ARP].pdst))


        # import socket
        # h_name = socket.gethostname()
        # print(h_name)
        # h_name = socket.gethostbyname(h_name)

        CMD = f"nmap -sn {h_name}/24"
        print(f"D... CMD=={CMD}" , file = sys.stderr)
        #sys.exit(0)
        res = sp.check_output(CMD.split()).decode("utf8")
        res = res.split("\n")
        #print(res)
        res = [x for x in res if (x.find("report for")>0) ]
        #mac = [x for x in res if (x.find("MAC Add")==0) ]

        print(res,  file = sys.stderr )
        #print(mac,  file = sys.stderr )

        hosts = [ x.split(" ")[-1].replace("(","").replace(")","") for x in res] # take IP and avoid ()
        print(hosts, file = sys.stderr)


        arps = get_all_arp()

        MYCONFIG = ""

        for host in hosts:
            label = "some"
            user = os.getlogin()  # my current user

            if host in arps:
                mac = arps[host]
                if mac.find("b8:27:eb")>=0:
                    label = "raspberry 3/z"
                    user = user_from_scan22(host)
                    #user = "pi"
                elif mac.find("dc:a6:32:")>=0:
                    label = "raspberry 4"
                    user = user_from_scan22(host)
                    #user = "pi"
            else:
                mac = ""

            remhost = host
            remhost2 = socket.getfqdn(host).split(".")[0]
            if not remhost2.isdigit():
                remhost = remhost2


            # try:
            #     CMD = f'tdb_io ls infl  -ip {host}'
            #     print(f"i...  {CMD}")
            #     res = sp.check_output(CMD.split()).decode("utf8")
            #     res = res.split("\n")
            #     res = [ x for x in res if x.find("i_am_")>=0]
            #     remhost = res[0].split("i_am_")[1]
            # except:
            #     print(f"D... no influx on {host} OR tdb_io not installed")

            MYCONFIG+= f"\nHost {remhost}\n    HostName {host}\n    User {user}\n    #Label {label}\n"

        print(MYCONFIG)
        sys.exit(0)

    #----------------- Original idea -  if config not present.... create it...
    if  (os.path.exists(CONFF))  and (os.stat(CONFF).st_size != 0):
        print("i... trying to open", CONFF)
        with open(CONFF) as f:
            lines = f.readlines()
        print("i... ok")
    else:
        print(f"!... NO ssh confi file exists. - try to create one:")
        print(f" ... nmap 192.168.0.1/24 ; sshconf.py nmap")
        print(f" ... parameter nmap  =={param}")

        user = os.environ.get('USER')
        ip = get_ip()
        newip = ".".join(ip.split(".")[:-1])

        machine = f"""
Host core6a
   HostName {newip+".22"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host core6b
   HostName {newip+".23"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host gigavg
   HostName {newip+".14"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host filip
   HostName {newip+".17"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host nasa
   HostName {newip+".20"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host gigajm
   HostName {newip+".21"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host tr24a
   HostName {newip+".15"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __


Host tr24b
   HostName {newip+".16"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __

Host kroha
   HostName {newip+".44"}
   IdentityFile ~/.ssh/id_rsa
   User {user}
   #Label: __


"""
        print(machine)
        sys.exit(0)




    lines = "".join(lines).split("Host ")
    lines = [ i.rstrip().lstrip().replace("  "," ") for i in lines]
    lines = [ i.replace("  "," ") for i in lines]
    lines = [ i.replace("  "," ") for i in lines]
    lines = [ i.replace("  "," ") for i in lines]

    while lines[0] == "":
        lines.pop(0)
    while lines[-1] == "":
        lines.pop()
    #print(lines)


    for i in lines: # Full record
        onedic = {} # EMPTY ONE LINE-RECORD  DICT
        its = i.split("\n")
        its = [i.strip() for i in its]

        onedic['host'] = its[0].lower()
        # loop for all fields in one record
        for j in its:

            for la in tab_src[0]: # Check the presence in tabsrc...HostName
                # here is wise trick to split by lowercase la
                # User/Label in FILE and user/label ... as a key in onedic
                # 20221219
                # I changed all MGO to mgo and the key will be always lower
                #  but it is not important
                #print(" >",la)
                if (j.lower().find( la )==0) or (j.lower().find( la )==1):
                    if la.lower()!='host':
                        #print( j.lower().split(la)[-1].strip()  )
                        #print( j.lower()  )
                        #print( "---")
                        #onedic[la.lower()] = j.lower().split(la)[-1].strip()
                        tojoin = j.strip().split(" ")[1:]
                        onedic[la.lower()] = " ".join(tojoin)

        # jump out---in no #LABEL
        if not 'label' in onedic:
            continue

        onedic['n'] = str(n[0])
        n.pop(0)
        if  onedic['host'] in alldics:
            print("X.. !!! host name already exists:", onedic['host'])
            sys.exit(1)
        alldics[onedic['host']] = onedic
    # when allics is ok, create the origin
    alldics_origin = copy.deepcopy(alldics)
    print("D... ALLDICS LOEADED",alldics)
    print("D... ALLDICS LOEADED",alldics_origin)



#----------------------------------------------------------- UPDATE
def update_table( okresults_dict , okvalues_dict={} ):
    global alldics, alldics_origin, tab_src
    tabsrc2 = tab_src.copy()


    neven = 0
    for i in alldics.keys():  # key is host, isnt it?
        #onedic = alldics[i]

        w = "autowhite"
        r = "autored"
        y = "autoyellow"
        g = "autogreen"
        abg = "autobgblack"

        # print( onedic )
        # print('D... updatetable - key',i)
        # print("D... u origins:",alldics_origin)
        # print("D... u origins I-hostname ok?:",alldics_origin[i]['hostname'] )


        # -------- ok_results dictionary :   fill it

        if 'ping' in okresults_dict.keys() and type(okresults_dict['ping']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['ping']:
                #print("OK")
                #alldics[i]['hostname'] = Color('{'+g+'}'+alldics_origin[i]['hostname']+'{/'+g+'}') # ONE COLOR ONLY
                alldics[i]['hostname'] = f"{fg.lightgreen}{alldics_origin[i]['hostname'].strip()}{fg.default}" # COLOR ONLY
                #print("...",alldics[i]['hostname'] )
            else:
                #alldics[i]['hostname'] = Color('{'+r+'}'+alldics_origin[i]['hostname']+'{/'+r+'}') # ONE COLOR ONLY
                alldics[i]['hostname'] = f"{fg.tomato}{alldics_origin[i]['hostname'].strip()}{fg.default}" # ONE COLOR ONLY
                #print("xxx",alldics[i]['hostname'] )


        if 'ssh' in okresults_dict.keys() and type(okresults_dict['ssh']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['ssh']:
                alldics[i]['user'] = Color('{'+g+'}'+alldics_origin[i]['user']+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['user'] = Color('{'+r+'}'+alldics_origin[i]['user']+'{/'+r+'}') # ONE COLOR ONLY


        alldics[i]['inf'] = " "
        alldics[i]['ntp'] = " "
        alldics[i]['cam'] = " "
        #alldics[i]['vnc'] = " "
        # I spam 5678 no more
        #alldics[i]['mys'] = " "
        #alldics[i]['ser'] = " "
        #alldics[i]['bor'] = " "
        #alldics[i]['mgo'] = " "



        # INF
        if 'inf' in okresults_dict.keys() and type(okresults_dict['inf']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['inf']:
                # here I can perform another query?
                line = ""
                res = "OK "
                CMD = [ 'curl', '-G', '-m','2', f'http://{alldics_origin[i]["hostname"]}:8086/query?',
                        '--data-urlencode', 'q=show databases']
                #========================= this locks at some moment.
                try:
                    pipe = sp.Popen(CMD, stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.DEVNULL)
                    line = pipe.stdout.readline().decode("utf8").rstrip("\n")
                except Exception as ex:
                    print(ex)
                    line = ""

                if "i_am_" in line:
                    res = line.split("i_am_")[-1].split('"')[0]
                else:
                    res = "OK "
                alldics[i]['inf'] = Color('{'+g+'}'+res+'{/'+g+'}') # ONE COLOR ONLY
                #alldics[i]['inf'] = Color('{'+g+'}'+"OK "+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['inf'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY


        # NTP
        if 'ntp' in okresults_dict.keys() and type(okresults_dict['ntp']) == list:
            myip = alldics_origin[i]['hostname']
            if myip in okresults_dict['ntp']: # if IP in []
                # print("D... okvalues",okvalues_dict)
                if myip in okvalues_dict.keys():
                    rx = okvalues_dict[myip]
                else:
                    rx = 0.0
                alldics[i]['ntp'] = Color('{'+g+'}'+ str(rx) +'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['ntp'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY


        # CAM
        if 'cam' in okresults_dict.keys() and type(okresults_dict['cam']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['cam']:
                alldics[i]['cam'] = Color('{'+g+'}'+"OK "+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['cam'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        # VNC
        # if 'vnc' in okresults_dict.keys() and type(okresults_dict['vnc']) == list:
        #     if alldics_origin[i]['hostname'] in okresults_dict['vnc']:
        #         alldics[i]['vnc'] = Color('{'+g+'}'+"OK "+'{/'+g+'}') # ONE COLOR ONLY
        #     else:
        #         alldics[i]['vnc'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        # MYS
        if 'mys' in okresults_dict.keys() and type(okresults_dict['mys']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['mys']:
                alldics[i]['mys'] = Color('{'+g+'}'+"mys"+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['mys'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        if 'ser' in okresults_dict.keys() and type(okresults_dict['ser']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['ser']:
                alldics[i]['ser'] = Color('{'+g+'}'+"OK "+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['ser'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        if 'bor' in okresults_dict.keys() and type(okresults_dict['bor']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['bor']:
                alldics[i]['bor'] = Color('{'+g+'}'+"brg"+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['bor'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        if 'mgo' in okresults_dict.keys() and type(okresults_dict['mgo']) == list:
            if alldics_origin[i]['hostname'] in okresults_dict['mgo']:
                alldics[i]['mgo'] = Color('{'+g+'}'+"brg"+'{/'+g+'}') # ONE COLOR ONLY
            else:
                alldics[i]['mgo'] = Color('{'+r+'}'+"---"+'{/'+r+'}') # ONE COLOR ONLY

        neven+=1
        if neven%3 == 0:
            oline =  [  #Color('{'+abg+'}'+alldics[i]['n'] + '{/'+abg+'}'),
                        f"{bg.darkslategray} {alldics[i]['n'].strip()} {bg.default}",
                        #Color('{'+abg+'}'+alldics[i]['host']    +'{/'+abg+'}'),
                        f"{bg.dimgray}{alldics[i]['host'].strip()}{bg.default}",
                        #Color('{'+abg+'}'+alldics[i]['user']    +'{/'+abg+'}'),
                        f"{bg.darkslategray}{alldics[i]['user'].strip()}{bg.default}",
                        #Color('{'+bg+'}'+alldics[i]['hostname']+'{/'+bg+'}'),
                        f"{bg.darkslategray}{alldics[i]['hostname'].strip()}{bg.default}",
                        #Color('{'+abg+'}'+alldics[i]['label']   +'{/'+abg+'}'),
                        f"{bg.darkslategray}{alldics[i]['label'].strip()}{bg.default}",
                        Color('{'+abg+'}'+alldics[i]['inf']     +'{/'+abg+'}'),
                        Color('{'+abg+'}'+alldics[i]['ntp']     +'{/'+abg+'}'),
                        Color('{'+abg+'}'+alldics[i]['cam']     +'{/'+abg+'}'),
                        #Color('{'+bg+'}'+alldics[i]['vnc']     +'{/'+bg+'}')
                        #Color('{'+bg+'}'+alldics[i]['mys']     +'{/'+bg+'}'),
                        #Color('{'+bg+'}'+alldics[i]['ser']     +'{/'+bg+'}'),
                        #Color('{'+bg+'}'+alldics[i]['bor']     +'{/'+bg+'}'),
                        #Color('{'+bg+'}'+alldics[i]['mgo']     +'{/'+bg+'}')
            ]
        else:
            oline =  [  f" {alldics[i]['n']} ",
                        alldics[i]['host'],
                        alldics[i]['user'],
                        alldics[i]['hostname'],
                        alldics[i]['label'],
                        alldics[i]['inf'],
                        alldics[i]['ntp'],
                        alldics[i]['cam'],
                        #alldics[i]['vnc']
                        #alldics[i]['mys'],
                        #alldics[i]['ser'],
                        #alldics[i]['bor'],
                        #alldics[i]['mgo']
            ]
            #oline = [ Color('{'+r+'}'+k+'{/'+r+'}') for k in oline ]
        tabsrc2.append( oline )
    #    print(onedic)
    return tabsrc2





def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    MYIP=s.getsockname()[0]
    print("i... IP From 8.8.8.8:\t",s.getsockname()[0])
    s.close()
    return MYIP




def ping_port( IPT, port, ret ):
    """
    IPT = ip, port=port, ret=dict that is merged later
    if port == -1 ... ping
    if port is number ... conn/dicsonn
    ntp? -
    WHAT IS RET????
    """
    global DEBUG
    if DEBUG: print("D...                      "+IPT+":"+str(port) )
    if port == -1:
        command = 'ping -c 1 -w 2 '+ IPT
        res = sp.call(command.split(), stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.DEVNULL)
        if DEBUG: print("D.... .... ping....  ",IPT,res)
        ret[IPT] = res # impotrant
        return IPT, res

    if port == -2:
        command = 'ntpdate -q '+ IPT # ??????
        command = f"chronyc -h {IPT} tracking"
        #  Root delay .. max  error if maximum asymetry
        #  Root dispersion ,... min error estimation  travel_time * clockskew
        # command = 'ntpdig -dc '+ IPT  # last line ---
        #if DEBUG: print("D... ",command)
        #res =
        #ret[IPT] = 0
        ntp = 999
        try:
            pipe = sp.Popen(shlex.split(command), stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.DEVNULL)
            lines = pipe.stdout.readlines() #.decode("utf8").rstrip("\n")
            #print(lines)
            line = [x.decode("utf8").rstrip("\n") for x in lines if x.decode("utf8").find("Root delay")>=0 ][0]
            #print(line)
            line = line.strip().split(":")[-1].strip() # '0.004657954 seconds'
            #print("X1", line)
            ntp = line.split()[0].strip() # get seconds
            #print("X2", ntp)
            ntp = round(1000*abs(float( ntp )),1) # make rounded float
            #print("X3", ntp)
            #print("*x*", IPT, res)
            ret[IPT] = -1.0 * ntp # 0 #ntp # <0 is good NOT NICE...I NEED TO SEND <0
            res = 0 # good result
        except:
            ret[IPT] = 1 # BAD RESULT
            res = 1      # BAD
        # ------------------
        # try:
        #     pipe = sp.Popen(command.split(), stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.DEVNULL)
        #     line = pipe.stdout.readline().decode("utf8").rstrip("\n")
        #     if DEBUG: print("D1... ... line = ",line)
        #     if len(line.split())>4:
        #         res = 0
        #         ntp = round(1000*abs(float( line.split()[3] )),1)
        #     else:
        #         if DEBUG: print("D... ... split failed, leaving")
        #         res = 1
        #         ntp = -1
        #     if DEBUG: print("D.... .... ntpsec-ntpdate....  ",IPT,res, ntp)
        #     ret[IPT] = -1.0*ntp # important? - 0/1 .... or <0with ntp
        # except:
        #     ret[IPT] = 1
        #     res = 1
        #print("---- return", IPT, res, ret[IPT], "----")
        return IPT, res

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((IPT, port))
    except socket.error:
        print(f"!... maybe NO DNS for {IPT}:{port}")
        result = -1

#    if result == 0:
#        print(" Open")
#    else:
#        print(" ----")
    sock.close()
    ret[IPT]=result # important
    return IPT,result






# 8086 influx
def discover_port(iplist, port='ssh'):
    """
    checks ports or PING
    """
    ret={}
    t=[]
    okresults = []
    okvalues = {}

    if port=='ssh':
        portn = 22
    elif port == 'ntp':
        portn = -2
    elif port == 'cam':
        portn = 8000
    elif port == 'inf':
        portn = 8086
    #elif port == 'vnc':
    #    portn = 5900
    #elif port == 'mys':
    #    portn = 5678
    elif port == 'ping':
        portn = -1
    #elif port == 'bor':
    #    portn = 2222
    #elif port == 'mgo':
    #    portn = 27017
    #elif port == 'ser':
    #    portn = 8099
#   # elif port == 'ser':
#   #     portn = 9010
    else:
        return


    if DEBUG: print("D... looking for port",port, portn)

    #for i in range(1,254):
    #for i in range(60,63):
    for i in iplist:
        #IPT=IP3+"."+str(i)
        IPT = i
        t.append( Thread(target=ping_port,args=(IPT,portn,ret)) )
        t[-1].start()
    for i in t:
        i.join()
    #print("\n",ret) #================== ret contains
    # print()


    for i,v in ret.items():
        #print(i,v)
        if v<=0:
            okresults.append( i ) # append the IP
        if v==0:
            okvalues[i]=0 # append the IP
        else: # <0 can be NTPQ
            okvalues[i]= -v  # append the IP


    # print("i... ok==", sorted(okresults), sorted(okvalues) )

    # with open( os.path.expanduser("~/.myservice_discover8086"),"w") as f:
    #      for i in okresults:
    #          print("D... writing to dicover",i)
    #          f.write( i +"\n")
    #          write_influx(i,MYIP) #
    return okresults, okvalues






def flat_scan(port = 22):
    """
    scan all range if local IP adresses
    """
    MYIP = get_my_ip()
    IP3=".".join( MYIP.split(".")[:3] )
    print("i... Scan ",IP3 +".*")
    iplist = list(range(1,254))

    discover_port(iplist,  port)









def main():#  param="ok", debug = False):
    global DEBUG, real_width, pause_main
    # toggles.disable_all_colors()

    # --------------------- replacement ------------------------------
    param=f"ok"
    debug = False

    # ----------wacky way
    if len(sys.argv) < 2:
        print("USAGE:  <par> [par2 ...]")
    else:
        n = 1
        for i in sys.argv[1:]:
            if n == 1:
                param = i
            elif i == "-d":
                debug = True

    print(param, debug)
    if param.find("~/.ssh/") >= 0:
        param = param.split("~/.ssh/")[-1]
    if param.find(os.path.expanduser("~/.ssh/")) >= 0:
        param = param.split(os.path.expanduser("~/.ssh/"))[-1]

    DEBUG = debug
    print(param, debug)
    #sys.exit(0)

    load_resources(param)
    # print( list(alldics.keys() ) )
    #sys.exit(0)

    #start the Keyboard thread
    kthread = KeyboardThread(my_callback)

    i = 0 # SCANS ALL AT ONCE
    #i = 1 # SCANS later
    okresults_dict = {}
    okvalues_dict = {}
    while True:
        # --------- here we discover different ports at different times -----------
        #print("D... WHILE",alldics_origin)
        i+=1
        DT = 120 # seconds
        # then every 3 seconds one port is scanned over all IP
        if (i%(10)) == 1:
            iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
            okresults_dict['ping'],_ = discover_port(iplist, 'ping')
        if (i%(DT)) == 6:
            iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
            okresults_dict['ssh'],_ = discover_port(iplist, 'ssh')
        # if (i%(DT)) == 27:
        #     iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
        #     okresults_dict['vnc'],_ = discover_port(iplist, 'vnc')
        if (i%(DT)) == 9:
            iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
            okresults_dict['cam'],_ = discover_port(iplist, 'cam')
        if (i%(DT)) == 12:
            iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
            okresults_dict['inf'],_ = discover_port(iplist, 'inf')
        #if (i%(DT)) == 15:
        #    iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
        #    okresults_dict['mys'],_ = discover_port(iplist, 'mys')
        # if (i%(DT)) == 18:
        #     iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
        #     okresults_dict['bor'],_ = discover_port(iplist, 'bor')
        # if (i%(DT)) == 21:
        #     iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
        #     okresults_dict['mgo'],_ = discover_port(iplist, 'mgo')
        # if (i%(DT)) == 24:
        #     iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
        #     okresults_dict['ser'],_ = discover_port(iplist, 'ser')

        # this is special... return values of ntpq
        if (i%(DT)) == 3:
            iplist = [ alldics_origin[i]['hostname'] for i in list(alldics.keys()) ]
            #print("D... ", iplist)
            res = discover_port(iplist, 'ntp')
            #print("D...", res)
            okresults_dict['ntp'],okvalues_dict = res


        print(f" ... done {i} {i%DT}",end="")
        if (i%DT> 27) and (i%DT<120):
            print(f" ... ping is <10s old; other {i%DT-27}+ sec")
        else:
            print(" ")
        time.sleep(0.5)

        tabsrc2 = update_table( okresults_dict, okvalues_dict )


        table = SingleTable(tabsrc2)
        table.padding_left = 1
        table.padding_right = 1

        if not debug:
            print( t.clear(),end="" )

        if not table.ok:
            table.padding_left=0
        if not table.ok:
            table.padding_right=0
        while not table.ok:
            j=0
            for k in tabsrc2:
                tabsrc2[j] = k[:-1]
                j+=1
            table = SingleTable(tabsrc2)
            table.padding_left = 0
            table.padding_right = 0

        # ========================================================================
        # ========================================================================
        # ======= THIS IS PRINT TABLE MOMENT   ===================================
        # ========================================================================
        # ========================================================================
        print(table.table )

        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")," ...(c)am (m)ys (s)sh (S)sh (p)ingy (v)nc (R)sync (h)elp")
        time.sleep(1)
        while pause_main:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
