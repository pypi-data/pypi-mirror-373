#!/usr/bin/env python3
from wifi import Cell, Scheme
from fire import Fire
import subprocess
import re
import jusfltuls.verif_apt as verif_apt

interface = 'wlan0'  # Replace with your wireless interface


def get_wifi_interfaces():
    """
    ubuntu 24 on pc has nmcli
    """
    result = subprocess.run(['nmcli', 'device', 'status'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    wifi_interfaces = [line.split()[0] for line in output.splitlines() if line.lower().find("w") == 0]
    return wifi_interfaces


def parse_iwlist_output(interface):
    """
    """
    result = subprocess.run(['sudo', 'iwlist', interface, 'scan'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"X...  error returned for iwlist on interface {interface}")
        return []
    output = result.stdout

    cells = re.split(r'Cell \d+ - Address:', output)
    networks = []

    for cell in cells[1:]:
        ssid_match = re.search(r'ESSID:"([^"]+)"', cell)
        signal_match = re.search(r'Signal level=(-?\d+)', cell)
        channel_match = re.search(r'Channel:(\d+)', cell)

        ssid = ssid_match.group(1) if ssid_match else 'N/A'
        signal = signal_match.group(1) if signal_match else 'N/A'
        channel = channel_match.group(1) if channel_match else 'N/A'

        networks.append({'SSID': ssid, 'Signal': signal, 'Channel': channel})

    return networks



def main():
    """
    interface is set to wlan0 ....
    """
    global interface

    verif_apt.main()

    ifaces = get_wifi_interfaces()
    if len(ifaces) > 1:
        print("i... taking first wifi interface", ifaces)
        interface = ifaces[0]
    elif len(ifaces) > 0:
        print("i... taking the   wifi interface", ifaces)
        interface = ifaces[0]
    else:
        print("X... NO wifi interfaces")
        return

    networks = parse_iwlist_output(interface)

    if len(networks) == 0:
        return

    #networks = Cell.all('wlan0')  # Replace 'wlan0' with your interface
    for network in networks:
        print(f"SSID: {network['SSID']}, Signal: {network['Signal']}, Channel: {network['Channel']}")


    networks2 = Cell.all(interface)  # Replace 'wlan0' with your wireless interface name
    for network in networks2:
        print(f"SSID: {network.ssid}, Signal: {network.signal}, Channel: {network.channel}")

if __name__ == "__main__":
    main()
