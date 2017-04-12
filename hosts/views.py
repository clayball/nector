from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Host
from .models import Subnet

# Create your views here.

def index(request):
    subnet_list = Subnet.objects.all()
    context = {'subnet_list': subnet_list}
    return render(request, 'hosts/index.html', context)

def detail(request, subnet_id):
    subnet = get_object_or_404(Subnet, pk=subnet_id)
    address = subnet.ipv4_address.rsplit('.', 1)
    host_list = Host.objects.filter(ipv4_address__startswith=address[0])
    context = {'host_list': host_list}
    return render(request, 'hosts/detail.html', context)