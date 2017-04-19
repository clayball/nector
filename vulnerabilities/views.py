from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Vulnerability

# Create your views here.

def index(request):
    vuln_list = Vulnerability.objects.all()
    context = {'vuln_list': vuln_list}
    return render(request, 'vulnerabilities/vulnz.html', context)
