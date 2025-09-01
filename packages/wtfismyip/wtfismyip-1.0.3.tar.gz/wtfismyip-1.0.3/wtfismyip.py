#!/usr/bin/env python3

import sys

import requests as requests
from rich.console import Console


def main():
    console = Console()
    console.print("What the fuck is my IP", style="bold white on blue", justify="center")

    with console.status("[bold blue]Getting..."):
        default_request = requests.get("https://wtfismyip.com/json")
        if default_request.status_code != 200:
            console.print(f"bad status {default_request.status_code}", style="bold red")
            sys.exit(1)
        ipv4_request = requests.get("https://ipv4.wtfismyip.com/json")
        if ipv4_request.status_code != 200:
            console.print(f"bad status {ipv4_request.status_code}", style="bold red")
            sys.exit(1)

    console.print("Your fucking IP address: ", style="green", end="")
    console.print(default_request.json().get("YourFuckingIPAddress"), style="yellow")

    if default_request.json().get("YourFuckingIPAddress") != ipv4_request.json().get("YourFuckingIPAddress"):
        console.print("Your fucking IPv4 address: ", style="green", end="")
        console.print(ipv4_request.json().get("YourFuckingIPAddress"), style="yellow")

    console.print("Your fucking location: ", style="green", end="")
    console.print(default_request.json().get("YourFuckingLocation"), style="yellow")
    console.print("Your fucking ISP: ", style="green", end="")
    console.print(default_request.json().get("YourFuckingISP"), style="yellow")

    if default_request.json().get("YourFuckingTorExit"):
        console.print("You are using Tor", style="red", )
    console.print("--------", style="bold white on blue", justify="center")
    console.print("powered by https://wtfismyip.com/", style="bold white", justify="right")


if __name__ == '__main__':
    main()
