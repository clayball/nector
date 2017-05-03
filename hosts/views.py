from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Host
from .models import Subnet
from vulnerabilities.models import Vulnerability


def index(request):
    subnet_list = Subnet.objects.all()
    no_mask_list = []
    # Remove the mask for ease of sorting.
    for i in subnet_list:
        no_mask_list.append(str(i).split('/')[0])
    # Sort the IPs.
    sorted_subnet_list = sort_ip_list(no_mask_list)
    sorted_subnet_set = []
    # Get sorted Subnet objects using sorted IPs.
    # (Aka "convert" list to QuerySet)
    for s in sorted_subnet_list:
        sorted_subnet_set.append(Subnet.objects.get(ipv4_address__startswith=s))
    context = {'subnet_list': sorted_subnet_set}
    return render(request, 'hosts/index.html', context)

def detail(request, subnet_id):
    subnet = get_object_or_404(Subnet, pk=subnet_id)
    address = subnet.ipv4_address.rsplit('.', 1)
    host_list = Host.objects.filter(ipv4_address__startswith=address[0])
    context = {'host_list': host_list, 'subnet_id' : subnet_id, 'limit' : 'online'}
    return render(request, 'hosts/detail.html', context)

def detail_host(request, subnet_id, host_id):
    host = get_object_or_404(Host, pk=host_id)
    vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)
    context = {'host': host, 'subnet_id' : subnet_id, 'vuln_list' : vuln_list}
    return render(request, 'hosts/detail_host.html', context)

# Used for sorting hosts by dropdown menu.
def limit_hosts(request, subnet_id):
    try:
        if request.method == 'GET':
            query = request.GET.get('select_hosts', None)
            subnet = get_object_or_404(Subnet, pk=subnet_id)
            address = subnet.ipv4_address.rsplit('.', 1)
            # Get queryset of (probably unordered) hosts.
            host_set = Host.objects.filter(ipv4_address__startswith=address[0])
            unsorted_host_list = get_ip_list(host_set)
            # Generate sorted queryset based on the newly sorted IP addresses.
            sorted_host_list = sort_ip_list(unsorted_host_list)
            sorted_host_set = []
            for h in sorted_host_list:
                sorted_host_set.append(Host.objects.get(ipv4_address=h))
            context = {'host_list': sorted_host_set, 'limit' : query, 'subnet_id' : subnet_id}
            return render(request, 'hosts/detail.html', context)
    except:
        return render(request, 'hosts/detail.html')

# Extract IPv4 addresses from QuerySet of Host objects.
def get_ip_list(queryset):
    unsorted_host_list = []
    for h in queryset:
        ip = str(h).split(',', 1)[0]
        unsorted_host_list.append(ip)
    return unsorted_host_list

# Return sorted list of IP addresses.
def sort_ip_list(unsorted_host_list):
    return sorted(unsorted_host_list, key=lambda ip: long(''.join(["%02X" % long(i) for i in ip.split('.')]), 16))

def search_host(request):
    try:
        if request.method == 'GET':
            query = request.GET.get('input_ip', None).strip()
            context = {}
            if is_ip(query):
                # Get corresponding id(s) for queried IP:
                host_id_list = Host.objects.filter(ipv4_address=query).values_list('id', flat=True)
                host = get_object_or_404(Host, pk=host_id_list[0])
                vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)
                context = {'host': host, 'vuln_list' : vuln_list}
                return render(request, 'hosts/detail_host.html', context)
            elif is_subnet(query):
                # Get corresponding id(s) for queried Subnet:
                ip_no_mask = query.split('/')[0]
                subnet_id_list = Subnet.objects.filter(ipv4_address=ip_no_mask).values_list('id', flat=True)
                subnet_id = subnet_id_list[0]
                subnet = get_object_or_404(Subnet, pk=subnet_id)
                address = subnet.ipv4_address.rsplit('.', 1)
                host_list = Host.objects.filter(ipv4_address__startswith=address[0])
                context = {'host_list': host_list, 'limit' : 'online', 'subnet_id' : subnet_id}
                return render(request, 'hosts/detail.html', context)
            # Assume hostname:
            else:
                # Get corresponding id(s) for queried Hostname:
                host_id_list = Host.objects.filter(host_name__iexact=query).values_list('id', flat=True)
                host_id = host_id_list[0]
                host = get_object_or_404(Host, pk=host_id)
                vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)
                context = {'host': host, 'vuln_list' : vuln_list}
                return render(request, 'hosts/detail_host.html', context)
            return render(request, 'hosts/detail_host.html', context)
    except:
        ## Inputted IP not found in our db, so load page with no host.
        return render(request, 'hosts/detail_host.html')

def is_subnet(query):
    if '/' in query:
        mask_split = query.split('/')
        bits = mask_split[0].split('.')
        if len(bits) != 4: return False
        try: return all(0<=int(p)<256 for p in bits)
        except ValueError: return False
    return False

def is_ip(query):
    pieces = query.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False
