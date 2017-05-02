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

def query_ipv4(request):
    context = {}
    if request.method == 'GET':
        query = request.GET.get('input_censys_query', None).strip()
        if not query:
            return render(request, 'censys/censys.html', context)
        account_set = Account.objects.get(id=1)
        API_URL = "https://www.censys.io/api/v1"
    	UID = str(account_set.api_key).strip().strip("'")
    	SECRET = str(account_set.secret).strip().strip("'")
        search_data = search(query, API_URL, UID, SECRET)
        search_status = search_data.get('status')
        hosts_info = search_data.get('data')
        list_ips = []
        list_protos = []
        list_titles = []
        list_servers = []
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
        context['ips'] = list_ips
        context['protocols'] = list_protos
        context['titles'] = list_titles
        context['servers'] = list_servers
        context['zip_data'] = zip(list_ips,
                                  list_protos,
                                  list_titles,
                                  list_servers)
        context['status'] = search_status
    return render(request, 'censys/censys.html', context)

def search(query, API_URL, UID, SECRET):
    data_per_host = []
    pages = float('inf')
    page = 1

    while page <= pages:
        params = {'query' : query, 'page' : page}
        res = requests.post(API_URL + "/search/ipv4",
                            json = params,
                            auth=(UID, SECRET))
        payload = res.json()

        try:
            for r in payload['results']:
                ip = r["ip"]
                proto = r["protocols"]
                proto = [p.split("/")[0] for p in proto]
                proto.sort(key=float)
                protoList = ','.join(map(str, proto))
                #print '[+] IP: %s - Protocols: %s' % (ip, protoList)
                if '80' in protoList:
                    host_info = view(ip,
                                     protoList,
                                     API_URL,
                                     UID,
                                     SECRET,
                                     data_per_host)
                    data_per_host.append(host_info)
        except:
            # 1 indicates success
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
    try:
        if 'title' in payload['80']['http']['get'].keys():
            data.append(payload['80']['http']['get']['title'])
            #print "[+] Title: %s" % payload['80']['http']['get']['title']
        if 'server' in payload['80']['http']['get']['headers'].keys():
            data.append(payload['80']['http']['get']['headers']['server'])
            #print "[+] Server: %s" % payload['80']['http']['get']['headers']['server']
    except Exception as error:
        print error
    return data
