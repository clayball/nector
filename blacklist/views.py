from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from hosts.models import Host
import urllib2

def index(request):
    bad_ips = fetch_bad_ips()
    context = {'bad_ips' : bad_ips}
    return render(request, 'blacklist/blacklist.html', context)

# Get malicious IPs from Talos Intelligence
def fetch_bad_ips(only_my_hosts=True):
    bad_ips = []
    # Read in the malicious IPs from Talos
    read_bad_ips = urllib2.urlopen("http://www.talosintelligence.com/feeds/ip-filter.blf").readlines()

    # Was "My Malicious Hosts" selected?
    # TODO: Optimize this. It's very very slow.
    if only_my_hosts:
        for ip in read_bad_ips:
            if ip_exists_in_db(ip):
                bad_ips.append(ip)
    else:
        # We want all the malicious hosts.
        bad_ips = read_bad_ips
    return bad_ips

# If we can filter out a Host with provided ip, then it exists in our DB.
def ip_exists_in_db(ip):
    return Host.objects.filter(ipv4_address=ip).exists()

# Used for filtering out your malicious hosts using dropdown menu.
def limit_hosts(request):
    bad_ips = []
    try:
        if request.method == 'GET':
            query = request.GET.get('select_hosts', None)
            if query == "my_hosts":
                bad_ips = fetch_bad_ips()
            else:
                bad_ips = fetch_bad_ips(False)
            context = {'bad_ips' : bad_ips}
            return render(request, 'blacklist/blacklist.html', context)
    except:
        return render(request, 'blacklist/blacklist.html')
