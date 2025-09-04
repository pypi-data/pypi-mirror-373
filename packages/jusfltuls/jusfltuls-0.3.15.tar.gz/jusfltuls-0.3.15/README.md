# Set of useful tools

- dtox - rename from whatever coding to ascii, works recursively
- cpuspeed - simple cpu test to compare
- pingy - big color font ping
- zoter - lauch zotero and make backup of sqlite after
- wavescan - display wifis in terminal
- sshconf - show status of PCs from ~/.ssh/config (if they have #Label: line)
- smartnow - looks to disks TO FINISH WITH NOTIFATOR


# TOOLS

## mci

 - It takes 23 minutes to extract csv of 1,7GB with 18M lines
 - `influx -import -path=file -precision ns` will import export.lp

### help to initial contact
 - `nc -vz 130.xxx.xxx.xxx 8086` - ping
 - `curl -sI http://130.x.x.x:8086/health` - version
 - `influx  -host 130.x.x.x -port 8086` - enters

## uv astral OLDTEXT

compilation/publication
```
rm dist/jusfl* ; gca && bumpversion patch &&  uv build && uv publish
```

see this

https://docs.astral.sh/uv/guides/package/#next-steps

**This is most important uv decision**

https://docs.astral.sh/uv/concepts/projects/init/#applications



**packaged system + MAINFEST.in is needed to have other data (bash script)  (or even --lib)**

```
# packaged app

uv init --package jusfltuls
# creates also  src/jusfltuls/*

```


**But no main function can have standard parameters**

```
def main():
    """
    indefinite ping wth minute and hour bars
    """
    if len(sys.argv) < 2:
        print("Usage: pingy <addr>")
        sys.exit(1)
    addr = sys.argv[1]
```

**Look how to handle parameters with sys.argv**

- pingy
 - smartnow - also python wrapper and MANIFEST.in
