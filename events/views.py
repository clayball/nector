from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Event
from hosts.models import Host
from hosts.models import Subnet

# Create your views here.

def index(request):
    events = Event.objects.all()
    context = {'events' : events}
    return render(request, 'events/events.html', context)
