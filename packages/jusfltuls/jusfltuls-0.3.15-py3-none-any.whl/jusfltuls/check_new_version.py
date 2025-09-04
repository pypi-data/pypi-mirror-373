#!/usr/bin/env python3

# check new version on PyPI
#
#
from console import fg, bg
import requests
#from jusfltuls.version import __version__

from importlib.metadata import version
##### print(version("jusfltuls"))

def is_there_new_version(package=None, printit=True, printall=True):
    """Check the latest version of a package on PyPI."""
    if package is None:
        return
    url = f"https://pypi.org/pypi/{package}/json"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['info']['version']
            if printall:
                print(f"{fg.darkslategray}Latest version of {package} on PyPI: {latest_version}{fg.default}")
            if version("jusfltuls") != latest_version:
                if printit:
                    print(f"{fg.green}NEW VERSION AVAILABLE: {latest_version} {fg.default}, current=={version("jusfltuls")}")
                return True
            else:
                return False
        else:
            if printit:
                print(f"Package {package} not found on PyPI.")
            return False
    except:
        pass
    return None
