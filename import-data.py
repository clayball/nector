#!/usr/bin/env python2

'''
Purpose
=======

Uses provided Hosts, Vulnerabilities, Events data to populate the
Nector database.


Prerequisites
=============

hosts.xml, vulnlist.csv, events.csv, and openports.xml must exist in the current
directory, contain desired information, and be formatted properly.

Sample data files stored in sample-data/
- sample_hosts.xml
- sample-vulnlist.csv
- sample-events.csv
- sample-openports.xml


Postconditions
==============

The database will be populated with Hosts, Vulnerabilities, Events, and Ports
specified in hosts.xml, vulnlist.csv, events.csv, and openports.xml.
'''

# Import necessary libraries.

import sys
# Used for accessing environment info.
import os
# Used for accessing Django features.
import django
# Used for getting args
from optparse import OptionParser
# Used for parsing vulnlist.csv, events.csv, & censys-keys.csv
import csv
# Used for parsing ports from nmap xml file.
from lxml import etree
# Used for parsing port dicts.
import json
# Used for getting current date.
import time
# Used in optimization of runtime.
from django.db import transaction
# Used in checking for Unique issues.
from django.db import IntegrityError
# Used for getting Host object.
from django.shortcuts import get_object_or_404

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nector.settings")
django.setup()

# Import Django models.
from hosts.models import Subnet
from hosts.models import Host
from hosts.models import Alert
from vulnerabilities.models import Vulnerability
from events.models import Event

# Get names of files containing Host, Subnet, Vulnerability, Events, & censys
# data that we want to import.
host_file_name = 'hosts.xml'
vulnerability_file_name = 'vulnlist.csv'
events_file_name = 'events.csv'
openports_file_name = 'openports.xml'

# Open files
host_file = open(host_file_name, 'r')
vulnerability_file = open(vulnerability_file_name, 'r')
vulnerability_csv = csv.reader(vulnerability_file)
events_file = open(events_file_name, 'r')
events_csv = csv.reader(events_file)
openports_file = open(openports_file_name, 'r')

# Get & Set Options / Args
parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="Print error/success messages. Useful in debugging.")
(options, args) = parser.parse_args()
verbose = options.verbose

# Alert messages
MSG_HOST_ADD = "Host added to database"
MSG_HOST_REMOVE = "Host removed from database"
MSG_NEW_VULN = "New vulnerability discovered"
MSG_OPEN_PORT = "Port %s opened"
MSG_CLOSED_PORT = "Port %s closed"

# Alert date.
DATE = time.strftime("%m/%d/%Y")

# Adds Hosts to database
def populate_hosts():

    print '[*] Importing Hosts...'

    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        for line in host_file:
            # Remove cruft from the end of the line:
            l = line.rstrip()
            # If host has a hostname:
            if l[-1] == ')':
                # Parse info from nmap scan.
                lsplit = l.split(' ')
                ipv4 = lsplit[5].strip('()')
                hostname = lsplit[4].strip()

                # Check if host is already in database.
                # If it's not, it'd throw an error if we didn't have this check.
                # If an error is thrown, then transaction.atomic() breaks,
                # meaning it won't save any Hosts to the database.
                if Host.objects.filter(ipv4_address=ipv4, host_name=hostname).exists():
                    # Warn user.
                    print '[!] Host already in database: %s' % ipv4

                else:
                    # Host doesn't exist in our db, so create a new one.
                    h = Host(ipv4_address=ipv4, host_name=hostname)

                    # Create an alert for new host.
                    a = Alert(ipv4_address=ipv4, message=MSG_HOST_ADD, date=DATE)

                    # Save Host to db (won't actually happen until
                    #  'with transaction.atomic()' is completed):
                    try:
                        h.save()
                        a.save()
                    except Exception as e:
                        # This shouldn't happen, unless the user screwed up
                        # the nmap scan.
                        # If we get an exception here, then the database
                        # will not save any of the hosts.
                        print '[!] %s' % e

            elif l[0] != '#':
                # Host has no hostname, aka it has an NXDOMAIN.
                # '#' indicates last line of Nmap scan.
                ipv4 = l.split(' ')[4]

                # Check if host is already in database.
                # If it's not, it'd throw an error if we didn't have this check.
                # If an error is thrown, then transaction.atomic() breaks,
                # meaning it won't save any Hosts to the database.
                if Host.objects.filter(ipv4_address=ipv4).exists():
                    # Warn user.
                    print '[!] Host already in database: %s' % ipv4

                else:
                    # Host doesn't exist in our db, so create a new one.
                    h = Host(ipv4_address=ipv4, host_name='NXDOMAIN')

                    # Create an alert for new host.
                    a = Alert(ipv4_address=ipv4, message=MSG_HOST_ADD, date=DATE)

                    # Save Host to db (won't actually happen until
                    #  'with transaction.atomic()' is completed):
                    try:
                        h.save()
                        a.save()
                    except Exception as e:
                        # This shouldn't happen, unless the user screwed up
                        # the nmap scan.
                        # If we get an exception here, then the database
                        # will not save any of the hosts.
                        print '[!] %s' %e

    print '[*] Hosts: Done!'


