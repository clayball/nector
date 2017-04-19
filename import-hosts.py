#!/usr/bin/env python2

# import-hosts.py
# Purpose: Uses provided Subnets, Hosts, and Vulnerabilities to populate a database which is queried throughout NECTOR.
# Preconditions: hosts.xml, subnets.txt, and vulnlist.csv must exist in the current directory, contain desired information, and be formatted properly (see sample_hosts.xml, sample_subnets.txt, and sample-vulnlist.csv).
# Postconditions: db.sqlite3 will be populated with Hosts, Subnets, and Vulnerabilities specified in hosts.xml, subnets.txt, and vulnlist.csv.


# Import necessary libraries.
import sys
import os
import django
import csv # Used for parsing vulnlist.csv
from django.db import transaction # Used in optimization of runtime.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nector.settings")
django.setup()

# Import Django models.
from hosts.models import Subnet
from hosts.models import Host
from vulnerabilities.models import Vulnerability

# Get names of files containing Host, Subnet, and Vulnerability data that we want to import.
host_file_name = 'hosts.xml'
subnet_file_name = 'subnets.txt'
vulnerability_file_name = 'vulnlist.csv'

# Open files
host_file = open(host_file_name, 'r')
subnet_file = open(subnet_file_name, 'r')
vulnerability_file = open(vulnerability_file_name, 'r')
vulnerability_csv = csv.reader(vulnerability_file)

# Adds Hosts to db.sqlite3
def populate_hosts():
    # Only allow changes to be made to db after nested blocks have been complete:
    with transaction.atomic():
        for line in host_file:
            # Remove cruft from the end of the line:
            l = line.rstrip()
            # If the last character in the string is ')':
            if l[-1] == ')':
                lsplit = l.split(' ')
                ipv4 = lsplit[5].strip('()')
                hostname = lsplit[4].strip()
                h = Host(ipv4_address=ipv4, host_name=hostname)
                # Save Host to db (won't actually happen until 'with transaction.atomic()' is completed):
                h.save()

# Adds Subnets to db.sqlite3
def populate_subnets():
    # Only allow changes to be made to db after nested blocks have been complete:
    with transaction.atomic():
        for line in subnet_file:
            l = line.rstrip()
            temp = l.split("/")
            s = Subnet(ipv4_address=temp[0], prefix=temp[1])
            # Save Subnet to db (won't actually happen until 'with transaction.atomic()' is completed):
            s.save()

# Adds Vulnerabilities to db.sqlite3
def populate_vulnerabilities():
    # Only allow changes to be made to db after nested blocks have been complete:
    with transaction.atomic():
        next(vulnerability_csv) # Skips the first entry of the csv file, which is just a header.
        for row in vulnerability_csv:
            v = Vulnerability(plugin_id=row[0], plugin_name=row[1], severity=row[2], ipv4_address=row[3], host_name=row[4])
            # Save Vulnerability to db (won't actually happen until 'with transaction.atomic()' is completed):
            v.save()

# Call funcitons.
populate_hosts()
populate_subnets()
populate_vulnerabilities()

# Close files.
host_file.close()
subnet_file.close()
vulnerability_file.close()
