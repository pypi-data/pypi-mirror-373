# Coded By Microtip
# This Program Coded In Time 2025 - 08 - 24 - 7.33 PM
# Program Name: IP-Finders Github Version █▓
# Descriptions: This Program For Find IP-Address From
#               Sites.
# Basic Module
import os, time, importlib, subprocess
# Auto Installation If User Not Installed Module
modules = ["rich", "requests", "pyfiglet"]
for module in modules:
    try:
        importlib.import_module(module)
    except(ImportError, ModuleNotFoundError):
        os.system("clear")
        print("[0] UPDATE && UPGRADE ENVIRONMENT")
        os.system("apt update && apt upgrade -y")
        print("[@] INSTALLING MATERIALS")
        subprocess.run(["apt", "install", "whois", "python", "python3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pip", "install", "rich", "pyfiglet", "requests"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] SUCCESS INSTALLING MATERIALS")
        time.sleep(1)
        os.system("clear")
# Import Modules
import sys, socket, argparse, requests, pyfiglet
from datetime import datetime
from rich import box
from rich.text import Text
from rich.style import Style
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.console import Console

# Colors-Bold
R = "\033[0m"
T = "\033[1;30m"
M = "\033[1;31m"
H = "\033[1;32m"
K = "\033[1;33m"
B = "\033[1;34m"
G = "\033[1;35m"
C = "\033[1;36m"
P = "\033[1;37m"
O = "\033[1;38;2;255;165;0m"
L = "\033[1;38;2;173;216;230m"

# Hex Colors
AM = "#8e9294"
BT = "#408eb3"
BM = "#42c3ff"
HS = "#12ff8c"
MQ = "#d67a7a"

# For Rich Print
console = Console()

# Waktu Sekarang / Time Now
time_now = datetime.now()

# Result Time When Program Start And Get Result
result_time = f"End In Time: {time_now.strftime('%Y-%m-%d %I:%M:%S %p')}"

# Info Time Starting Operations
def info_time():
    timeinfo = f"[bold {MQ}]• intimes[/bold {MQ}][bold black]:[/bold black] [bold white]{time_now.strftime('%Y-%m-%d %I:%M:%S %p')}[/bold white]"
    console.print(Align.center(timeinfo))

# Setuping Arguments Parse CLI
ikan = argparse.ArgumentParser(description="Simple Tools For Find IP Address Domains")
ikan.add_argument("-s", "--save", help="For Save Result In File Name", metavar="file.txt", nargs="?", const="resdom.txt", default=None )
try:
    args = ikan.parse_args()
except SystemExit:
    print("[?] Argument Wrong")
    sys.exit(1)

# Clean Terminal Screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# Program Icon
def icon():
    icon_figlet = pyfiglet.figlet_format("IPFIND", font="ansi_shadow").rstrip()
    icon_display = Panel.fit(Text(icon_figlet, style="bold yellow"), border_style="bold blue", title="[bold green]IP-FINDERS[/bold green]", subtitle="[bold white on blue][CODED BY MICROTIPS][/bold white on blue]")
    console.print(Align.center(icon_display))

# Program Features
def features():
    # For Print Features
    fprint = lambda n, text: f"[bold blue][[bold white]{n}[/bold white]][/bold blue] [bold white]{text}[/bold white]"
    # Show Features
    feature = Table(show_header=False, box=None)
    feature.add_row(fprint("1", "CHECK DOMAIN NAME IP ADDRESS"))
    feature.add_row(fprint("2", "CHECK IP IN LIST FILE DOMAIN"))
    feature.add_row(fprint("3", "CHECK INFO DOMAIN IP ADDRESS"))
    feature.add_row(fprint("4", "INFO ABOUT AUTHOR THIS TOOLS"))
    feature.add_row(fprint("5", "EXIT FROM THIS PROGRAM/TOOLS"))
    console.print(Align.center(Panel.fit(feature, border_style="bold yellow")))

# Lines
def line():
    width = subprocess.check_output(["tput", "cols"], text=True)
    print(T + "=" * int(width))

# Program Display
def ipfind_display():
    clear()
    icon()
    features()
    line()

# User Select Choices
def program_select():
    ipfind_display()
    user_choice = input(f"{O}[{P}S{O}] {K}SELECT ONE CHOICES{T}: {H}")
    if user_choice == "1":
       check_domain_ip()
    elif user_choice == "2":
       check_domains_ip()
    elif user_choice == "3":
       info_ip_address()
    elif user_choice == "4":
       about_author()
    elif user_choice == "5":
       exit_choice()
    else:
       program_select()

# Feature 1 - Check Domain IP Address
def check_domain_ip():
    domain = input(f"{K}[{P}I{K}] {H}ENTER DOMAIN NAME{T}: {P}")
    if not domain.strip():
       print(f"{L}[{G}E{L}] {K}ENTER DOMAIN NAME OR HOSTNAME")
       sys.exit(0)
    else:
         line()
         output = find_domain_ip(domain.lower())
         line()
         only_info_ending()
         info_time()
         if args.save: # Jika User Ngetik python ipfind.py -s output.txt
            save_result(args.save, output) # Maka Simpan File Sesuai Nama Yang User Ketik

# Feature 2 - Check Domains IP Adress In List File
def check_domains_ip():
    file_name = input(f"{O}[{G}F{O}] {P}ENTER LIST FILE DOMAIN NAME{T}: {H}")
    if not file_name:
         if os.path.exists("domain.txt"):
            line()
            with open("domain.txt", "r") as domfile:
                 domains = domfile.readlines()
                 kaumemangterbaiklahman = []
                 for domain in domains:
                     output = find_domain_ip(domain.strip())
                     kaumemangterbaiklahman.append(output)
                 kaumemangterbaiklahman = "\n\n".join(kaumemangterbaiklahman)
            line()
            info_ending(domains)
            info_time()
            if args.save:
               save_result(args.save, kaumemangterbaiklahman)
         elif not os.path.exists("domain.txt"):
            line()
            with open("domains.txt", "r") as domfile:
                 domains = domfile.readlines()
                 okeman = []
                 for domain in domains:
                     output = find_domain_ip(domain.strip())
                     okeman.append(output)
                 okeman = "\n\n".join(okeman)
            line()
            info_ending(domains)
            info_time()
            if args.save:
               save_result(args.save, okeman)
    else:
         line()
         with open(file_name, "r") as domfile:
              domains = domfile.readlines()
              okeman = []
              for domain in domains:
                  output = find_domain_ip(domain.strip())
                  okeman.append(output)
              okeman = "\n\n".join(okeman)
         line()
         info_ending(domains)
         info_time()
         if args.save:
            save_result(args.save, okeman)

# Feature 3 - Check Info Domain IP Address
def info_ip_address():
    ip = input(f"{O}[{H}P{O}] {K}ENTER IP ADDRRESS DOMAIN{T}: {P}")
    line()
    if not ip.strip():
       print(f"{P}[{B}!{P}] {L}ENTER IP ADDRESS DOMAIN FOR INFO")
       sys.exit()
    else:
       wprint = lambda key, value: print(f"{K}[{P}+{K}] {P}{key} {T}: {H}{value}")
       info_ip = subprocess.check_output(["whois", f"{ip}"], text=True)
       do = []
       output = {}
       do.append(f"[@] IP Address : {ip}")
       for info in info_ip.splitlines():
           if ":" in info:
              fish, red = info.split(":", 1)
              if not red.strip():
                 red = "None"
              output[fish.strip()] = red.strip()
       for sockfish, deadtime in output.items():
           wprint(sockfish, deadtime)
           do.append(f"[+] {sockfish} : {deadtime}")
       do.append(f"[T] Time: {time_now.strftime('%Y-%m-%d %I:%M:%S %p')}")
       line()
       info_time()
       do = "\n".join(do)
       if args.save:
          save_result(args.save, do)

# Feature 4 - About Author This Tools
def about_author():
    clear()
    if os.path.exists(".sigmacat.txt"):
       os.system("cat .sigmacat.txt")
    else:
         try:
             print(f"{O}[{P}P{O}] {K}DOWNLOADING FILES{T}: {H}..........")
             download = requests.get("https://0x0.st/KHWv.txt")
             with open(".sigmacat.txt", "wb") as sigma:
                  sigma.write(download.content)
             clear()
             os.system("cat .sigmacat.txt")
         except requests.exceptions.ConnectionError:
             print(f"{P}[^] FILE NOT FOUND BECAUSE YOUR OFFLINE")
    aprint = lambda title, info: f"[bold blue][[bold gold1]+[/bold gold1]][/bold blue] [bold green]{title}[/bold green] [bold black]:[/bold black] [bold white]{info}[/bold white]"
    info_author = f"""{aprint('Author Name', 'Microtip')}
{aprint('Author Descript', '[bold yellow]++++++[>++++++++++<-]>+++++.+++++++++++.+++.-.\n>++++++[>++++++++++<-]>+++++++++.\n>++++++++++.[/bold yellow]')}
{aprint('Author Status', '[underline]not found[/underline]')}
{aprint('Author Age', '[underline]not found[/underline]')}
{aprint('Author Respon', '[bold red]Hello, World![/bold red]')}
{aprint('Author Github', '[italic underline bold blue]https://github.com/W-HAT909[/italic underline bold blue]')}"""
    console.print(Align.center(Panel.fit(info_author, border_style="bold magenta", title="[bold orange1]IP-FINDERS[/bold orange1]")))
    print()
    back = input("[@] Back To Main? [Y/n] > ")
    if not back.strip():
       main()
    elif back.lower() == "y":
       main()
    else:
       exit_choice()

# Feature 5 - Exit Feature
def exit_choice():
    print(f"{H}[{G}√{H}] {P}EXITED FROM PROGRAM.")
    sys.exit()

# Main Feature - Find IP Address Domain
def find_domain_ip(domain):
    output = [] # For Placet Saved Output In Here
    result = [] # For Place Output In Here
    output.append(f"Domain Name: {domain}") # Output Saved Domain
    result.append("[bold white][[bold green]SUCC[/bold green]] DOMAIN IP ADDRESS FOUND[/bold white]")
    result.append(f"[bold white][[bold orange1]DOMN[/bold orange1]][/bold white] [bold yellow]RESULT [bold {BM}]{domain}[/bold {BM}] IP ADDRESS[/bold yellow][bold black]:[/bold black]")
    # Find IPv4 Domain
    output.append("IPv4 Domain Address:") # Output Saved IPv4 Domain Info
    result.append("[bold white][[bold blue]IPv4[/bold blue]][/bold white] [bold green]RESULT FROM [bold white][[bold blue]IPv4[/bold blue]][/bold white] ADDRESS[/bold green][bold black]:[/bold black]")
    IPv4 = socket.gethostbyname_ex(domain)
    for ip_address in IPv4[2]:
        result.append(" " * 7 + f"[bold green]-[/bold green] [bold white]{ip_address}[/bold white]")
        output.append(f"- {ip_address}") # Output Saved IPv4 Address
    # Find IPv6 Domain
    output.append("IPv6 Domain Address:") # Output Saved IPv6 Domain Info
    result.append("[bold white][[bold yellow]IPv6[/bold yellow]] [bold green]RESULT FROM[/bold green] [[bold yellow]IPv6[/bold yellow]][/bold white] [bold green]ADDRESS[/bold green][bold black]:[/bold black]")
    SIPv6 = set() # For Not Duplicate IPv6
    IPv6 = socket.getaddrinfo(domain, None, socket.AF_INET6)
    for ip_address in IPv6:
        SIPv6.add(ip_address[4][0])
    for ip_address in SIPv6:
        result.append(" " * 7 + f"[bold green]-[/bold green] [bold white]{ip_address}[/bold white]")
        output.append(f"- {ip_address}") # Output Saved IPv6 Address
    output.append(result_time)
    # Combine Results
    result = "\n".join(result)
    # Combine Saved Output
    output = "\n".join(output)
    # Print Results
    console.print(Align.center(Panel.fit(result, border_style=f"bold medium_purple1", title=f"[bold orange1][[bold {HS}]IP-FINDERS[/bold {HS}]][/bold orange1]")))
    return output

# End Info Only
def only_info_ending():
    end_info = f"[bold yellow]• total domain[/bold yellow][bold black]:[/bold black] [bold white]1 [/bold white] [bold magenta]• status[/bold magenta][bold black]:[/bold black] [bold green]success[/bold green] [bold orange1]• program[/bold orange1][bold black]:[/bold black] [bold {BM}]ended[/bold {BM}]"
    console.print(Align.center(end_info))

# End Info
def info_ending(domains):
    total_sites = len(domains)
    end_info = f"[bold yellow]• total domain[/bold yellow][bold black]:[/bold black] [bold white]{total_sites}[/bold white] [bold magenta]• status[/bold magenta][bold black]:[/bold black] [bold green]success[/bold green] [bold orange1]• program[/bold orange1][bold black]:[/bold black] [bold {BM}]ended[/bold {BM}]"
    console.print(Align.center(end_info))

# Saved Output To File
def save_result(filename, output):
    with open(filename, "a") as resdom:
         resdom.write(output)
         resdom.write("\n\n")
    # For Print Info File Saved
    kucing_makan_besi = f"[bold medium_purple1]• result[/bold medium_purple1][bold black]:[/bold black] [bold {HS}]file saved in [bold white]{filename}[/bold white][/bold {HS}]"
    console.print(Align.center(kucing_makan_besi))
    # For Print Info Saved File
    garap = "[bold blue]• info[/bold blue][bold black]:[/bold black] [bold gold1]saved file not replace result, but add[/bold gold1]\n"
    console.print(Align.center(garap))

# Main Program
def main():
    # For Print Exceptions
    eprint = lambda s, text: print(f"{L}[{G}{s}{L}] {K}{text}")
    try:
        program_select()
    except KeyboardInterrupt:
        eprint("C", "PROGRAM CANCELED.")
        sys.exit(0)
    except EOFError:
        print()
        eprint("D", "EXITED FROM THIS PROGRAM")
        sys.exit(0)
    except socket.gaierror:
        eprint("E", "ERROR WITH HOSTNAME OR CONNECTIONS")
        sys.exit(0)
    except socket.herror:
        eprint("W", "NONE DOMAIN NAME YOUR TYPE, ENTER DOMAIN NAME")
    except FileNotFoundError:
        eprint("F", f"FILE NOT FOUND, MAKE LIST DOMAIN {G}FILE {P}domain.txt")
        sys.exit(0)
    except subprocess.CalledProcessError:
        eprint("S", f"WHAT YOUR TYPE? IT'S NOT WORK")
        sys.exit(0)

# Run Main Program
if __name__ == "__main__":
    main()

# Enjoy It ~# -
# 𝙒𝙀 𝘼𝙍𝙀 𝘼𝙉𝙊𝙉𝙔𝙈𝙊𝙐𝙎, 𝙀𝙓𝙋𝙀𝘾𝙏 𝙐𝙎.
