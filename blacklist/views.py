from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from hosts.models import Host
from hosts.models import Subnet
import urllib2

def index(request):
    '''Render default Blacklist page.'''

    # Default with 'My Malicious Hosts.'
    bad_ip_data = fetch_bad_ips(True)

    bad_ips = []
    bad_ip_subnets = []

    # For all of OUR malicious Hosts found in Talos,
    # add them and their subnets to lists so they can
    # be passed to the template as context.
    for i in bad_ip_data:
        bad_ips.append(Host.objects.get(ipv4_address=i[0]))
        bad_ip_subnets.append(i[1])

    # Pass context to rendered page.
    context = {'bad_ips' : bad_ips, 'bad_ip_data' : zip(bad_ips, bad_ip_subnets), 'selected' : 'my_hosts'}
    return render(request, 'blacklist/blacklist.html', context)


def fetch_bad_ips(only_my_hosts=True):
    '''Get malicious IPs from Talos Intelligence.'''
    bad_ips = []
    bad_ip_subnets = []

    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    # Read in the malicious IPs from Talos
    read_bad_ips = opener.open("http://www.talosintelligence.com/feeds/ip-filter.blf").readlines()
    # We want to remove '\n' from end of site-read IPs.
    read_bad_ips = [word.rstrip() for word in read_bad_ips]

    # Was "My Malicious Hosts" selected?
    if only_my_hosts:
        # Store all of OUR host object's IPv4 addresses in a list.
        addresses = Host.objects.values_list('ipv4_address', flat=True)
        # Get all hosts that exist in both OUR db and on Talos (Blacklist).
        bad_ips = list(set(read_bad_ips).intersection(addresses))

        # Get subnets for all of OUR ips so we can
        # add hyperlinks to them in our template.
        for ip in bad_ips:
            subnet_address = str(ip).rsplit('.', 1)
            bad_ip_subnets.append(Subnet.objects.get( \
                ipv4_address__startswith=subnet_address[0]))
    else:
        # We want ALL the malicious hosts.
        bad_ips = read_bad_ips
        bad_ip_subnets = [None]*len(bad_ips)
    return zip(bad_ips, bad_ip_subnets)


def limit_hosts(request):
    '''Renders Blacklist page that filters out malicious hosts using
       the dropdown menu.'''
    bad_ips = []
    bad_ip_subnets = []
    try:
        if request.method == 'GET':
            # Get whatever the user selected in the dropdown menu.
            query = request.GET.get('select_hosts', None)

            # If the user selected "my_hosts", then only hosts that
            # exist in both our db and the Blacklist will be displayed.
            if query == "my_hosts":
                bad_ip_data = fetch_bad_ips()
                for i in bad_ip_data:
                    bad_ips.append(i[0])
                    bad_ip_subnets.append(i[1])

            # Else, we'll just display the Blacklist hosts.
            else:
                bad_ip_data = fetch_bad_ips(False)
                for i in bad_ip_data:
                    bad_ips.append(i[0])

            # Context passed to rendered page.
            context = {
                       'bad_ips' : bad_ips,
                       'bad_ip_data' : zip(bad_ips, bad_ip_subnets),
                       'selected' : query,
                      }
            return render(request, 'blacklist/blacklist.html', context)
    except:
        return render(request, 'blacklist/blacklist.html')
