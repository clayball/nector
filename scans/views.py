from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.template import loader
from django.template.context_processors import csrf

# Our custom form. See ./forms.py for more info.
from forms import ScansForm

from hosts.models import Host
from hosts.models import Subnet
from django.db import models

import json

# Exporting CSV
import csv
from django.http import StreamingHttpResponse

def index(request):
    '''
    Default loading page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''
    exporting = False
    if request.POST.get("export"):
        exporting = True
    if request.method == "POST":
        form = ScansForm(request.POST)
        if form.is_valid():
            context = {}
            context['checks'] = request.POST.getlist('checks')
            context['rad'] = request.POST.getlist('rad')
            processed_query = process_query(form, context['checks'], context['rad'])
            context['open_ports'], context['host_list'] = get_open_ports_and_new_list(processed_query)
            context['subnet_list'] = get_subnet_list(context['host_list'])
            context['host_data'] = zip(context['host_list'], context['subnet_list'])
            context.update(csrf(request))
            context['form'] = form
            if exporting:
                return export(request, context)
            return render_to_response('scans/scans.html', context)
    context = {}
    context.update(csrf(request))
    context['form'] = ScansForm()
    context['checks'] = ['ipv4_address', 'host_name', 'ports']
    return render_to_response('scans/scans.html', context)


def process_query(form, checks, rad):
    '''
    Parses data from form and gets all objects that have that data.
    Returns QuerySet of Hosts.
    '''
    ipv4_address = form.cleaned_data['ipv4_address']
    host_name = form.cleaned_data['host_name']
    ports = form.cleaned_data['ports']
    os = form.cleaned_data['os']
    lsp = form.cleaned_data['lsp']
    host_groups = form.cleaned_data['host_groups']
    location = form.cleaned_data['location']
    tags = form.cleaned_data['tags']
    notes = form.cleaned_data['notes']

    host_list = []

    # Check if multiple ports entered (ex 80, 443)
    if ',' in ports:
        ports = ports.split(',')
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)
        # Filter each specified port, one at a time.
        for p in ports:
            p = p.strip()
            host_list = host_list.filter(ports__icontains='"'+p+'"'+':')
    elif ports.strip():
        # Single port entered, so single filter needed:
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        ports__icontains='"'+ports+'"'+':',
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)
    else:
        # No port entered:
        host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                        host_name__icontains=host_name,
                                        os__icontains=os,
                                        lsp__icontains=lsp,
                                        host_groups__icontains=host_groups,
                                        location__icontains=location,
                                        tags__icontains=tags,
                                        notes__icontains=notes)

    # Did we select Online-Only or Offline-Only or All Hosts?
    if 'online' in rad:
        host_list = host_list.exclude(notes__icontains='Offline')
    elif 'offline' in rad:
        host_list = host_list.filter(notes__icontains='Offline')

    return host_list


def get_open_ports_and_new_list(host_list):
    '''
    Returns a tuple following (open_ports, host_list).
    open_ports is a dict following {ip: [ports]}.
    host_list is a QuerySet.
    Example return value:
        {'123.45.67.89': ['80', '443']}, <Host QuerySet>
    If a port is not open, then we won't add the port to the dict.
    If a port is not open, then we will remove the respective Host
    from the host_list since we don't want to display that Host.
    '''
    open_ports = {}
    for h in host_list:
        if h.ports: # If the host has ports:
            port_json = json.loads(h.ports)
            h_ports = []
            has_open_port = False
            for p in port_json:
                # Port is open, add to list .
                if port_json[p][0] == 'open':
                    h_ports.append(str(p))
                    has_open_port = True
                # Port is closed, remove Host from host_list.
                elif port_json[p][0] == 'closed':
                    host_list = host_list.exclude(ipv4_address=h.ipv4_address)
                else:
                    print 'Something went wrong! (scans/views.py -> get_open_ports_and_new_list())'
            # Make sure it has an open port before we add it to the final dict.
            # Otherwise, we are throwing in an empty list, and who needs that?
            if has_open_port:
                open_ports[str(h.ipv4_address)] = h_ports
    return open_ports, host_list


def get_subnet_list(host_list):
    subnet_list = []
    for h in host_list:
        h_ip = h.ipv4_address
        subnet_address = h_ip.rsplit('.', 1)
        try:
            subnet_list.append(Subnet.objects.get(ipv4_address__startswith=subnet_address[0]))
        except:
            print 'ERROR: Could not find subnet for ' + h_ip
    return subnet_list


class Echo(object):
    '''
    An object that implements just the write method of the file-like
    interface.
    '''
    def write(self, value):
        '''Write the value by returning it, instead of storing in a buffer.'''
        return value

def export(request, context):
    '''
    Looks at what info the user wants exported, and parses that out of
    'context'.
    Returns a response that creates a popup on the page asking the user
    to download a CSV file.
    Uses the Echo class (above) as a means of storing data in a buffer.
    '''

    existing_header_columns = []

    # Bools to keep track of what was selected.
    # Will be used for determining what gets outputted to csv file.
    sel_ip = sel_name = sel_ports = sel_os = sel_lsp = sel_groups \
    = sel_location = sel_tags = sel_notes = False

    if 'ipv4_address' in context['checks']:
        existing_header_columns.append('IPv4')
        sel_ip = True
    if 'host_name' in context['checks']:
        existing_header_columns.append('Name')
        sel_name = True
    if 'ports' in context['checks']:
        existing_header_columns.append('Ports')
        sel_ports = True
    if 'os' in context['checks']:
        existing_header_columns.append('OS')
        sel_os = True
    if 'lsp' in context['checks']:
        existing_header_columns.append('LSP')
        sel_lsp = True
    if 'host_groups' in context['checks']:
        existing_header_columns.append('Host Groups')
        sel_groups = True
    if 'location' in context['checks']:
        existing_header_columns.append('Location')
        sel_location = True
    if 'tags' in context['checks']:
        existing_header_columns.append('Tags')
        sel_tags = True
    if 'notes' in context['checks']:
        existing_header_columns.append('Notes')
        sel_notes = True

    ipv4_addresses = [host.ipv4_address for host in context['host_list']]
    host_names = [host.host_name for host in context['host_list']]
    open_ports = context['open_ports']
    oses = [host.os for host in context['host_list']]
    lsps = [host.lsp for host in context['host_list']]
    host_groups = [host.host_groups for host in context['host_list']]
    locations = [host.location for host in context['host_list']]
    tags = [host.tags for host in context['host_list']]
    notes = [host.notes for host in context['host_list']]

    host_data = zip(ipv4_addresses, host_names, oses, lsps,
                    host_groups, locations, tags, notes)

    # NOTE: Lines with #new utilize a buffer and a stream.
    #       They're great for dealing with large CSV files.
    #       Lines with #old just write lines one-by-one into the file.

    pseudo_buffer = Echo() #new
    writer = csv.writer(pseudo_buffer) #new
    #response = HttpResponse(content_type='text/csv') #old
    #writer = csv.writer(response) #old
    output = []
    output.append(existing_header_columns)

    for ip, name, os, lsp, group, loc, tag, note in host_data:
        tmp = []
        if sel_ip:
            tmp.append(ip)
        if sel_name:
            tmp.append(name)
        if sel_ports:
            if ip in open_ports:
                tmp.append(open_ports[ip])
            else:
                tmp.append('')
        if sel_os:
            tmp.append(os)
        if sel_lsp:
            tmp.append(lsp)
        if sel_groups:
            tmp.append(group)
        if sel_location:
            tmp.append(loc)
        if sel_tags:
            tmp.append(tag)
        if sel_notes:
            tmp.append(note)
        output.append(tmp)
    response = StreamingHttpResponse((writer.writerow(row) for row in output),
                                        content_type="text/csv") #new
    #writer.writerows(output) #old
    response['Content-Disposition'] = 'attachment; filename="export.csv"' #new
    return response
