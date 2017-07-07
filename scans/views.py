from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.template import loader

from forms import ScansForm


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

            # Append important info to context.
            context = {}

            context.update(csrf(request))
            context['form'] = form

            if live_scanning:
                return live_scan(request, context)

            # We're not exporting, so render the page with a table.
            return render(request, 'scans/scans.html', context)

    context = {}
    context.update(csrf(request))
    context['form'] = ScansForm()
    context['checks'] = ['ipv4_address', 'host_name', 'ports']
    return render(request, 'scans/scans.html', context)


def live_scan(request, context):
    """TODO: Add results of the live scan to context. Display on page."""
    return render(request, 'scans/scans.html', context)
