from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.template import loader


def index(request):
    return render(request, 'scans/scans.html')
