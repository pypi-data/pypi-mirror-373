import subprocess as sp

def main():
    print("Hello from verify!")

    ok = True

    CMD = ['/usr/bin/which','uconv']
    result = sp.run( CMD, capture_output=True, text=True )
    if result.returncode != 0:
        print("!... uconv not found... apt install icu-devtools")
        ok = False
    else:
        print("i... uconv found")


    CMD = ['/usr/bin/which','iwlist']
    result = sp.run( CMD, capture_output=True, text=True )
    if result.returncode != 0:
        print("!... iwlist not found... apt install ")
        ok = False
    else:
        print("i... iwlist found")


    CMD = ['/usr/bin/which','nmcli']
    result = sp.run( CMD, capture_output=True, text=True )
    if result.returncode != 0:
        print("!... nmcli not found... apt install ")
        ok = False
    else:
        print("i... nmcli found")

    #print()


if __name__ == "__main__":
    main()
