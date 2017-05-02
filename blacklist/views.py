from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from hosts.models import Host
from hosts.models import Subnet
import urllib2

def index(request):
    # Default with 'My Malicious Hosts.'
    bad_ip_data = fetch_bad_ips(True)
    bad_ips = []
    bad_ip_subnets = []
    for i in bad_ip_data:
        bad_ips.append(Host.objects.get(ipv4_address=i[0]))
        bad_ip_subnets.append(i[1])
    context = {'bad_ips' : bad_ips, 'bad_ip_data' : zip(bad_ips, bad_ip_subnets), 'selected' : 'my_hosts'}
    return render(request, 'blacklist/blacklist.html', context)


# Get malicious IPs from Talos Intelligence
def fetch_bad_ips(only_my_hosts=True):
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
        addresses = Host.objects.values_list('ipv4_address', flat=True)
        bad_ips = list(set(read_bad_ips).intersection(addresses))
        for ip in bad_ips:
            subnet_address = str(ip).rsplit('.', 1)
            bad_ip_subnets.append(Subnet.objects.get( \
                ipv4_address__startswith=subnet_address[0]))
    else:
        # We want ALL the malicious hosts.
        bad_ips = read_bad_ips
        bad_ip_subnets = [None]*len(bad_ips)
    return zip(bad_ips, bad_ip_subnets)

# If we can filter out a Host with provided ip, then it exists in our DB.
def ip_exists_in_db(ip):
    return Host.objects.filter(ipv4_address=ip).exists()

# Used for filtering out your malicious hosts using dropdown menu.
def limit_hosts(request):
    bad_ips = []
    bad_ip_subnets = []
    try:
        if request.method == 'GET':
            query = request.GET.get('select_hosts', None)
            if query == "my_hosts":
                bad_ip_data = fetch_bad_ips()
                for i in bad_ip_data:
                    bad_ips.append(i[0])
                    bad_ip_subnets.append(i[1])
            else:
                bad_ip_data = fetch_bad_ips(False)
                for i in bad_ip_data:
                    bad_ips.append(i[0])
            context = {
                       'bad_ips' : bad_ips,
                       'bad_ip_data' : zip(bad_ips, bad_ip_subnets),
                       'selected' : query,
                      }
            return render(request, 'blacklist/blacklist.html', context)
    except:
        return render(request, 'blacklist/blacklist.html')
