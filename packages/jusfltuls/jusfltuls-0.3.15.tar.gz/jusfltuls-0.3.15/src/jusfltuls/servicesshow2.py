#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import getpass

import click
import pandas as pd

import re
from console import fg, bg

_ANSIRE = re.compile(r'\x1b\[[0-9;]*m')

ESC = "\033["
RESET = ESC + "0m"
GREEN = ESC + "32m"
RED = ESC + "31m"
YELLOW = ESC + "33m"
WHITE = ESC + "37m"

"""
make this in
 sudo visudo -f /etc/sudoers.d/ufw-status
youruser ALL=(root) NOPASSWD: /usr/sbin/ufw status, /usr/sbin/ufw status verbose
"""

def strip_ansi(s):
    return _ANSIRE.sub('', s)

def pad_ansi(s, width, left=True):
    vis = strip_ansi(s)
    pad = max(0, width - len(vis))
    return (s + ' ' * pad) if left else (' ' * pad + s)

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return p.stdout


def original_user():
    try:
        out = run(["logname"]).strip()
        if out:
            return out
    except Exception:
        pass
    # fallback
    return os.environ.get("SUDO_USER") or getpass.getuser()


def parse_ufw():
    """Return dict port->rule_str and list of allowed numeric ports (unique, sorted)."""
    txt = run(["sudo", "ufw", "status"])
    rules = {}
    allowed = set()
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        # skip lines that start with an IP (like "Anywhere  ALLOW IN  1.2.3.4")
        if re.match(r"^[0-9]+\.", line):
            continue
        parts = re.split(r"\s+", line)
        first = parts[0]
        # normalize first column removing /tcp /udp
        first_norm = re.sub(r"/(tcp|udp)$", "", first)
        if re.match(r"^\d+$", first_norm):
            rule_str = " ".join(parts[:4]) if len(parts) >= 4 else " ".join(parts)
            rules[first_norm] = rule_str
            if "DENY" not in rule_str and "DENY" not in line:
                allowed.add(int(first_norm))
    allowed_list = sorted(allowed)
    if len(rules) == 0 or len(allowed_list) == 0:
        # print(rules, allowed_list)
        print(f"X... {bg.red}{fg.white} UFW - SOME PROBLEM with FIREWALL {fg.default}{bg.default}")
    return rules, allowed_list


def check_ufw_for_port(rules, port):
    port_s = str(port)
    return rules.get(port_s, "")


def systemctl_status(svc):
    # append .service (systemctl handles either)
    unit = f"{svc}.service"
    out = run(["systemctl", "is-active", unit]).strip()
    return out or "unknown"


def show_warning_if_policy_not_deny():
    txt = run(["ufw", "status", "verbose"])
    if "Default: deny (incoming)" not in txt:
        click.echo("X... check default policies of ufw !!!")
        click.echo(txt)


def ps_contains(pattern):
    txt = run(["ps", "-ef"])
    return pattern in txt


def ss_listening_contains(port, name_substr=None):
    txt = run(["ss", "-tulpn"])
    if str(port) not in txt:
        return False
    if name_substr:
        return name_substr in txt
    return True


# ================================================================================
#
#                MAIN --------------------------
#
# --------------------------------------------------------------------------------
@click.command()
@click.option("-n", "--no-decoration", is_flag=True, help="Do not print headers / separators")
def main(no_decoration):
    user = run(["whoami"]).strip()
    orig_user = original_user()

    services = [
        ("ufw", 0),
        ("psad", 0),
        ("ssh", 22),
        ("influxdb", 8086),
        ("chrony", 323),
        ("ntp", 123),
        ("mosquitto", 1883),
        (f"syncthing@{orig_user}", 22000),
        ("grafana-server", 3000),
        ("smbd", 445),
        ("elog", 9000),
        ("nginx", 80),
        ("ntfy", 80),
    ]

    rules, open_ports = parse_ufw()
    open_ports_left = list(open_ports)  # numeric list

    rows = []
    if not no_decoration:
        click.echo("  sysd-service       status            port        UFW-opened")
        click.echo("_______________________________________________________________")

    for svc, port in services:
        status = systemctl_status(svc)
        if status == "active":
            color = GREEN
        elif status == "inactive":
            color = WHITE
        else:
            color = RED
        ufw_status = ""
        ufw_color = GREEN
        if port != 0:
            ufw_status = check_ufw_for_port(rules, port)
            if "DENY" in ufw_status:
                ufw_color = RED
            # remove from open_ports_left if present
            if port in open_ports_left:
                open_ports_left = [p for p in open_ports_left if p != port]
        rows.append(
            {
                "service": svc,
                "status": f"{color}{status}{RESET}",
                "port": "" if port == 0 else str(port),
                "ufw": f"{ufw_color}{ufw_status}{RESET}" if ufw_status else "",
            }
        )

    # keep table in pandas
    df = pd.DataFrame(rows, columns=["service", "status", "port", "ufw"])

    # # print using our format to keep colors
    # for _, r in df.iterrows():
    #     svc = r["service"]
    #     status_colored = r["status"]
    #     port = r["port"]
    #     ufw = r["ufw"]
    #     if port:
    #         click.echo(f"  {svc:<20} {status_colored:<8}     Port {port:>5}   {ufw}")
    #     else:
    #         click.echo(f"  {svc:<20} {status_colored:<8}                  {ufw}")

    # printing loop (replace your current loop)
    for _, r in df.iterrows():
        svc = r["service"]
        status_colored = r["status"]
        port = r["port"]
        ufw = r["ufw"]

        svc_field = f"  {svc:<20}"
        status_field = pad_ansi(status_colored, 8)   # visible width 8
        if port:
            click.echo(f"{svc_field} {status_field}     Port {port:>5}   {ufw}")
        else:
            click.echo(f"{svc_field} {status_field}                  {ufw}")

    # TELEGRAF and VADIM checks (as in original)
    tlgf_active = False
    ps_txt = run(["ps", "-ef"])
    if f"{orig_user}.conf" in ps_txt and "telegraf" in ps_txt:
        tlgf_active = True
    vadi_active = ss_listening_contains(8200, "telegraf")

    tlgf_str = f"{GREEN}active{RESET}" if tlgf_active else f"{WHITE}inactive{RESET}"
    vadi_str = f"{GREEN}active{RESET}" if vadi_active else f"{WHITE}inactive{RESET}"

    click.echo(f" TELEGRAF@{orig_user}         {tlgf_str}")
    click.echo(f" VADIM-8200-{orig_user}       {vadi_str}")

    if not no_decoration:
        click.echo("_______________________________________________________________")

    if os.geteuid() == 0:
        click.echo("", nl=False)
        click.echo(f"{YELLOW}: {open_ports_left} {RESET}")
        show_warning_if_policy_not_deny()


if __name__ == "__main__":
    main()