# Get subnets from Hosts and add them to database
def populate_subnets():

    print '\n[*] Getting Subnets from Hosts...'

    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        all_hosts = Host.objects.all()
        for host in all_hosts:
            host_ip = host.ipv4_address
            host_subnet = host_ip.rsplit('.', 1)
            subnet_suffix = '.x'
            full_subnet = host_subnet[0] + subnet_suffix

            # Check if subnet is already in database.
            # If it's not, it'd throw an error if we didn't have this check.
            # If an error is thrown, then transaction.atomic() breaks,
            # meaning it won't save any Subnets to the database.
            if Subnet.objects.filter(ipv4_address=host_subnet[0], suffix=subnet_suffix).exists():
                # Warn user.
                if verbose:
                    print '[!] Subnet already in database: %s' % full_subnets

            else:
                # Subnet doesn't exist in our db, so create a new one.
                s = Subnet(ipv4_address=host_subnet[0], suffix=subnet_suffix)

                # Save Subnet to db (won't actually happen until
                #  'with transaction.atomic()' is completed):
                try:
                    s.save()
                except Exception as e:
                    # This shouldn't happen, unless the user screwed up
                    # the nmap scan.
                    # If we get an exception here, then the database
                    # will not save any of the subnets.
                    print '[!] %s' % e

    print '[*] Subnets: Done!'


# Adds Vulnerabilities to database
def populate_vulnerabilities():

    print '\n[*] Importing Vulnerabilities...'

    with transaction.atomic():
        next(vulnerability_csv) # Skip first entry of the csv file, a header.
        for row in vulnerability_csv:

            # Check if vulnerability is already in database.
            # If it's not, it'd throw an error if we didn't have this check.
            # If an error is thrown, then transaction.atomic() breaks,
            # meaning it won't save any vulns to the database.
            if Vulnerability.objects.filter(plugin_and_host=row[0]+row[4],
                    plugin_id=row[0], plugin_name=row[1], severity=row[2],
                    ipv4_address=row[3], host_name=row[4]).exists():
                # Warn user.
                if verbose:
                    print '[!] Vulnerability already in database: %s' % row[0]+row[4]

            else:
                v = Vulnerability(plugin_and_host=row[0]+row[4], plugin_id=row[0],
                        plugin_name=row[1], severity=row[2], ipv4_address=row[3],
                        host_name=row[4])

                # Create an alert for new vulnerability.
                a = Alert(ipv4_address=row[3], message=MSG_NEW_VULN, date=DATE)

                # Save Vulnerability to db (won't actually happen until
                #  'with transaction.atomic()' is completed):
                try:
                    v.save()
                    a.save()
                except Exception as e:
                    # This shouldn't happen, unless the user screwed up
                    # the vulnerability file.
                    # If we get an exception here, then the database
                    # will not save any of the vulnerabilities.
                    print '[!] %s' % e
    print '[*] Vulnerabilities: Done!'


# Adds Events to database
def populate_events():

    print '\n[*] Importing Events...'

    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():
        next(events_csv) # Skip first entry of the csv file, a header.
        for row in events_csv:

            # Check if Event is already in database.
            # If it's not, it'd throw an error if we didn't have this check.
            # If an error is thrown, then transaction.atomic() breaks,
            # meaning it won't save any Events to the database.
            if Event.objects.filter(request_number=row[0], date_submitted=row[1],
                    title=row[2], status=row[3], date_last_edited=row[4],
                    submitters=row[5], assignees=row[6].split(":")[0]).exists():
                # Warn user.
                if verbose:
                    print '[!] Event already in database: %s' % row[0]

            else:
                # Get event
                e = Event(request_number=row[0], date_submitted=row[1],
                        title=row[2], status=row[3], date_last_edited=row[4],
                        submitters=row[5], assignees=row[6].split(":")[0])

                # We only want to save Closed events
                if e.status == "Closed":
                    # Save Event to db (won't actually happen until
                    #  'with transaction.atomic()' is completed):
                    try:
                        e.save()
                    except Exception as e:
                        # This shouldn't happen, unless the user screwed up
                        # the events file.
                        # If we get an exception here, then the database
                        # will not save any of the events.
                        print '[!] %s' % e

    print '[*] Events: Done!'


