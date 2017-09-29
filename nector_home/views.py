from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db import connection
from django.template.context_processors import csrf
from django.forms import formset_factory

from hosts.models import Host
from vulnerabilities.models import Vulnerability
from events.models import Event
from malware.models import Malware

from forms import EventForm, VulnForm, MalwareForm

import os.path # Used to check for existing subnets.txt
import subprocess # Used for performing nmap scans.


def index(request):
    installation_complete = False

    subnets_installed = os.path.isfile('subnets.txt')

    hosts_installed = Host.objects.all().exists()
    vulns_installed = Vulnerability.objects.all().exists()
    events_installed = Event.objects.all().exists()
    malware_installed = Malware.objects.all().exists()
    ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

    if hosts_installed and vulns_installed and events_installed \
       and ports_installed and malware_installed:
        installation_complete = True

    context = {'subnets_installed' : subnets_installed,
               'hosts_installed'   : hosts_installed,
               'vulns_installed'   : vulns_installed,
               'events_installed'  : events_installed,
               'malware_installed' : malware_installed,
               'ports_installed'   : ports_installed,
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


# 'sup' is shorthand for 'setup'
def status(request, sup_hosts=False, sup_ports=False, sup_events=False, sup_vulns=False, sup_malware=False, changing_db=False):
    installation_complete = False

    subnets_installed = os.path.isfile('subnets.txt')

    hosts_installed = Host.objects.all().exists()
    vulns_installed = Vulnerability.objects.all().exists()
    events_installed = Event.objects.all().exists()
    malware_installed = Malware.objects.all().exists()
    ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

    if hosts_installed and vulns_installed and events_installed \
       and ports_installed and malware_installed:
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
               'changing_db' : changing_db,
               'db_type' : connection.vendor}

    if sup_events:
        context['events_form'] = formset_factory(EventForm)
        context['extra_forms'] = 1

    if sup_vulns:
        context['vulns_form'] = formset_factory(VulnForm)
        context['extra_forms'] = 1

    if sup_malware:
        context['mals_form'] = formset_factory(MalwareForm)
        context['extra_forms'] = 1

    return render(request, 'nector_home/status.html', context)


def change_db(request):
    return status(request, changing_db=True)


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


def status_skip_hosts(request):
    Host.objects.create(ipv4_address="0", ports='"":""')
    return status(request)


def status_skip_ports(request):
    return status_skip_hosts(request)


def status_skip_events(request):
    Event.objects.create(request_number="")
    return status(request)


def status_skip_vulns(request):
    Vulnerability.objects.create(plugin_and_host="")
    return status(request)


def status_skip_malware(request):
    Malware.objects.create()
    return status(request)


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


def submit_hosts(request):
    if not request.POST:
        return status(request, sup_hosts=True)

    elif 'hosts_file' in request.FILES:
        input_file = request.FILES['hosts_file'].read()
        with open('hosts.xml', 'w') as hosts_xml:
            for line in input_file:
                hosts_xml.write(line)
            hosts_xml.close()
        update_db()
        return status(request)

    else:
        return status(request)


def submit_ports(request):
    if not request.POST:
        return status(request, sup_ports=True)

    elif 'ports_file' in request.FILES:
        input_file = request.FILES['ports_file'].read()
        with open('openports.xml', 'w') as openports_xml:
            for line in input_file:
                openports_xml.write(line)
            openports_xml.close()
        update_db()
        return status(request)

    else:
        return status(request)


def submit_events(request):
    if not request.POST:
        return status(request, sup_events=True)

    extra_forms = 1

    if 'add-additional-event' in request.POST:

        extra_forms = int(request.POST['num_extra_forms']) + 1
        events_formset = formset_factory(EventForm, extra=extra_forms)

        installation_complete = False

        subnets_installed = os.path.isfile('subnets.txt')

        hosts_installed = Host.objects.all().exists()
        vulns_installed = Vulnerability.objects.all().exists()
        events_installed = Event.objects.all().exists()
        malware_installed = Malware.objects.all().exists()
        ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

        if hosts_installed and vulns_installed and events_installed \
           and ports_installed and malware_installed:
            installation_complete = True

        context = {'subnets_installed' : subnets_installed,
                   'hosts_installed'   : hosts_installed,
                   'vulns_installed'   : vulns_installed,
                   'events_installed'  : events_installed,
                   'malware_installed' : malware_installed,
                   'ports_installed'   : ports_installed,
                   'installation_complete' : installation_complete,
                   'db_type' : connection.vendor}

        context['events_form'] = events_formset
        context['sup_events'] = True
        context['extra_forms'] = extra_forms

        return render(request, 'nector_home/status.html', context)

    elif 'event_file' in request.FILES:
        input_file = request.FILES['event_file'].read()
        with open('events.csv', 'w') as events_csv:
            for line in input_file:
                events_csv.write(line)
            events_csv.close()
        update_db()
        return status(request)

    else:
        extra_forms = int(request.POST['num_extra_forms'])
        events_formset = formset_factory(EventForm, extra=extra_forms)
        events_formset = events_formset(request.POST)
        with open('events.csv', 'w') as events_csv:
            events_csv.write('Request Number,Date Submitted,Title,Status,Last Edit Date,Submitted By,Assignees\n')
            for f in events_formset:
                if f.is_valid():
                    try:
                        instance = f.save(commit=False)
                        instance.save()
                    except Exception as e:
                        print e
                    clean = f.cleaned_data
                    try:
                        line = '%s,%s,%s,%s,%s,%s,%s\n' % (clean['request_number'],
                                                         clean['date_submitted'],
                                                         clean['title'],
                                                         clean['status'],
                                                         clean['date_last_edited'],
                                                         clean['submitters'],
                                                         clean['assignees'])
                        events_csv.write(line)
                    except Exception as e:
                        print e
            events_csv.close()
        return status(request)


