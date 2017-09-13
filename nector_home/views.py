from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db import connection

from hosts.models import Host
from vulnerabilities.models import Vulnerability
from events.models import Event
from malware.models import Malware


def index(request):
    installation_complete = False

    hosts_installed = Host.objects.all().exists()
    vulns_installed = Vulnerability.objects.all().exists()
    events_installed = Event.objects.all().exists()
    malware_installed = Malware.objects.all().exists()

    if hosts_installed and vulns_installed and events_installed and malware_installed:
        installation_complete = True

    context = {'hosts_installed' : hosts_installed,
               'vulns_installed' : vulns_installed,
               'events_installed' : events_installed,
               'malware_installed' : malware_installed,
               'installation_complete' : installation_complete,
               'db_type' : connection.vendor}

    if installation_complete:
        return about(request)
    return render(request, 'nector_home/status.html', context)


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


def status(request):
    installation_complete = False

    hosts_installed = Host.objects.all().exists()
    vulns_installed = Vulnerability.objects.all().exists()
    events_installed = Event.objects.all().exists()
    malware_installed = Malware.objects.all().exists()

    if hosts_installed and vulns_installed and events_installed and malware_installed:
        installation_complete = True

    context = {'hosts_installed' : hosts_installed,
               'vulns_installed' : vulns_installed,
               'events_installed' : events_installed,
               'malware_installed' : malware_installed,
               'installation_complete' : installation_complete,
               'db_type' : connection.vendor}

    return render(request, 'nector_home/status.html', context)
