#!/usr/bin/env python2

'''
Purpose
=======

Uses provided Subnets, Hosts, Vulnerabilities, Events data to populate the
Nector database.


Prerequisites
=============

hosts.xml, subnets.txt, vulnlist.csv, and events.csv must exist in the current
directory, contain desired information, and be formatted properly.

Sample data files stored in sample-data/
- sample_hosts.xml
- sample_subnets.txt
- sample-vulnlist.csv
- sample-events.csv


Postconditions
==============

The database will be populated with Hosts, Subnets, Vulnerabilities, and Events
specified in hosts.xml, subnets.txt, vulnlist.csv, and events.csv.
'''

# Import necessary libraries.
import sys
import os
import django
from optparse import OptionParser # Used for getting args
import csv # Used for parsing vulnlist.csv, events.csv, & censys-keys.csv
from django.db import transaction # Used in optimization of runtime.
from django.db import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nector.settings")
django.setup()

# Import Django models.
from hosts.models import Subnet
from hosts.models import Host
from vulnerabilities.models import Vulnerability
from events.models import Event

# Get names of files containing Host, Subnet, Vulnerability, Events, & censys
# data that we want to import.
host_file_name = 'hosts.xml'
subnet_file_name = 'subnets.txt'
vulnerability_file_name = 'vulnlist.csv'
events_file_name = 'events.csv'

# Open files
host_file = open(host_file_name, 'r')
subnet_file = open(subnet_file_name, 'r')
vulnerability_file = open(vulnerability_file_name, 'r')
vulnerability_csv = csv.reader(vulnerability_file)
events_file = open(events_file_name, 'r')
events_csv = csv.reader(events_file)

# Get & Set Options / Args
parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="Print error/success messages. Useful in debugging.")
(options, args) = parser.parse_args()
verbose = options.verbose


# Adds Hosts to db.sqlite3
def populate_hosts():
    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        for line in host_file:
            # Remove cruft from the end of the line:
            l = line.rstrip()
            # If host has a hostname:
            if l[-1] == ')':
                lsplit = l.split(' ')
                ipv4 = lsplit[5].strip('()')
                hostname = lsplit[4].strip()
                h = Host(ipv4_address=ipv4, host_name=hostname, status="Online")
                # Save Host to db (won't actually happen until
                #  'with transaction.atomic()' is completed):
                try:
                    h.save()
                except:
                    # Duplicate entry, so do nothing.
                    if verbose:
                        print 'Unique Error: Duplicate host ' + ipv4 + ', ' \
                        + hostname
                    else:
                        pass
            elif l[0] != '#':
                # Host has no hostname, therefore it's down.
                # '#' indicates last line of Nmap scan.
                ipv4 = l.split(' ')[4]
                h = Host(ipv4_address=ipv4, status="Offline")
                try:
                    h.save()
                except:
                    # Duplicate entry, so do nothing.
                    if verbose:
                        print 'Unique Error: Duplicate host ' + ipv4 \
                        + ', Offline'
                    else:
                        pass
    if verbose:
        print '\nHosts: Done!\n====================\n'


# Adds Subnets to db.sqlite3
def populate_subnets():
    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        for line in subnet_file:
            l = line.rstrip()
            temp = l.split("/")
            s = Subnet(ipv4_address=temp[0], prefix=temp[1])
            # Save Subnet to db (won't actually happen until
            #  'with transaction.atomic()' is completed):
            try:
                s.save()
            except:
                # Duplicate entry, so do nothing.
                if verbose:
                    print 'Unique Error: Duplicate subnet ' + temp[0] \
                    + '/' + temp[1]
                else:
                    pass
    if verbose:
        print '\nSubnets: Done!\n====================\n'


# Adds Vulnerabilities to db.sqlite3
def populate_vulnerabilities():
    next(vulnerability_csv) # Skip first entry of the csv file, a header.
    for row in vulnerability_csv:
        v = Vulnerability(plugin_and_host=row[0]+row[4], plugin_id=row[0],
                plugin_name=row[1], severity=row[2], ipv4_address=row[3],
                host_name=row[4])
        # Save Vulnerability to db (won't actually happen until
        #  'with transaction.atomic()' is completed):
        try:
            with transaction.atomic():
                v.save()
        except IntegrityError as e:
            # Duplicate entry, so do nothing.
            if verbose:
                print 'Unique Error: Duplicate vulnerability ' + row[0] \
                + ', ' + row[3]
            else:
                pass
    if verbose:
        print '\nVulnerabilities: Done!\n====================\n'


# Adds Events to db.sqlite3
def populate_events():
    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        next(events_csv) # Skip first entry of the csv file, a header.
        for row in events_csv:
            e = Event(request_number=row[0], date_submitted=row[1],
                    title=row[2], status=row[3], date_last_edited=row[4],
                    submitters=row[5], assignees=row[6].split(":")[0])
            # We only want to save Closed events
            if e.status == "Closed":
                # Save Event to db (won't actually happen until
                #  'with transaction.atomic()' is completed):
                try:
                    e.save()
                except:
                    # Duplicate entry, so do nothing.
                    if verbose:
                        print 'Unique Error: Duplicate event ' + row[0]
                    else:
                        pass
    if verbose:
        print '\nEvents: Done!\n====================\n'


# Call funcitons.
populate_hosts()
populate_subnets()
populate_vulnerabilities()
populate_events()

# Close files.
host_file.close()
subnet_file.close()
vulnerability_file.close()
events_file.close()
