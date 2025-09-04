from fire import Fire
from glob import glob
import os
import subprocess as sp
from console import fg, bg, fx
import sys
import random
import string
import sys
import termios
import tty

from jusfltuls import verif_apt

# second layer
from unidecode import unidecode
#  What Unidecode provides is a middle road: the function unidecode() takes Unicode data and tries to represent it in ASCII characters (i.e., the universally displayable characters between 0x00 and 0x7F),
from jusfltuls.check_new_version import is_there_new_version



# GLOBAL
rename_all = False

#===============================================================
#    linux uconv  conversion to useful ASCII
#---------------------------------------------------------------
def run_uconv( inp):
    """
    echo Résumé | uconv -x Any-Latin\\;Latin-ASCII
    gives Resume
    """
    # res = uconv -x 'Any-Latin;Latin-ASCII'
    ###result = sp.run(['uconv', '-x', 'Any-Latin;Latin-ASCII', inp], capture_output=True, text=True)
    #outputs.append(result.stdout)
    #run(['uconv', '-x', 'Any-Latin;Latin-ASCII', file])
    result = sp.run(['uconv', '-x', 'Any-Latin;Latin-ASCII'], input=inp, capture_output=True, text=True)
    #print(result)
    return result.stdout

#===============================================================
#
#---------------------------------------------------------------
def badchars( inp ):
    chktext=inp
    chktext=chktext.replace("?","")
    chktext=chktext.replace("!","")
    #chktext=chktext.replace(".","")
    chktext=chktext.replace(",","")
    chktext=chktext.replace("   ","")
    chktext=chktext.replace("  ","")
    chktext=chktext.replace(" ","_")
    #chktext=chktext.replace("/","_")
    chktext=chktext.replace('"',"_")
    chktext=chktext.replace("'","") # Cest

    chktext=chktext.replace("\\","")

    #if inp.find("KarelK") >= 0: print("  >", chktext)

    badchar=" :<>`~!@#$%&*+=–!,–… ?--«»()‘…{}[]'"  # canbe /_ # i removed - #45
    badchar=" :<>`~!@#$%&*+=–!,… ?=«»()‘…{}[]'"  # canbe /_ # i removed - #45
    badchar=" :<>`~!@#$%&*+=–!,… ?=«»()‘…{}[]'|"  # canbe /_ # i removed - #45 I added |



    for i in range(len(badchar)):
        chktext=chktext.replace( badchar[i] ,"_")
        #if inp.find("KarelK") >= 0: print("  >", chktext)

    chktext=chktext.replace("____","_")
    chktext=chktext.replace("___","_")
    chktext=chktext.replace("__","_")
    #if inp.find("KarelK") >= 0: print("  >", chktext)

    return chktext



#===============================================================
#   aaa to aab to aac .............
#---------------------------------------------------------------
def get_random_string():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return random_string

#===============================================================
#   aaa to aab to aac .............
#---------------------------------------------------------------
def increment_string(s):
    s = list(s)
    i = len(s) - 1
    while i >= 0:
        if s[i] == 'z':
            s[i] = 'a'
            i -= 1
        else:
            s[i] = chr(ord(s[i]) + 1)
            break
    return ''.join(s)


#===============================================================
#
#---------------------------------------------------------------
def isduplicate_in( aaa, newf ):
    #duplicates = [item for item in set(newf) if newf.count(item) > 1]
    if aaa in newf:
        return True
    return False

#===============================================================
#
#---------------------------------------------------------------
def create_unique_filename(filepath, newf):
    """
    we know already filepath is duplicit. Add a suffinx and go
    newf is the list of existing filenames
    """
    # complete split.
    dir_name, file_name = os.path.split(filepath)
    base, ext = os.path.splitext(file_name)
    #suffix = 'aaa'
    new_filepath = None

    while (new_filepath is None) or (new_filepath in newf):
        suffix = get_random_string()
        if not ext:
            new_filepath = os.path.join(dir_name, f"{base}_{suffix}")
        else:
            new_filepath = os.path.join(dir_name, f"{base}_{suffix}{ext}")

    # while True:#new_filepath  in newf:
    #     # add suffix
    #     if not ext:
    #         new_filepath = os.path.join(dir_name, f"{base}_{suffix}")
    #     else:
    #         new_filepath = os.path.join(dir_name, f"{base}_{suffix}{ext}")
    #     if not(new_filepath in newf):
    #         break
    #     suffix = increment_string(suffix)
    # #print( "    dedup:", new_filepath)
    return new_filepath


#===============================================================
#
#---------------------------------------------------------------
def deduplicate_against( aaa, newf ):
    dupflag = False
    if isduplicate_in( aaa, newf):
        #newf[-1] = create_unique_filename(newf[-1], newf)
        #print(fg.magenta, f"{aaa} in {newf}", fg.default)
        dupflag = True
        return create_unique_filename(aaa, newf), dupflag
    return aaa, dupflag


#===============================================================
#        VATA remove
#---------------------------------------------------------------
# Function to replace all matching parts of VATA in filename with "_"
def replace_vata(filename ):
    """
    jedna blbost
    """
    VATA = "Kukaj to - Raj online filmov a serialov"
    for i in range(len(VATA), 6, -1):
        if VATA[:i] in filename:
            filename = filename.replace(VATA[:i], "_")
    return filename