def submit_vulns(request):
    if not request.POST:
        return status(request, sup_vulns=True)

    extra_forms = 1

    if 'add-additional-event' in request.POST:

        extra_forms = int(request.POST['num_extra_forms']) + 1
        vulns_formset = formset_factory(VulnForm, extra=extra_forms)

        installation_complete = False

        subnets_installed = os.path.isfile('subnets.txt')

        hosts_installed = Host.objects.all().exists()
        vulns_installed = Vulnerability.objects.all().exists()
        events_installed = Event.objects.all().exists()
        malware_installed = Malware.objects.all().exists()
        ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

        if hosts_installed and vulns_installed and events_installed \
           and ports_installed and malware_installed:
            installation_complete = True

        context = {'subnets_installed' : subnets_installed,
                   'hosts_installed'   : hosts_installed,
                   'vulns_installed'   : vulns_installed,
                   'events_installed'  : events_installed,
                   'malware_installed' : malware_installed,
                   'ports_installed'   : ports_installed,
                   'installation_complete' : installation_complete,
                   'db_type' : connection.vendor}

        context['vulns_form'] = vulns_formset
        context['sup_vulns'] = True
        context['extra_forms'] = extra_forms

        return render(request, 'nector_home/status.html', context)

    elif 'vuln_file' in request.FILES:
        input_file = request.FILES['vuln_file'].read()
        with open('vulnlist.csv', 'w') as vulnlist_csv:
            for line in input_file:
                vulnlist_csv.write(line)
            vulnlist_csv.close()
        update_db()
        return status(request)

    else:
        extra_forms = int(request.POST['num_extra_forms'])
        vulns_formset = formset_factory(VulnForm, extra=extra_forms)
        vulns_formset = vulns_formset(request.POST)
        with open('vulnlist.csv', 'w') as vulnlist_csv:
            vulnlist_csv.write('"Plugin","Plugin Name","Severity","IP Address","DNS Name"\n')
            for f in vulns_formset:
                if f.is_valid():
                    clean = f.cleaned_data
                    try:
                        line = '"%s","%s","%s","%s","%s"\n' % (clean['plugin_id'],
                                                         clean['plugin_name'],
                                                         clean['severity'],
                                                         clean['ipv4_address'],
                                                         clean['host_name'],)

                        vulnlist_csv.write(line)
                    except Exception as e:
                        print e
            vulnlist_csv.close()
        update_db()
        return status(request)


def submit_malware(request):
    if not request.POST:
        return status(request, sup_malware=True)

    extra_forms = 1

    if 'add-additional-event' in request.POST:

        extra_forms = int(request.POST['num_extra_forms']) + 1
        malware_formset = formset_factory(MalwareForm, extra=extra_forms)

        installation_complete = False

        subnets_installed = os.path.isfile('subnets.txt')

        hosts_installed = Host.objects.all().exists()
        vulns_installed = Vulnerability.objects.all().exists()
        events_installed = Event.objects.all().exists()
        malware_installed = Malware.objects.all().exists()
        ports_installed = Host.objects.all().filter(ports__icontains='"').exists()

        if hosts_installed and vulns_installed and events_installed \
           and ports_installed and malware_installed:
            installation_complete = True

        context = {'subnets_installed' : subnets_installed,
                   'hosts_installed'   : hosts_installed,
                   'vulns_installed'   : vulns_installed,
                   'events_installed'  : events_installed,
                   'malware_installed' : malware_installed,
                   'ports_installed'   : ports_installed,
                   'installation_complete' : installation_complete,
                   'db_type' : connection.vendor}

        context['mals_form'] = malware_formset
        context['sup_malware'] = True
        context['extra_forms'] = extra_forms

        return render(request, 'nector_home/status.html', context)

    elif 'malware_file' in request.FILES:
        input_file = request.FILES['malware_file'].read()
        with open('malware.csv', 'w') as malware_csv:
            for line in input_file:
                malware_csv.write(line)
            malware_csv.close()
        update_db()
        return status(request)

    else:
        extra_forms = int(request.POST['num_extra_forms'])
        mals_formset = formset_factory(MalwareForm, extra=extra_forms)
        mals_formset = mals_formset(request.POST)
        with open('malware.csv', 'w') as malware_csv:
            malware_csv.write('AlertID,AlertType,File,Computer,NumericIP,ContactGroup,Virus,ActualAction,Comment\n')
            for f in mals_formset:
                if f.is_valid():
                    clean = f.cleaned_data
                    try:
                        line = '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (clean['alert_id'],
                                                         clean['alert_type'],
                                                         clean['file_name'],
                                                         clean['computer'],
                                                         clean['numeric_ip'],
                                                         clean['contact_group'],
                                                         clean['virus'],
                                                         clean['actual_action'],
                                                         clean['comment'])

                        malware_csv.write(line)
                    except Exception as e:
                        print e
            malware_csv.close()
        update_db()
        return status(request)
