from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.template import loader
from django.template.context_processors import csrf

# Our custom form. See ./forms.py for more info.
from forms import ScansForm

from hosts.models import Host
from django.db import models

import json

def index(request):
    '''
    Default loading page.
    If a POST request was made to get here, then our form was submitted,
    so display a table of the query made.
    Otherwise, just display the form.
    '''
    if request.method == "POST":
        form = ScansForm(request.POST)
        if form.is_valid():
            context = {}
            processed_query = process_query(form)
            context['host_list'] = processed_query
            context['open_ports'] = get_open_ports(processed_query)
            context.update(csrf(request))
            context['form'] = ScansForm()
            context['checks'] = request.POST.getlist('checks')
            return render_to_response('scans/scans.html', context)
    context = {}
    context.update(csrf(request))
    context['form'] = ScansForm()
    return render_to_response('scans/scans.html', context)


def process_query(form):
    '''
    Helper function for index().
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
    # Check multiple ports
    # TODO
    '''if ',' in ports:
        ports = ports.split(',')
        print ports'''
    host_list = Host.objects.filter(ipv4_address__icontains=ipv4_address,
                                    host_name__icontains=host_name,
                                    ports__icontains=ports,
                                    os__icontains=os,
                                    lsp__icontains=lsp,
                                    host_groups__icontains=host_groups,
                                    location__icontains=location,
                                    tags__icontains=tags,
                                    notes__icontains=notes)
    '''
    # Remove all closed ports from host-list:
    for h in host_list:
        if h.ports:
            port_json = json.loads(h.ports)
            all_ports = []
            for p in port_json:
                all_ports.append(p)
                if p == ports:
                    if 'closed' in port_json[ports]:
                        print h.ipv4_address
                        host_list = host_list.exclude(ipv4_address=h.ipv4_address)
            # Port searched for was part of port json, not the port # itself.
            if ports not in all_ports:
                host_list = host_list.exclude(ipv4_address=h.ipv4_address)
    '''
    return host_list


def get_open_ports(host_list):
    all_ports = {}
    for h in host_list:
        if h.ports:
            port_json = json.loads(h.ports)
            h_ports = []
            for p in port_json:
                h_ports.append(str(p))
            all_ports[h.ipv4_address] = h_ports
    return all_ports


def export(request):
    # todo
    return render_to_response('scans/scans.html')
