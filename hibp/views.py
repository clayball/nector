from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

import urllib2, json


# Create your views here.

def index(request):
    context = {}
    return render(request, 'hibp/hibp.html', context)

# Use Have I Been Pwned? (HIBP) API to check if specified account has been preached.
# Consider breaking this up into helper functions.
def check_pwn_account(request):
    if request.method == 'GET':
        query = request.GET.get('input_user', None).strip()
        title = []
        date = []
        description = []
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
        except urllib2.HTTPError as err:
            print "User has no breaches!"

        context = {'account' : user, 'titles' : title, 'dates' : date, 'descriptions' : description}
        return render(request, 'hibp/hibp.html', context)
