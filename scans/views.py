from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.template import loader

from forms import ScansForm

import subprocess # For nmap

'''
    Useful nmap scans we can use as defaults:
        1. Scan for UDP DDOS reflectors:
            nmap -sU -A -PN -n -pU:19,53,123,161 -script=ntp-monlist,dns-recursion,snmp-sysdescr 192.168.1.0/24
        2. Get HTTP headers of web services:
            nmap --script=http-headers 192.168.1.0/24
        3. Heartbleed Testing:
            nmap -sV -p 443 --script=ssl-heartbleed 192.168.1.0/24
        4. IP Information:
            nmap --script=asn-query,whois,ip-geolocation-maxmind 192.168.1.0/24
        5. Scan 100 most common ports (Fast):
            nmap -F 192.168.1.1
'''


def get_nmap_command(request, context):
    """TODO: Add results of the live scan to context. Display on page."""

    scan_name = context['scan_name']
    host_address = context['host_address']
    ports = context['ports']
    scan_options = context['scan_options']

    nmap_command = ['nmap']

    for opt in scan_options:
        if opt == 'version_detection':
            nmap_command.append('-sV')
        elif opt == 'os_and_services':
            nmap_command.append('-A')
        elif opt == 'fast':
            nmap_command.append('-F')
        elif opt == 'no_ping':
            nmap_command.append('-Pn')

    nmap_command.append(host_address)

    tmp_ports = []
    if ',' in ports:
        nmap_command.append('-p')

        tmp_ports = ports.split(',')

        str_port_list = ''

        for p in tmp_ports:
            p = p.strip()
            if int(p) > 0 and int(p) < 65535:
                str_port_list += str(p) + ','
            else:
                print 'Invalid port %s' % p

        nmap_command.append(str_port_list)

    elif '-' in ports:
        nmap_command.append('-p')

        tmp_ports = ports.split('-')

        is_valid_range = True
        for p in tmp_ports:
            p = p.strip()
            if int(p) > 0 and int(p) < 65535:
                print 'Good'
            else:
                is_valid_range = False

        if is_valid_range:
            nmap_command.append(ports)

    elif ' ' in ports:
        nmap_command.append('-p')

        tmp_ports = ports.split(' ')

        str_port_list = ''

        for p in tmp_ports:
            p = p.strip()
            if int(p) > 0 and int(p) < 65535:
                str_port_list += str(p) + ','
            else:
                print 'Invalid port %s' % p

        nmap_command.append(str_port_list)

    else:
        p = ports.strip()
        if int(p) > 0 and int(p) < 65535:
            nmap_command.append('-p')
            nmap_command.append(p)

    return nmap_command



def live_scan(request, context):
    nmap_command = get_nmap_command(request, context)

    # We're using check_output w/ universal_newlines & splitlines
    # in order to retain the shell's formatting.
    process = subprocess.check_output(nmap_command, universal_newlines=True).splitlines()

    context['nmap_output'] = process

    '''
    process = subprocess.Popen(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = process.communicate()

    context['nmap_output'] = out

    '''
    return render(request, 'scans/scans.html', context)


def index(request):
    '''
    Default search page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''

    live_scanning = False

    if request.POST.get("live_scan"):
        # User pressed Export button.
        live_scanning = True

    if request.method == "POST":
        # User is either Generating a table to the page (exporting=False)
        #             or Exporting to a CSV file (exporting=True).

        # Get form information.

        form = ScansForm(request.POST)

        if form.is_valid():

            scan_name = form.cleaned_data['scan_name']
            host_address = form.cleaned_data['host_address']
            ports = form.cleaned_data['ports']
            scan_options = form.cleaned_data['scan_options']

            # Append important info to context.
            context = {}

            context.update(csrf(request))
            context['scan_name'] = scan_name
            context['host_address'] = host_address
            context['ports'] = ports
            context['scan_options'] = scan_options
            context['form'] = form

            if live_scanning:
                return live_scan(request, context)

            # We're not exporting, so render the page with a table.
            return render(request, 'scans/scans.html', context)

    context = {}
    context.update(csrf(request))
    context['form'] = ScansForm()
    return render(request, 'scans/scans.html', context)
