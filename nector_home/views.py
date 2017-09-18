from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db import connection
from django.template.context_processors import csrf

from hosts.models import Host
from vulnerabilities.models import Vulnerability
from events.models import Event
from malware.models import Malware

import os.path # Used to check for existing subnets.txt
import subprocess # Used for performing nmap scans.


def index(request):
    return status(request)


def osint(request):
    return render(request, 'nector_home/osint.html')


def detection(request):
    return render(request, 'nector_home/detection.html')


def reports(request):
    return render(request, 'nector_home/reports.html')


def about(request):
    return render(request, 'nector_home/about.html')


def settings(request):
    return render(request, 'nector_home/settings.html')


# 'sup' is shorthand for 'setup'
def status(request, sup_hosts=False, sup_ports=False, sup_events=False, sup_vulns=False, sup_malware=False):
    installation_complete = False

    subnets_installed = os.path.isfile('subnets.txt')

    hosts_installed = Host.objects.all().exists()
    vulns_installed = Vulnerability.objects.all().exists()
    events_installed = Event.objects.all().exists()
    malware_installed = Malware.objects.all().exists()
    ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

    if hosts_installed and vulns_installed and events_installed and malware_installed:
        installation_complete = True

    context = {'subnets_installed' : subnets_installed,
               'hosts_installed'   : hosts_installed,
               'vulns_installed'   : vulns_installed,
               'events_installed'  : events_installed,
               'malware_installed' : malware_installed,
               'ports_installed'   : ports_installed,
               'installation_complete' : installation_complete,
               'sup_hosts'   : sup_hosts,
               'sup_ports'   : sup_ports,
               'sup_events'  : sup_events,
               'sup_vulns'   : sup_vulns,
               'sup_malware' : sup_malware,
               'db_type' : connection.vendor}

    if installation_complete:
        return about(request)
    return render(request, 'nector_home/status.html', context)


def status_setup_hosts(request):
    return status(request, sup_hosts=True)


def status_setup_ports(request):
    # If Hosts haven't been imported, then do that first.
    if not Host.objects.all().exists():
        return status(request, sup_hosts=True)
    return status(request, sup_ports=True)


def status_setup_events(request):
    return status(request, sup_events=True)


def status_setup_vulns(request):
    return status(request, sup_vulns=True)


def status_setup_malware(request):
    return status(request, sup_malware=True)


def submit_subnets(request):
    if not request.POST:
        return status(request)

    if 'subnet_ips' in request.POST:
        subnets_txt = open('subnets.txt', 'w')
        subnets_txt.write(request.POST['subnet_ips'])
        subnets_txt.close()

    elif 'subnet_file' in request.FILES:
        input_file = request.FILES['subnet_file'].read()
        with open('subnets.txt', 'w') as subnets_txt:
            for line in input_file:
                subnets_txt.write(line)
            subnets_txt.close()

    return status(request, sup_hosts=True)


def update_db():
    subprocess.call(['python', 'import-data.py'])


def nmap_hosts(request):
    nmap_status = subprocess.call(['nmap', '-sL', '-iL', 'subnets.txt', '-oN', 'hosts.xml'])
    update_db()
    return status(request)


def nmap_ports(request):
    nmap_status = subprocess.call(['nmap', '-Pn', '-sV', '--version-light', '-T5', '-p17,19,21,22,23,25,53,80,123,137,139,153,161,443,445,548,636,1194,1337,1900,3306,3389,4380,4444,4672,5353,5900,6000,6881,8000,8080,9050,31337', '-iL', 'subnets.txt', '--open', '-oX', 'openports.xml', '2>&1', '>', '/dev/null'])
    update_db()
    return status(request)
