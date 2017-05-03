from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

import sys
import json
import requests

from .models import Account

def index(request):
    context = {}
    return render(request, 'censys/censys.html', context)

# Renders Censys page with info on query.
# Consider refactoring this script. It's gross.
def query_ipv4(request):
    context = {}
    if request.method == 'GET':
        query = request.GET.get('input_censys_query', None).strip()
        if not query:
            return render(request, 'censys/censys.html', context)

        # API Setup
        account_set = Account.objects.get(id=1)
        API_URL = "https://www.censys.io/api/v1"
    	UID = str(account_set.api_key).strip().strip("'")
    	SECRET = str(account_set.secret).strip().strip("'")
        # Search for query on Censys
        search_data = search(query, API_URL, UID, SECRET)
        # Get status (0 == success, 1 == error)
        search_status = search_data.get('status')
        # Get data (ex. ip, open ports, city, state, ...)
        hosts_info = search_data.get('data')

        # Separate info into different lists for ease of maintaining
        # consistency during iteration.
        list_ips = []
        list_protos = []
        list_titles = []
        list_servers = []
        list_provinces = []
        list_cities = []
        list_countries = []
        list_descriptions = []
        list_organizations = []
        list_names = []
        list_oses = []
        list_os_descriptions = []

        # Store data (ip, open ports, etc) into relevant list.
        # If data was not found in JSON, store as 'None.'
        for i in hosts_info:
            try:
                list_ips.append(i[0])
            except:
                list_ips.append(None)
            try:
                list_protos.append(i[1])
            except:
                list_protos.append(None)
            try:
                list_titles.append(i[2])
            except:
                list_titles.append(None)
            try:
                list_servers.append(i[3])
            except:
                list_servers.append(None)
            try:
                list_provinces.append(i[4])
            except:
                list_provinces.append(None)
            try:
                list_cities.append(i[5])
            except:
                list_cities.append(None)
            try:
                list_countries.append(i[6])
            except:
                list_countries.append(None)
            try:
                list_descriptions.append(i[7])
            except:
                list_descriptions.append(None)
            try:
                list_organizations.append(i[8])
            except:
                list_organizations.append(None)
            try:
                list_names.append(i[9])
            except:
                list_names.append(None)
            try:
                list_oses.append(i[10])
            except:
                list_oses.append(None)
            try:
                list_os_descriptions.append(i[11])
            except:
                list_os_descriptions.append(None)

        # Store lists into context using appropriate keys.
        context['ips'] = list_ips
        context['protocols'] = list_protos
        context['titles'] = list_titles
        context['servers'] = list_servers
        context['provinces'] = list_provinces
        context['cities'] = list_cities
        context['countries'] = list_countries
        context['descriptions'] = list_descriptions
        context['organizations'] = list_organizations
        context['names'] = list_names
        context['oses'] = list_oses
        context['os_descriptions'] = list_os_descriptions
        context['zip_data'] = zip(list_ips,
                                  list_protos,
                                  list_titles,
                                  list_servers,
                                  list_provinces,
                                  list_cities,
                                  list_countries,
                                  list_descriptions,
                                  list_organizations,
                                  list_names,
                                  list_oses,
                                  list_os_descriptions)
        context['status'] = search_status
        context['query'] = query
    return render(request, 'censys/censys.html', context)

def search(query, API_URL, UID, SECRET):
    data_per_host = []
    pages = float('inf')
    page = 1

    # Iterate through every page of info (returned as JSON)
    while page <= pages:
        # Parameters to send through API
        params = {'query' : query, 'page' : page}
        res = requests.post(API_URL + "/search/ipv4",
                            json = params,
                            auth=(UID, SECRET))
        # Info returned on query as JSON
        payload = res.json()

        # Iterate through JSON to get desired info
        try:
            for r in payload['results']:
                ip = r["ip"]
                proto = r["protocols"]
                proto = [p.split("/")[0] for p in proto]
                proto.sort(key=float)
                protoList = ','.join(map(str, proto))
                # Only get Web Servers (port 80 is open)
                if '80' in protoList:
                    host_info = view(ip,
                                     protoList,
                                     API_URL,
                                     UID,
                                     SECRET,
                                     data_per_host)
                    data_per_host.append(host_info)
        except:
            # 1 indicates error (most likely reached limit of API queries)
            return {'data' : data_per_host, 'status' : "1"}

        pages = payload['metadata']['pages']
        page += 1
    # 0 indicates success
    return {'data' : data_per_host, 'status' : "0"}

def view(server, protoList, API_URL, UID, SECRET, data_per_host):
    data = []
    data.extend([server, protoList])
    res = requests.get(API_URL + ("/view/ipv4/%s" % server),
                       auth = (UID, SECRET))
    payload = res.json()
    # Get desired information from JSON.
    try:
        if 'title' in payload['80']['http']['get'].keys():
            data.append(payload['80']['http']['get']['title'])
        if 'server' in payload['80']['http']['get']['headers'].keys():
            data.append(payload['80']['http']['get']['headers']['server'])
        if 'province' in payload['location'].keys():
            data.append(payload['location']['province'])
        if 'city' in payload['location'].keys():
            data.append(payload['location']['city'])
        if 'country' in payload['location'].keys():
            data.append(payload['location']['country'])
        if 'description' in payload['autonomous_system'].keys():
            data.append(payload['autonomous_system']['description'])
        if 'organization' in payload['autonomous_system'].keys():
            data.append(payload['autonomous_system']['organization'])
        if 'name' in payload['autonomous_system'].keys():
            data.append(payload['autonomous_system']['name'])
        if 'os' in payload['metadata'].keys():
            data.append(payload['metadata']['os'])
        if 'os_description' in payload['metadata'].keys():
            data.append(payload['metadata']['os_description'])
    except Exception as error:
        print error
    return data
