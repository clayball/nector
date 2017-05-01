from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

import urllib2, json
from HTMLParser import HTMLParser


# Create your views here.

def index(request):
    context = {}
    return render(request, 'hibp/hibp.html', context)

# Use Have I Been Pwned? (HIBP) API to check if specified account has been breached.
def check_pwn_account(request):
    breach_context = check_pwn_breaches(request)
    paste_context = check_pwn_pastes(request)
    breach_context.update(paste_context)
    return render(request, 'hibp/hibp.html', breach_context)

# Consider breaking this up into helper functions.
def check_pwn_breaches(request):
    if request.method == 'GET':
        query = request.GET.get('input_user', None).strip()
        title = []
        date = []
        description = []
        leak = []
        user = str(query)
        url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
        userurl = url + user
        # HIBP uses CloudFlare to check requests and will ban IP based on User-Agent.
        # Spoof our User-Agent so we don't look like a bot:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        try:
            response = opener.open(userurl)
            # Get the HTML of the site:
            html = response.read()
            # Parse the HTML as JSON:
            jsondata = json.loads(html)
            # Manipulate the JSON to get important info:
            for i in jsondata:
                title.append(i['Title'])
                date.append(i['BreachDate'])
                description.append(i['Description'])
                leak.append(i['DataClasses'])
        except urllib2.HTTPError as err:
            pass
        except ValueError as e:
            pass
        context = {'account' : user, 'titles' : title, 'breachdates' : date, 'descriptions' : description, 'leaks' : leak, 'breach_data' : zip(title, date, description, leak)}
        return context

def check_pwn_pastes(request):
    if request.method == 'GET':
        query = request.GET.get('input_user', None).strip()
        source = []
        source_id = []
        date = []
        source_title = []
        user = str(query)
        url = "https://haveibeenpwned.com/api/v2/pasteaccount/"
        userurl = url + user
        # HIBP uses CloudFlare to check requests and will ban IP based on User-Agent.
        # Spoof our User-Agent so we don't look like a bot:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        try:
            response = opener.open(userurl)
            # Get the HTML of the site:
            html = response.read()
            # Parse the HTML as JSON:
            jsondata = json.loads(html)
            # Manipulate the JSON to get important info:
            for i in jsondata:
                source.append(i['Source'])
                source_id.append(i['Id'])
                date.append(i['Date'])
                source_title.append(i['Title'])
        except urllib2.HTTPError as err:
            pass
        except ValueError as e:
            pass
        context = {'sources' : source, 'source_ids' : source_id, 'pastedates' : date, 'source_title' : source_title, 'paste_data' : zip(source, source_id, date, source_title)}
        return context
