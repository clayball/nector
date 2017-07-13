from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.template import loader

from forms import ScansForm

from models import ScanType

import subprocess # For nmap

import json

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

    if ports:
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


def delete_scan(request, context):
    if request.POST:
        if request.user.is_authenticated():
            if 'selected_scan_name' in request.POST:
                scan_to_delete = request.POST['selected_scan_name']
                user = request.user
                try:
                    scan_inst = ScanType.objects.get(scan_name=scan_to_delete)
                    scan_inst.delete()
                except Exception as e:
                    print '%s' % e
    return render(request, 'scans/scans.html', context)


def edit_scan(request):

    context = {}

    scan_name = request.POST.get("selected_scan_name")

    scan_obj = get_object_or_404(ScanType, scan_name=scan_name, user=request.user)

    scan_options = []

    dirty_scan_options = scan_obj.scan_options

    if 'version_detection' in dirty_scan_options:
        scan_options.append('version_detection')
    if 'os_and_services' in dirty_scan_options:
        scan_options.append('os_and_services')
    if 'fast' in dirty_scan_options:
        scan_options.append('fast')
    if 'no_ping' in dirty_scan_options:
        scan_options.append('no_ping')

    scan_obj.scan_options = scan_options

    form = ScansForm(instance=scan_obj)

    if request.user.is_authenticated():
        saved_scans = ScanType.objects.filter(user=request.user)
        context['saved_scans'] = saved_scans

    context.update(csrf(request))
    context['form'] = form
    return render(request, 'scans/scans.html', context)


def index(request):
    '''
    Default search page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''

    context = {}

    if request.user.is_authenticated():
        saved_scans = ScanType.objects.filter(user=request.user)
        context['saved_scans'] = saved_scans

    live_scanning = False


    if request.POST.get("live_scan"):
        # User pressed Export button.
        live_scanning = True

    if request.method == "POST":

        if request.POST.get("btn_edit_scan"):
            print 'edit'
            return edit_scan(request)

        elif request.POST.get("btn_live_scan"):
            print 'live'
            scan_name = request.POST.get("selected_scan_name")

            scan_obj = get_object_or_404(ScanType, scan_name=scan_name, user=request.user)

            scan_name = scan_obj.scan_name
            host_address = scan_obj.host_address
            ports = scan_obj.ports
            scan_options = []

            dirty_scan_options = scan_obj.scan_options

            if 'version_detection' in dirty_scan_options:
                scan_options.append('version_detection')
            if 'os_and_services' in dirty_scan_options:
                scan_options.append('os_and_services')
            if 'fast' in dirty_scan_options:
                scan_options.append('fast')
            if 'no_ping' in dirty_scan_options:
                scan_options.append('no_ping')


            # Append important info to context.

            context.update(csrf(request))
            context['scan_name'] = scan_name
            context['host_address'] = host_address
            context['ports'] = ports
            context['scan_options'] = scan_options

            if request.user.is_authenticated():
                saved_scans = ScanType.objects.filter(user=request.user)
                context['saved_scans'] = saved_scans

            scan_obj.scan_options = scan_options

            context.update(csrf(request))
            form = ScansForm(instance=scan_obj)
            context['form'] = form
            return live_scan(request, context)

        elif request.POST.get("btn_delete_scan"):
            print 'delete'
            context = {}

            if request.user.is_authenticated():
                saved_scans = ScanType.objects.filter(user=request.user)
                context['saved_scans'] = saved_scans

            context.update(csrf(request))
            form = ScansForm()
            context['form'] = form

            return delete_scan(request, context)

        else:

            # Get form information.
            print 'else'

            form = ScansForm(request.POST)

            if form.is_valid():

                scan_name = form.cleaned_data['scan_name']
                host_address = form.cleaned_data['host_address']
                ports = form.cleaned_data['ports']
                scan_options = form.cleaned_data['scan_options'].split(',')

                # Append important info to context.

                context.update(csrf(request))
                context['scan_name'] = scan_name
                context['host_address'] = host_address
                context['ports'] = ports
                context['scan_options'] = scan_options
                context['form'] = form

                '''
                existing_scan_instance = None
                if ScanType.objects.filter(scan_name=scan_name).exists():
                    existing_scan_instance = get_object_or_404(ScanType, scan_name=scan_name)
                '''

                if live_scanning:
                    # Perform live nmap scan.
                    return live_scan(request, context)
                else:
                    # Save scantype to db.
                    if request.user.is_authenticated():
                        user = request.user

                        str_scan_options = ''
                        for option in scan_options[:-1]:
                            str_scan_options += option + ','
                        str_scan_options += scan_options[-1]
                        print str_scan_options

                        new_scan = ScanType(scan_name=scan_name, user=user,
                                            host_address=host_address, ports=ports,
                                            scan_options=scan_options)
                        new_scan.save()

                # We're not exporting, so render the page with a table.
                return render(request, 'scans/scans.html', context)

    context.update(csrf(request))
    context['form'] = ScansForm()
    return render(request, 'scans/scans.html', context)
