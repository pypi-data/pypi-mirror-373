
#!/usr/bin/env python3
"""
watch_ping.py - realtime ping sparklines (blue=reply, red=miss)

Usage: python watch_ping.py google.com 8.8.8.8
"""
import sys
import asyncio
# import argparse
import shutil
import re
from collections import deque
from time import monotonic
import os
import click


PING_RE = re.compile(r"time[=<]\s*([\d.]+)\s*ms", re.I)
SPARK = "▁▂▃▄▅▆▇█"  # 8 levels
BLUE = "\033[94m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
RESET = "\033[0m"
CLEAR = "\033[H\033[J"

# add near constants
INIT = object()



CONFF = os.path.expanduser("~/.ssh/config")

def parse_ssh_config(path=CONFF):
    """
    return list of IP
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf8") as f:
        lines = f.readlines()

    blocks = []
    current = []
    for ln in lines:
        if re.match(r"^\s*Host\s+", ln, flags=re.I):
            if current:
                blocks.append(current)
            current = [ln]
        else:
            if current:
                current.append(ln)
    if current:
        blocks.append(current)

    out = []
    seen = set()
    for block in blocks:
        # Host line may have many names; take first sensible token
        host_line = block[0].strip()
        m = re.match(r"(?i)Host\s+(.+)", host_line)
        if not m:
            continue
        aliases = m.group(1).split()
        alias = next((a for a in aliases if not re.search(r"[*?\[\]]", a)), aliases[0]).strip()

        hostname = None
        for ln in block[1:]:
            m2 = re.match(r"(?i)\s*HostName\s+(.+)", ln)
            if m2:
                hostname = m2.group(1).split()[0].strip().strip('"').strip("'")
                break

        value = hostname if hostname else alias
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


async def ping_once(host, ping_cmd, timeout):
    # spawn ping with single packet; we kill after timeout if needed
    proc = await asyncio.create_subprocess_exec(*ping_cmd, host,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        try:
            await proc.communicate()
        except Exception:
            pass
        return None
    txt = (out + err).decode(errors="ignore")
    m = PING_RE.search(txt)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None

def make_ping_command(is_windows):
    # we only need to send one packet; count flag differs
    if is_windows:
        # Windows: ping -n 1 host
        return ["ping", "-n", "1"]
    else:
        # Unix-like: ping -c 1 host
        return ["ping", "-c", "1"]

def map_to_level(rtt, max_rtt):
    # rtt in ms -> 0..7 index in SPARK
    if rtt is None:
        return None
    r = min(rtt, max_rtt) / max_rtt
    idx = int(r * (len(SPARK) - 1) + 0.5)
    return max(0, min(len(SPARK) - 1, idx))

def render(hosts, history, max_rtt, stats):
    cols = shutil.get_terminal_size().columns

    name_w = max(len(h) for h in hosts) + 2
    spark_w = max(10, cols - name_w - 1)
    out_lines = [CLEAR]
    header = f"watch_ping - {len(hosts)} hosts  max_rtt={max_rtt}ms  "#width={spark_w} "
    out_lines.append(header)
    for h in hosts:
        dq = history[h]
        # ensure correct width
        if len(dq) < spark_w:
            dq.extendleft([None] * (spark_w - len(dq)))
        elif len(dq) > spark_w:
            for _ in range(len(dq) - spark_w):
                dq.popleft()
        line = ""
        if stats[h]['last'] is not None:
            line = GREEN + h.ljust(name_w) + RESET
        else:
            line = RED + h.ljust(name_w) + RESET

        s = []
        # ... and in render(), treat INIT specially
        for val in dq:
            if val is INIT:
                s.append(" ")                     # initial empty = black
            else:
                lvl = map_to_level(val, max_rtt)
                if lvl is None:
                    s.append(RED + "█" + RESET)   # actual timeout = red
                else:
                    s.append(BLUE + SPARK[lvl] + RESET)

        rtt_text = f"{stats[h]['last']:.1f}ms" if stats[h]['last'] is not None else "timeout"
        loss = stats[h]['loss'] * 100.0
        line += "".join(s) + " " + f"{rtt_text} loss={loss:.0f}% "
        out_lines.append(line)
    return "\n".join(out_lines)







async def async_main(hosts, interval, timeout, max_rtt, config):
    # replace with your async logic
    #hosts = args.hosts
    if config:
        hosts = parse_ssh_config()

    if hosts is None or len(hosts) == 0:
        return

    is_windows = sys.platform.startswith("win")
    ping_cmd = make_ping_command(is_windows)
    #timeout = args.timeout
    #interval = args.interval
    #max_rtt = args.max_rtt

    # history per host (deque with newest appended at right)
    history = {h: deque(maxlen=600) for h in hosts}  # MAXIMUM 600 COLUMNS
    stats = {h: {"last": None, "sent": 0, "lost": 0, "loss": 0.0} for h in hosts}


    # populate initial with misses so lines have full width on first render
    cols = shutil.get_terminal_size().columns
    name_w = max(len(h) for h in hosts) + 2
    spark_w = max(10, cols - name_w - 1)
    for h in hosts:
        history[h].extend([INIT] * spark_w)
    #    for h in hosts:
    #        history[h].extend([None] * spark_w)

    try:
        while True:
            t0 = monotonic()
            # ping all hosts in parallel
            tasks = {h: asyncio.create_task(ping_once(h, ping_cmd, timeout)) for h in hosts}
            results = {}
            for h, task in tasks.items():
                try:
                    r = await task
                except Exception:
                    r = None
                results[h] = r
                stats[h]["sent"] += 1
                if r is None:
                    stats[h]["lost"] += 1
                stats[h]["loss"] = stats[h]["lost"] / stats[h]["sent"]
                stats[h]["last"] = r if r is not None else None
                history[h].append(r)
            # render
            print(render(hosts, history, max_rtt, stats), flush=True)
            # sleep until next interval
            dt = interval - (monotonic() - t0)
            if dt > 0:
                await asyncio.sleep(dt)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nExiting.", flush=True)


@click.command()
@click.argument("hosts", nargs=-1, required=False)
@click.option("-i", "--interval", type=float, default=1.0, help="seconds between samples")
@click.option("-t", "--timeout", type=float, default=1.0, help="ping timeout in seconds")
@click.option("-m", "--max-rtt", type=float, default=200.0, help="max RTT (ms) mapped to sparkline")
@click.option("-c", "--config", is_flag=True, default=False, help="read ssh config (switch)")
#async def main(hosts, interval, timeout, max_rtt, config):
#async def main(hosts, interval, timeout, max_rtt, config):
def main(hosts, interval, timeout, max_rtt, config):
    try:
        asyncio.run(async_main(hosts, interval, timeout, max_rtt, config))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
#    p = argparse.ArgumentParser(description="Watch ping as sparklines (blue=reply, red=miss)")
#    p.add_argument("hosts", nargs="+", help="hosts to ping")
#    p.add_argument("-i", "--interval", type=float, default=1.0, help="seconds between samples (default 1.0)")
#    p.add_argument("-t", "--timeout", type=float, default=1.0, help="ping timeout in seconds (default 1.0)")
#    p.add_argument("-m", "--max-rtt", type=float, default=200.0, help="max RTT (ms) mapped to sparkline (default 200ms)")
#    p.add_argument("-c", "--config", is_flag=True, default=False, help="read.ssh config")
#    args = p.parse_args()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
