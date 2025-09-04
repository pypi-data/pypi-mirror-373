import os
import subprocess
import time
from datetime import datetime
"""
 just transformed from bash to python....
 it was more transparent than doing it with wrappers
"""


EXECUTABLE_PATH = "~/01_Dokumenty/04_ourpublic/zotero_install/Zotero_linux-x86_64/zotero"
SQLITE_PATH = "~/01_Dokumenty/04_ourpublic/ZOTERO"


def main():
    # Paths
    zname = os.path.expanduser(EXECUTABLE_PATH)
    dbpath = os.path.expanduser(SQLITE_PATH)
    dbname1 = os.path.join(dbpath, "zotero.sqlite")
    better_bibtex = os.path.join(dbpath, "better-bibtex.sqlite")

    # Check if Zotero executable exists
    if os.path.exists(zname):
        # Check if database exists
        if os.path.exists(dbname1):
            initial_mod_time = os.path.getmtime(dbname1)
            tag1 = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"{tag1} ZOTERO STARTED initime {initial_mod_time}")

            # Call Zotero
            subprocess.run([zname])

            final_mod_time = os.path.getmtime(dbname1)
            tag2 = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"{tag2} ZOTERO ENDED {final_mod_time}")
            time.sleep(1)

            # Check if database was modified
            if final_mod_time > initial_mod_time:
                tag = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"cp {dbname1} {dbname1}.{tag}")
                subprocess.run(["cp", dbname1, f"{dbname1}.{tag}"])
                subprocess.run(["cp", better_bibtex, f"{better_bibtex}.{tag}"])
                print(f"{tag} ....  databases copied...")
                print(dbname1)
                print(dbname1)
                print(dbname1)
                print(better_bibtex)
                print(better_bibtex)
                print(better_bibtex)
            else:
                print("... SQLITE not changed ...")
            time.sleep(1)
        else:
            print(f"X... no database {dbname1}")
    else:
        print(f"X... no zotero executable {zname}")

if __name__ == "__main__":
    main()
