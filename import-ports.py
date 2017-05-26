#!/usr/bin/env python2

'''
Purpose
=======

Imports scans of hosts with their corresponding open ports into database.

Prerequisites
=============

Directory called 'port-scans' exists, containing scans of open ports.
Scan files must follow this csv format:

host,port,state,info
"127.0.0.1","22","open","OpenSSH 7.3 protocol2.0"

(See sample files ./port-scans)

Postconditions
==============

db.sqlite3 will update Hosts with respective port info.
'''

# Import necessary libraries.
import sys
import os
import django
from optparse import OptionParser # Used for getting args
import csv # Used for parsing vulnlist.csv, events.csv, & censys-keys.csv
import json
from django.db import transaction # Used in optimization of runtime.
from django.db import IntegrityError # Used in checking for duplicates.
from django.shortcuts import render, get_object_or_404
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nector.settings")
django.setup()

# Import Django models.
from hosts.models import Host

# Directory containing scans.
# We'll be importing every scan in dir.
scans_dir_name = './port-scans/'

# Get & Set Options / Args
parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="Print error/success messages. Useful in debugging.")
(options, args) = parser.parse_args()
verbose = options.verbose

# Adds ports to Hosts in db.sqlite3
def import_ports():
    HEADER = 'host'
    for scan in os.listdir(scans_dir_name):
        # Allow changes to be made to db after nested blocks have been
        # completed. (aka whenever we finish reading a file.)
        with transaction.atomic():
            port = ''
            print '-> Importing %s' % scan
            with open(scans_dir_name + '/' + scan) as csvfile:
                scan_file = csv.reader(csvfile)
                for row in scan_file:
                    if row[0] == HEADER:
                        next(scan_file)
                    else:
                        ip = row[0]
                        port = row[1]
                        status = row[2]
                        proto = row[3]
                        try:
                            host = get_object_or_404(Host, ipv4_address=ip)
                            dict_ports = "{\"%s\" : [\"%s\", \"%s\"]}" % (port, status, proto)
                            if not host.ports:
                                host.ports = dict_ports
                            else:
                                host_json = json.loads(host.ports)
                                host_json[port] = [status, proto]
                                host.ports = json.dumps(host_json)
                                if verbose:
                                    print host.ports
                            # Save Host to db (won't actually happen until
                            #  'with transaction.atomic()' is completed):
                            try:
                                host.save()
                            except:
                                # Duplicate entry, so do nothing.
                                if verbose:
                                    print 'Unique Error: Duplicate host ' + ipv4 + ', ' \
                                        + hostname
                                else:
                                    pass
                        except django.http.response.Http404:
                            print '==================================='
                            print 'Could not find host %s' % ip
                            print '==================================='
            print '[Port %s] Saving to database...\n' % port
    print '=============================='
    print 'Database successfully updated!\n'


# Call funcitons.
import_ports()
