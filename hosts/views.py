from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Host
from .models import Subnet
from vulnerabilities.models import Vulnerability

# Create your views here.

def index(request):
    subnet_list = Subnet.objects.all()
    context = {'subnet_list': subnet_list}
    return render(request, 'hosts/index.html', context)

def detail(request, subnet_id):
    subnet = get_object_or_404(Subnet, pk=subnet_id)
    address = subnet.ipv4_address.rsplit('.', 1)
    host_list = Host.objects.filter(ipv4_address__startswith=address[0])
    context = {'host_list': host_list, 'subnet_id' : subnet_id}
    return render(request, 'hosts/detail.html', context)

def detail_host(request, subnet_id, host_id):
    host = get_object_or_404(Host, pk=host_id)
    vuln_list = Vulnerability.objects.filter(ipv4_address=host.ipv4_address)
    context = {'host': host, 'subnet_id' : subnet_id, 'vuln_list' : vuln_list}
    return render(request, 'hosts/detail_host.html', context)

def search_host(request):
    try:
        if request.method == 'GET':
            query = request.GET.get('input_ip', None).strip()
            # Get corresponding id(s) for queried IP:
            host_id_list = Host.objects.filter(ipv4_address=query).values_list('id', flat=True)
            subnet_id_list = Subnet.objects.filter(ipv4_address=query).values_list('id', flat=True)
            print subnet_id_list
            host_list = []
            # Note, if len(host_list) > 1, then there are duplicate entries in the db.
            # We /should/ only want 1 of these entries, since they'll be exactly the same.
            for i in range(0, len(host_id_list)):
                # Get corresponding Host object(s) for id(s):
                host_list.append(get_object_or_404(Host, pk=host_id_list[i]))
            vuln_list = Vulnerability.objects.filter(ipv4_address=host_list[0].ipv4_address)
            context = {'host': host_list[0] , 'vuln_list' : vuln_list}
            return render(request, 'hosts/detail_host.html', context)
    except:
        ## Inputted IP not found in our db, so load page with no host.
        return render(request, 'hosts/detail_host.html')