#===============================================================
#        y/n
#---------------------------------------------------------------
def ask_yes_no(question: str = "?(y/n): ") -> bool:
    print(question, end='', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            key = sys.stdin.read(1).lower()
            #if key in ['y', 'n']:
            print(key, end="")
            return key == 'y'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def ask_yes_no_never(question: str = "Rename? (y/n/q/a  for yes no quit all ): ") -> str:
    print(question, end='', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            key = sys.stdin.read(1).lower()
            if key == 'y':
                print(key)
                return 'y'
            elif key == 'n':
                print(key)
                return 'n'
            elif key == 'a':
                print(key)
                return 'a'
            else:
                print(key)
                sys.exit(0)#return 'never'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)




#===============================================================
# *******   CAREFULL RENAME with CYAN   ***********************
#---------------------------------------------------------------
def rename_wise(old, new, dry=True, dupflag=False):
    global rename_all
    failed = True

    # Remember the current directory
    current_dir = os.getcwd()
    # Extract the directory and file names
    old_dir = os.path.dirname(old)
    old_file = os.path.basename(old)
    new_file = os.path.basename(new)
    # Change to the directory
    if old_dir is not None and old_dir != "":
        os.chdir(old_dir)
    # stop if no file
    if not os.path.exists(old_file):
        print(fg.red, old_file, fg.default, " NO SUCH FILE " )
        os.chdir(current_dir)
        return failed

    # Rename the file
    print( f"{fg.cyan}@ {os.getcwd()}{fg.default} :")
    print( f"  {fx.italic}   {fx.default}  {fg.gray}{old_file}{fg.default} " )
    print( f"  {fx.italic}new{fx.default}  {new_file} ", end="")
    if dupflag:
        print(bg.magenta, "DUP", bg.default, end="")

    # stop if file exists (error in dedup)
    if os.path.exists(new_file):
        print("\n", fg.red,"    ", new_file, fg.default, " file EXISTS already ")
        os.chdir(current_dir)
        return failed

    # question  y/n/q/a
    dorename = False
    if dry and (rename_all == False):
        dorename = ask_yes_no_never()
        if dorename == "y":
            dorename = True
        elif dorename == "n":
            dorename = False
        elif dorename == "a":
            dorename = True
            rename_all = True # ONE TIME SWITCH
    else:
        dorename = True


    if dorename:
        try:
            os.rename(old_file, new_file)
            print( bg.green, "OK", bg.default)
            failed = False
        except:
            print(bg.red, " XXX ", bg.default)
    else:
        print(fg.cyan, "DRY", fg.default)
        failed = True
    # return back to the initial directory and exit rename
    os.chdir(current_dir)
    return failed

#===============================================================
#
#---------------------------------------------------------------
#===============================================================
#
#---------------------------------------------------------------
def main(  ):
    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    verif_apt.main()
    args = sys.argv[1:]
    yesreally = '-y' in list(args)
    #for i in list(args):
    #    print("###", i)
    # remove -y from arguments
    args = list(arg for arg in args if arg != '-y')
    if args:
        args = [i.strip("\n") for i in args]
    #for i in list(args):
    #    print("###", i)
    #print("D... hi")
    #print("YES :", yesreally, type(yesreally) )
    #print("ARGS:", args)
    #if type(yesreally) != bool:
    #    print("D...  yesreally NOTBOOL:", yesreally)
    #    sys.exit(1)

    # --------  what files I take
    currf = []
    if args:
        currf = args
    else:
        currf = glob("**/*", recursive=True)
        currf.sort(key=lambda x: x.count(os.sep), reverse=True)

    #---NOW--------------- I have either all subdir OR arguments
    newf = []
    to_rename = 0 # those that differ
    unchanged=0 # those goods
    failed = 0 # failed to rename

    #for i in currf:
    #    print("FILE: ", i)
    print(f" ... files in the total lists : {len(currf)}")
    for i in currf:
        #print(f"D... {i} *******************")
        apc = i
        apc = replace_vata(apc) # jedna blbost
        apc = run_uconv(apc)    # uconv - Any Latin TO Useful ASCII
        apc = unidecode(apc)    # direct call To get ASCII
        #   now LATIN should be basically handled, remove bads
        apc = badchars(apc) #

        # deduplicate against current known list newf
        dupflag = False
        apc, dupflag= deduplicate_against(apc, newf )

        # now: consider it OK and unique, add to the new list
        newf.append( apc  ) # STORE FOR LATER REFERENCE.....

        # ====== The Only Files That Are Going To Change !!!!!!!
        if i != apc:
            to_rename += 1
            if apc in currf:
                print("X... HORROR:", apc)
                failed+= 1
            else:
                resfa = rename_wise(i, apc, dry=not yesreally, dupflag=dupflag)
                if resfa: # fail==true
                    failed+= 1
        else:
            unchanged+=1
    print("___________________________________________________________________dtox")
    # total - to_rename= goods.
    good_names = len(currf) - to_rename
    #      unchanged= {unchanged-to_rename}
    print(f"i... FILES TOTAL= {len(currf)}    TORENAME= {to_rename}     failed= {fg.red}{failed}{fg.default}    renamed= {fg.green}{to_rename-failed}{fg.default}")
    #duplicates = [item for item in set(newf) if newf.count(item) > 1]

if __name__ == "__main__":
    #verif_apt.main()
    main()