# Adds Open Ports to database
def populate_openports():

    print '\n[*] Importing Open Ports...'

    tree = etree.parse(openports_file)

    # Allow changes to be made to db after nested blocks have been
    # completed.
    with transaction.atomic():

        host_list = {}
        port_list = []

        # Iterate through each <host> tag.
        for host_element in tree.iter("host"):

            # Get IPv4 addr of current host.
            host_ip = host_element.find('address').get('addr')

            host_list[host_ip] = []

            # Iterate through each <port> tag superceded by a <host> tag.
            for port_element in host_element.iter("port"):

                # Get Port number.
                port_number = port_element.get('portid')

                # Temp vars for getting info we want.
                product = version = x_info = ''

                try:
                    # Get port service. If no service, leave blank.
                    product = port_element.find('service').get('product')
                    if not product:
                        product = ''
                except:
                    pass
                try:
                    # Get service version. If no version, leave blank.
                    version = port_element.find('service').get('version')
                    if not version:
                        version = ''
                except:
                    pass
                try:
                    # Get service's extra info. If no info, leave blank.
                    x_info = '(' + port_element.find('service').get('extrainfo') + ')'
                    if not x_info:
                        x_info = ''
                except:
                    pass

                # Concatenate all port info into single string.
                service_info = product + ' ' + version + ' ' + x_info

                # If a port is in our nmap list, then it has to be open.
                status = 'open'

                # Add current port to port_list.
                # We'll use the list later to check for closed ports.
                if port_number not in port_list:
                    port_list.append(port_number)

                try:
                    # Get Host object with corresponding IPv4 address.
                    # Add it to host_list for later use.
                    host = get_object_or_404(Host, ipv4_address=host_ip)
                    host_list[host.ipv4_address].append(port_number)

                    # Create string formatted as dict for storing port
                    # info as a TextField.
                    dict_ports = "{\"%s\" : [\"%s\", \"%s\", \"%s\"]}" % \
                                    (port_number, status, service_info, DATE)

                    if not host.ports:
                        # Host doesn't have any ports, so we can assign it to
                        # our string directly.
                        host.ports = dict_ports
                        a = Alert(ipv4_address=host.ipv4_address, message=MSG_OPEN_PORT % port_number, date=DATE)
                        a.save()
                    else:
                        # Host does have ports, so we'll have to add port info
                        # to existing dict.
                        new_port_info = json.loads(host.ports)

                        # If port was not open but is now, we should
                        # add new Alert to our database.
                        try:
                            if new_port_info[port_number][0] != 'open':
                                a = Alert(ipv4_address=host.ipv4_address, message=MSG_OPEN_PORT % port_number, date=DATE)
                                a.save()
                        except:
                            pass

                        new_port_info[port_number] = [status, service_info, DATE]
                        host.ports = json.dumps(new_port_info)
                        if verbose:
                            print host.ports
                    # Save Host to db (won't actually happen until
                    #  'with transaction.atomic()' is completed):
                    try:
                        host.save()
                    except:
                        # Duplicate entry, so do nothing.
                        if verbose:
                            print '[Ports] Unique Error: Duplicate host ' + host_ip
                        else:
                            pass
                except django.http.response.Http404:
                    print '[!] Could not find host in database: %s' % host_ip

        # If port is now closed, then we wanna close it.
        # Iterate through each port number.
        for port_number in port_list:
            # Get all Host objects that have current port.
            hosts_w_port = Host.objects.filter(ports__icontains="\""+port_number+"\":")
            for h in hosts_w_port:
                # If host isn't in our host list, that means it used to have
                # current port open, but now it doesn't.
                if h.ipv4_address in host_list:
                    if port_number not in host_list[h.ipv4_address]:
                        # Mark port as closed and update db Host object.
                        closed_port = json.loads(h.ports)
                        if closed_port[port_number][0] == "open":
                            closed_port[port_number] = ["closed", str(closed_port[port_number][1]), DATE]
                            a = Alert(ipv4_address=h.ipv4_address, message=MSG_CLOSED_PORT % port_number, date=DATE)
                            a.save()
                            h.ports = json.dumps(closed_port)
                            h.save()
            print '[*] [Port %s] Saving to database...' % port_number
    print '[*] Open Ports: Done!'


def main():
    # Call functions.
    populate_hosts()
    populate_subnets()
    populate_vulnerabilities()
    populate_events()
    populate_openports()

    # Close files.
    host_file.close()
    vulnerability_file.close()
    events_file.close()
    openports_file.close()


if __name__ == "__main__":
    main()
