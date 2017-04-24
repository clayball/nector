from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader


def index(request):
    return render(request, 'nector_home/index.html')

def osint(request):
    return render(request, 'nector_home/osint.html')

def detection(request):
    return render(request, 'nector_home/detection.html')
