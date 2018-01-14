# VietnamFlashbacks #

Real-time NTLMv2 bruteforcer. Designed to accompany **lgandx's Responder/MultiRelay**.

## What it's for ##

Sometimes Responder/MultiRelay fails to start a session for you, however it still collects hashes into it's *logs* directory. This tool automatically catches every new NTLMv2 hash in the *logs* directory and passes it to hashcat in order to crack it in real-time. 

## Demo ##

[You can see demo here](https://youtu.be/6UV8H_lWzE0). Video is recorded on the Kali Linux box (IP 10.10.1.99) with Responder/MultiRelay started along with VietnamFlashbacks. Soon after that, domain user (User) on a Win7 machine (IP 10.10.1.11) tries to open a network share with nonsense name for the sake of demo. Responder\MutliRelay catches the hash and writes it down to a text file, VietnamFlashbacks spawns hashcat process in order to crack it and succeeds (obviously). Same with Administrator account on Win2012 machine (IP 10.10.1.1).

## Usage ##

There is only one mandatory option, which is --responder. Without --dictionary set program will only log hashes without cracking:
- ```-r or --responder is a path to Responder root directory (i.e. /root/git/responder)```
- ```-d or --dictionary is a path to dictionary file of your choice (i.e. /root/dict/passwords.txt)```
