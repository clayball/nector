#!/usr/bin/env python2

# Import libraries, set directories, set input file

## Trying to remove this line and the ##sys.path.append line below.
##nector_path = '$HOME/Documents/nector/'

# Add your host and subnet data to the following files.
infile = 'hosts.xml'
infile2 = 'subnets.txt'

# Allow our script to access nector project
import sys
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nector.settings")
##sys.path.append(nector_path)
django.setup()

from hosts.models import Subnet
from hosts.models import Host

# Open files
f = open(infile, 'r')
f2 = open(infile2, 'r')

for line in f:
    # remove cruft from the end of the line
    l = line.rstrip()
    # if the last character in the string is ')'
    if l[-1] == ')':
        lsplit = l.split(' ')
        ipv4 = lsplit[5].strip('()') 
        hostname = lsplit[4].strip()
        h = Host(ipv4_address=ipv4, host_name=hostname)
        h.save()

for line in f2:
    l = line.rstrip()
    temp = l.split("/")
    s = Subnet(ipv4_address=temp[0], prefix=temp[1])
    s.save()

# Close files
f.close()
f2.close()
