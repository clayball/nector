from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Vulnerability
from hosts.models import Host
from hosts.models import Subnet

# Create your views here.

def index(request):
    vuln_list = Vulnerability.objects.all()
    host_list = []
    subnet_list = []
    for vuln in vuln_list:
        vuln_ip = vuln.ipv4_address
        host_list.append(Host.objects.get(ipv4_address=vuln_ip))
        subnet_address = vuln_ip.rsplit('.', 1)
        subnet_list.append(Subnet.objects.get(ipv4_address__startswith=subnet_address[0]))

    context = {'vuln_list' : vuln_list, 'host_list' : host_list, 'subnet_list' : subnet_list, 'host_data' : zip(vuln_list, host_list, subnet_list)}
    return render(request, 'vulnerabilities/vulnz.html', context)
