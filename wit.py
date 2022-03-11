#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import socket
import struct


class Color:
    END = "\33[0m"
    BOLD = "\033[1m"
    YELLOW = "\33[33m"
    RED = "\033[91m"


ascii_art = (
    "         x0XNWWWWNXKO.        \n"
    "    ,OKNWMMMMMMMMMMMMMWX0x    \n"
    " .0NMMMM:             MMMMWKl \n"
    "kWMMX     xO00KKK0Ok.    :MMMN\n"
    "      :0XWMMMMMMMMMMMNKO      \n"
    "    'XMMMX          cMMMWx    \n"
    "      X.   ;O0KK0Ok    K'     \n"
    "         0NMMMMMMMMWK.        \n"
    "          kX      cM          \n"
    "             k00O,            \n"
    "           ,WMMMMMk           \n"
    "           ;MMMMMM0           \n"
    "             OMMM.            \n"
)


def get_interface() -> str | None:
    with open("/proc/net/route", "r") as f:
        for line in f:
            fields = line.split()
            if fields[2] != "00000000" and fields[2] != "Gateway":
                return fields[0]
        return None


def get_level(iface: str) -> int | None:
    with open("/proc/net/wireless", "r") as f:
        for line in f:
            fields = line.split()
            if fields[0] == f"{iface}:":
                return fields[3].removesuffix(".")
        return None


def get_gateway() -> str | None:
    with open("/proc/net/route", "r") as f:
        for line in f:
            gateway = line.split()[2]
            if len(gateway) == 8 and gateway != "00000000":
                return socket.inet_ntoa(struct.pack("<L", int(gateway, 16)))
        return None


def get_private_ip(server: str) -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((server, 80))
            ip = s.getsockname()[0]
            return ip
    except (socket.gaierror, TypeError):
        return None


def get_public_ip(server: str) -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server, 80))
            s.send(f"GET / HTTP/1.1\r\nHost:{server}\r\n\r\n".encode())
            r = s.recv(1024)
            ip = r.split()[-1].decode()
            return ip
    except socket.gaierror:
        return None


def get_mac_address(iface: str) -> str | None:
    try:
        with open(f"/sys/class/net/{iface}/address") as f:
            mac = f.read().removesuffix("\n")
            return mac
    except FileNotFoundError:
        return None


def main() -> None:
    iface = get_interface()
    lvl = get_level(iface)
    gateway = get_gateway()
    private_ip = get_private_ip(gateway)
    public_ip = get_public_ip("ifconfig.me")
    mac = get_mac_address(iface)

    data = (
        f"{Color.BOLD}[•] Interface:\t\t{Color.YELLOW}{iface}{Color.END}\n"
        f"{Color.BOLD}[•] Signal level:\t{Color.YELLOW}{lvl}{Color.END}\n"
        f"{Color.BOLD}[•] Gateway:\t\t{Color.YELLOW}{gateway}{Color.END}\n"
        f"{Color.BOLD}[•] Private ip:\t\t{Color.YELLOW}{private_ip}{Color.END}\n"
        f"{Color.BOLD}[•] Public ip:\t\t{Color.YELLOW}{public_ip}{Color.END}\n"
        f"{Color.BOLD}[•] Mac address:\t{Color.YELLOW}{mac}{Color.END}\n"
    )

    print(f"{Color.BOLD}{ascii_art}{Color.END}\n{data}")


if __name__ == "__main__":
    try:
        if platform.system() == "Linux":
            main()
        else:
            print(f"{Color.RED}[•] Operating system not supported.{Color.END}")
    except (KeyboardInterrupt, EOFError):
        os.system("clear")
        print("[•] Exiting...")
        exit(0)
