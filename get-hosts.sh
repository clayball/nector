#!/bin/bash

# get-hosts.sh by Brian Jopling, 2017
# ----------------------------------
# Reads from subnets.txt and runs two nmap scans.
# First nmap scan gets a list of hosts on the subnets.
# Second nmap scan gets a list of the open ports and their hosts.
# Creates two files: hosts.xml and openports.xml

rm hosts.xml >/dev/null         # Remove the file if it exists. (Easy way to clear the results)
touch hosts.xml >/dev/null      # Create the file if it doesn't exist.

rm openports.xml >/dev/null     # Remove the file if it exists. (Easy way to clear results)
touch openports.xml >/dev/null  # Create the file if it doesn't exist.

echo '[*] Scanning subnets for existing hosts...'
# Run nmap scan on all subnets to generate list of hosts.
# Export to hosts.xml
$(nmap -sL -iL subnets.txt -oN hosts.xml)
echo '[!] Populated file: hosts.xml'

echo '[*] Scanning subnet(s) for hosts with open ports...'
# Run nmap scan on all subnets to generate list of open ports and their hosts.
# Export to openports.xml
$(nmap -Pn -sV --version-light -vv -T5 -p17,19,21,22,23,25,53,80,123,137,139,153,161,443,445,548,636,1194,1337,1900,3306,3389,4380,4444,4672,5353,5900,6000,6881,8000,8080,9050,31337 -iL subnets.txt --open -oX openports.xml 2>&1 > /dev/null)
echo '[!] Populated file: openports.xml'

echo ''
echo '[!] Complete. See files: hosts.xml, openports.xml';
